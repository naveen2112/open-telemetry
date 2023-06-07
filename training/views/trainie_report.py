from collections import defaultdict
from django.forms import model_to_dict
from django.shortcuts import render, get_object_or_404
from hubble.models import Task_Timeline, User, SubBatch, Assessment, WeekExtension
from training.forms import AddReportForm
from django.http import JsonResponse
from django.db.models import Count, Q, Subquery, OuterRef

def user_profile(request, sub_batch, pk):

    latest_entries = Assessment.objects.filter(task = OuterRef('id')).order_by('-id')[:1]
    check = Task_Timeline.objects.filter(sub_batch = sub_batch, task_type = "Assessment").annotate(retries = Count('assessments__is_retry') - 1, last_entry = Subquery(latest_entries.values('score')), comment = Subquery(latest_entries.values('comment')), is_retry = Subquery(latest_entries.values('is_retry'))).values( 'id', 'last_entry', 'retries', 'comment', 'name', 'is_retry')

    extension_weeks = WeekExtension.objects.filter(sub_batch__id = sub_batch, user__id = pk)
    user = User.objects.get(id=pk)

    latest_records = []
    retry_counts = dict()
    task_lists = []
    all_reports = defaultdict(list)
    tasks = Task_Timeline.objects.filter(task_type = "Assessment")

    for task in tasks:
        latest_record = Assessment.objects.filter(task = task.id).last()
        count = Assessment.objects.filter(task=task.id).aggregate(retry=Count('is_retry', filter=Q(is_retry=True)))
        retry_counts[task.id] = count['retry']
        if latest_record:
            latest_records.append(latest_record)

    context = {
        "tasks": tasks,
        "user": user,
        "form": AddReportForm(),
        "sub_batch_id": sub_batch,
        "assessments": check,
        "retry_counts": retry_counts,
        "extension_weeks": extension_weeks,
    }
    return render(request, "batch/user_report.html", context)


def create_user_report(request, pk):
    """
    Create User report
    """
    if request.method == "POST":
        form = AddReportForm(request.POST)
        print(request.POST.get('status'))
        if form.is_valid():  # Check if form is valid or not
            report = form.save(commit=False)
            report.task = Task_Timeline.objects.get(id = request.POST.get('task'))
            report.sub_batch = SubBatch.objects.get(id = request.POST.get("sub_batch"))
            report.user = User.objects.get(id = pk)
            report.is_retry = True if request.POST.get('status') == 'true' else False
            report.created_by = request.user
            report.save()
            return JsonResponse({"status": "success"})
        else:
            field_errors = form.errors.as_json()
            non_field_errors = form.non_field_errors().as_json()
            return JsonResponse(
                {
                    "status": "error",
                    "field_errors": field_errors,
                    "non_field_errors": non_field_errors,
                }
            )
        

def add_extension(request, pk, sub_batch):
    extension = WeekExtension.objects.create(
        sub_batch = SubBatch.objects.get(id=sub_batch),
        user = User.objects.get(id=pk),
        created_by = request.user,
    )
    return JsonResponse({"status": "success"})


def delete_extension(request, pk):
    """
    Delete Timeline Template
    Soft delete the template and record the deletion time in deleted_at field
    """
    try:
        extension = get_object_or_404(WeekExtension, id=pk)
        extension.delete()
        return JsonResponse({"message": "Week extension deleted succcessfully", "status": "success"})
    except Exception as e:
        return JsonResponse({"message": "Error while deleting week extension!"}, status=500)