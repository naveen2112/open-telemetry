"""
Module responsible for determining the scenario for assessment status
"""
from . import constants


def zeroth_assessment_entry(
    current_week_end_date,
    current_week_start_date,
    last_assessment_with_absent_record,
    current_task,
    user,
):
    """
    This function handles the scenario where the trainee has yet to take an assessment
    """
    count_of_task = len(
        [
            assessments_with_absent_record
            for assessments_with_absent_record in current_task["assessments"]
            if assessments_with_absent_record["user_id"] == user
        ]
    )
    if current_week_end_date is not constants.NO_END_DATE:
        if count_of_task and (
            current_week_start_date
            <= last_assessment_with_absent_record["updated_at"]
            <= current_week_end_date
        ):
            response = constants.TEST_EDIT
        else:
            response = constants.TEST_CREATE
    elif count_of_task:
        response = constants.INFINITE_TEST_EDIT
    else:
        response = constants.INFINITE_TEST_CREATE
    return response


# pylint: disable=too-many-branches
def first_assessment_entry(
    current_week_end_date,
    current_week_start_date,
    last_assessment_with_absent_record,
    last_assessment_record,
):
    """
    This function handles the scenario where the trainee has take single assessment
    """
    if current_week_end_date != constants.NO_END_DATE:
        if (
            current_week_start_date
            <= last_assessment_with_absent_record["updated_at"]
            <= current_week_end_date
        ):
            if not last_assessment_with_absent_record["is_retry"]:
                response = constants.TEST_EDIT
            else:
                response = constants.RETEST_EDIT
        elif last_assessment_record["is_retry_needed"]:
            response = constants.RETEST_CREATE
        else:
            response = constants.TEST_COMPLETED
    elif last_assessment_record["is_retry_needed"]:
        if last_assessment_with_absent_record["is_retry"]:
            response = constants.INFINITE_RETEST_EDIT
        else:
            response = constants.INFINITE_RETEST_CREATE
    elif (
        last_assessment_record["present_status"] and not last_assessment_record["is_retry_needed"]
    ):
        if last_assessment_record["updated_at"] < current_week_start_date:
            response = constants.TEST_COMPLETED
        else:
            response = constants.TEST_EDIT
    return response


def second_assessment_entry(
    current_week_end_date,
    current_week_start_date,
    last_assessment_with_absent_record,
    last_assessment_record,
):
    """
    This function handles the scenario where the trainee
    has completed all his chances for an assessment
    """
    if current_week_end_date != constants.NO_END_DATE:
        if (
            current_week_start_date
            <= last_assessment_with_absent_record["updated_at"]
            <= current_week_end_date
        ):
            response = constants.RETEST_EDIT
        else:
            response = constants.TEST_COMPLETED
    elif (
        not last_assessment_with_absent_record["present_status"]
        and last_assessment_with_absent_record["is_retry"]
    ):
        response = constants.INFINITE_RETEST_EDIT
    elif last_assessment_record["present_status"]:
        if (
            last_assessment_record["is_retry"]
            and last_assessment_record["updated_at"] > current_week_start_date
        ):
            response = constants.INFINITE_RETEST_EDIT
        else:
            response = constants.TEST_COMPLETED
    return response
