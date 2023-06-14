import datetime

from ajax_datatable import AjaxDatatableView
from django.http import HttpResponseForbidden


class CustomDatatable(AjaxDatatableView):
    """This class provides the feature of sending a list of dictionaries as input to the datatable"""

    show_column_filters = False

    def get_table_row_id(self, request, obj, i):
        """
        Provides a specific ID for the table row; default: "row-ID"
        Override to customize as required.

        Do to a limitation of datatables.net, we can only supply to table rows
        a id="row-ID" attribute, and not a data-row-id="ID" attribute
        """
        result = ""
        if self.table_row_id_fieldname:
            if type(obj) == dict:
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
        """This function is responsible for assigning values to the respective columns in a row"""
        return row.get(column, None)

    def prepare_results(self, request, qs):
        """This function is responsible for preparing the json data which should be returned as response when the datatable is called"""
        json_data = []
        columns = [c["name"] for c in self.column_specs]
        if len(qs) > 0 and type(qs[0]) is dict:
            func = getattr(self, "render_dict_column")
        else:
            func = getattr(self, "render_column")
        for i, cur_object in enumerate(qs):
            retdict = {
                # fieldname: '<div class="field-%s">%s</div>' % (fieldname, self.render_column(cur_object, fieldname))
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


def calculate_duration(holidays, start_date, duration, number_of_days):
    start_time = datetime.time(hour=9, minute=0)  # Day start time
    end_time = datetime.time(hour=18, minute=0)  # Day end time
    break_time = datetime.time(hour=13, minute=0)  # Day break time
    break_end_time = datetime.time(hour=14, minute=0)  # Day break end time\

    task_start_date = None
    task_end_date = None
    while duration != datetime.timedelta(0):
        temp_duration = datetime.timedelta(hours=4)
        end_datetime = datetime.datetime.combine(start_date, start_time) + temp_duration
        start_datetime = datetime.datetime.combine(start_date, start_time)

        # While the end date falls on a Sunday or holiday then it will increament the date 1
        while (end_datetime.date().weekday() == 6) or end_datetime.date() in holidays:
            end_datetime += datetime.timedelta(days=1)

        total_start_hours = (duration.days * 24) + (
            duration.seconds / 3600
        )  # Calculating the hours required to complete the task

        # Check if total hours and hours required are the same
        if total_start_hours == number_of_days * 8:
            # While the end date falls on a Sunday or holiday then it will increament the date 1
            while (
                start_datetime.date().weekday() == 6
            ) or start_datetime.date() in holidays:  # need to check
                start_datetime += datetime.timedelta(days=1)
            task_start_date = start_datetime.date()

        duration = duration - temp_duration
        total_hours = (duration.days * 24) + (
            duration.seconds / 3600
        )  # Calculating the remaining hours
        if total_hours == 0:
            task_end_date = end_datetime.date()

        # Check if the end_datetime.time() is equal to day end time
        if end_datetime.time() == end_time:
            end_datetime += datetime.timedelta(days=1)

        start_date = end_datetime
        start_time = end_datetime.time()

        # Check the end_datetime.time() is equal to break time
        # Exclide the 1hr breaktime
        if end_datetime.time() == break_time:
            start_time = break_end_time

        if end_datetime.time() == end_time:
            start_time = datetime.time(hour=9, minute=0)

    return [task_start_date, task_end_date, start_date, start_time]


def admin_user(request):
    return request.id != 16 #Condition needs to be changed


def validate_authorization(test_func):
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden()

        return wrapped_view

    return decorator
