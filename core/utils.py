"""
Module contains the custom configuration for the Django ajax datatable
"""
import datetime

from ajax_datatable import AjaxDatatableView  # pylint: disable=no-name-in-module
from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponseForbidden

from hubble.models import (
    InternDetail,
    SubBatchTaskTimeline,
    TimelineTask,
    TraineeHoliday,
)


class CustomDatatable(AjaxDatatableView):  # pragma: no cover
    """
    This class provides the feature of sending a list of dictionaries
    as input to the datatable
    """

    show_column_filters = False

    # It is used to ommit 'arguments-differ'.In this case, the
    # `get_table_row_id` method in the `CustomDatatable` class has a different
    # signature than the method it is overriding from the
    # pylint: disable=arguments-differ
    def get_table_row_id(self, request, obj, i):  # pylint: disable=unused-argument
        """
        Provides a specific ID for the table row; default: "row-ID"
        Override to customize as required.

        Do to a limitation of datatables.net, we can only supply to table rows
        a id="row-ID" attribute, and not a data-row-id="ID" attribute
        """
        result = ""
        if self.table_row_id_fieldname:
            if isinstance(obj, dict):
                try:
                    result = self.table_row_id_prefix + str(i + 1)
                except AttributeError:
                    result = ""
            else:
                try:
                    result = self.table_row_id_prefix + str(
                        getattr(obj, self.table_row_id_fieldname)
                    )
                except AttributeError:
                    result = ""
        return result

    def render_dict_column(self, row, column):
        """This function is responsible for assigning values to the respective
        columns in a row"""
        return row.get(column, None)

    def prepare_results(self, request, qs):
        """This function is responsible for preparing the json data which
        should be returned as response when the datatable is called
        """
        json_data = []
        columns = [c["name"] for c in self.column_specs]
        if len(qs) > 0 and isinstance(qs[0], dict):
            func = getattr(self, "render_dict_column")
        else:
            func = getattr(self, "render_column")
        for i, cur_object in enumerate(qs):
            retdict = {
                # fieldname: '<div class="field-%s">%s</div>'
                # % (fieldname, self.render_column(cur_object, fieldname))
                fieldname: func(cur_object, fieldname)
                for fieldname in columns
                if fieldname
            }

            self.customize_row(retdict, cur_object)
            self.clip_results(retdict)

            row_id = self.get_table_row_id(request, cur_object, i)

            if row_id:
                # "Automatic addition of row ID attributes"
                # https://datatables.net/examples/server_side/ids.html
                retdict["DT_RowId"] = row_id

            json_data.append(retdict)
        return json_data


class ValidateAuthorizationMixin(AccessMixin):
    """Mixin that validates user authorization"""

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatches the request to the view function
        """
        if not request.user.is_admin_user:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


def validate_authorization():  # pragma: no cover
    """
    Decorator function that validates user authorization
    """

    def decorator(view_func):
        """
        Decorator function that wraps the view function
        """

        def wrapped_view(request, *args, **kwargs):
            """
            Wrapped view function that performs authorization validation
            """
            if request.user.is_admin_user:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden()

        return wrapped_view

    return decorator


def update_expected_end_date_of_intern_details(sub_batch):
    """
    Updates the expected completion date of intern details based on the
    latest sub-batch task timeline
    """
    expected_completion_day = (
        SubBatchTaskTimeline.objects.filter(sub_batch_id=sub_batch).order_by("-order").first()
    )
    InternDetail.objects.filter(sub_batch_id=sub_batch).update(
        expected_completion=expected_completion_day.end_date
    )


def is_leave_day(holidays, start_date):
    """
    Checks if a given date is a leave day (holiday or Sunday)
    """
    return (start_date.date() in holidays) or (start_date.date().weekday() == 6)


def calculate_duration_for_task(holidays, start_date, is_half_day, number_of_days):
    """
    Calculates the start and end date/time for a task, taking into
    account holidays, half-day status, and the number of days
    """
    if start_date.time() == datetime.time(hour=18, minute=0):
        start_date += datetime.timedelta(1)
        start_date = start_date.replace(hour=9, minute=0)

    while is_leave_day(holidays, start_date):
        start_date += datetime.timedelta(1)

    if is_half_day:
        start_date_time = datetime.datetime.combine(start_date, datetime.time(hour=14, minute=0))
    else:
        start_date_time = datetime.datetime.combine(start_date, datetime.time(hour=9, minute=0))

    having_half_day_at_end = False
    end_time = datetime.time(hour=18, minute=0)

    if (not is_half_day and (number_of_days % 1 == 0.5)) or (
        is_half_day and (number_of_days % 1 != 0.5)
    ):
        having_half_day_at_end = True
        end_time = datetime.time(hour=13, minute=0)

    total_num_days = 0
    if is_half_day:
        total_num_days += 0.5
        end_date = start_date
        start_date += datetime.timedelta(1)

    while total_num_days != number_of_days:
        if is_leave_day(holidays, start_date):
            start_date += datetime.timedelta(1)
            continue

        if number_of_days - total_num_days == 0.5:
            total_num_days += 0.5
            end_date = start_date
            continue

        total_num_days += 1
        end_date = start_date
        start_date += datetime.timedelta(1)
    return {
        "start_date_time": start_date_time,
        "end_date_time": datetime.datetime.combine(end_date, end_time),
        "ends_afternoon": having_half_day_at_end,
    }


def schedule_timeline_for_sub_batch(sub_batch, user=None, is_create=True):
    """
    Schedules the timeline for a sub-batch based on the holiday of the batch
    """
    holidays = list(
        TraineeHoliday.objects.filter(batch_id=sub_batch.batch.id).values_list(
            "date_of_holiday", flat=True
        )
    )
    start_date = datetime.datetime.strptime(str(sub_batch.start_date), "%Y-%m-%d")
    is_half_day = False
    order = 0
    if is_create:
        for task in TimelineTask.objects.filter(timeline=sub_batch.timeline.id):
            values = calculate_duration_for_task(holidays, start_date, is_half_day, task.days)

            order += 1
            SubBatchTaskTimeline.objects.create(
                name=task.name,
                days=task.days,
                sub_batch=sub_batch,
                present_type=task.present_type,
                task_type=task.task_type,
                start_date=values["start_date_time"],
                end_date=values["end_date_time"],
                created_by=user,
                order=order,
            )
            start_date = values["end_date_time"]
            is_half_day = values["ends_afternoon"]
        value_end_date = values["end_date_time"]

    else:
        for task in SubBatchTaskTimeline.objects.filter(sub_batch=sub_batch).order_by("order"):
            values = calculate_duration_for_task(holidays, start_date, is_half_day, task.days)
            start_date = values["end_date_time"]
            is_half_day = values["ends_afternoon"]
            task.start_date = values["start_date_time"]
            task.end_date = values["end_date_time"]
            task.save()
        value_end_date = values["end_date_time"]
    update_expected_end_date_of_intern_details(sub_batch.id)
    return value_end_date
