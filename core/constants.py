"""
Module containing constants and configurations for the project.
"""
from datetime import datetime

COPY_RIGHTS_TEXT = (
    f"{datetime.today().year} "
    + "Mallow Technologies Pvt Ltd. | All rights reserved | "
    + "ISO 27001:2013 Certified"
)
COMPANY_NAME = "Mallow Technologies Pvt Ltd."

ENVIRONMENT_DEVELOPMENT = "Development"
ENVIRONMENT_PRODUCTION = "Production"
ENVIRONMENT_TESTING = "Testing"

PRESENT_TYPE_REMOTE = "Remote"
PRESENT_TYPE_IN_PERSON = "In-Person"
PRESENT_TYPES = [
    (PRESENT_TYPE_REMOTE, PRESENT_TYPE_REMOTE),
    (PRESENT_TYPE_IN_PERSON, PRESENT_TYPE_IN_PERSON),
]

TASK_TYPE_TASK = "Task"
TASK_TYPE_ASSESSMENT = "Assessment"
TASK_TYPE_CULTURAL_MEET = "Cultural Meet"
TASK_TYPES = [
    (TASK_TYPE_TASK, TASK_TYPE_TASK),
    (TASK_TYPE_ASSESSMENT, TASK_TYPE_ASSESSMENT),
    (TASK_TYPE_CULTURAL_MEET, TASK_TYPE_CULTURAL_MEET),
]

ADMIN_EMAILS = [
    "saranya.sivanandham@mallow-tech.com",
    "yogesh@mallow-tech.com",
    "poovarasu@mallow-tech.com",
    "kumaresan@mallow-tech.com",
    "satheesh@mallow-tech.com",
    "anandraj@mallow-tech.com",
    "sanjay@mallow-tech.com",
    "palaniyappan@mallow-tech.com",
    "afsal@mallow-tech.com",
    "poonkawin@mallow-tech.com",
]

PROBATIONER_EMAILS = [
    "ajit.thenraj@mallow-tech.com",
]

GOOD = "Good"
MEET_EXPECTATION = "Meet Expectation"
ABOVE_AVERAGE = "Above Average"
AVERAGE = "Average"
POOR = "Poor"
NOT_YET_STARTED = "Not Yet Started"

USER_STATUS_INTERN = "intern"
USER_STATUS_PROJECT_INTERN = "project_intern"
USER_STATUS_PROBATIONER = "probationer"
USER_STATUS_WORKING = "working"
USER_STATUS_NOTICE_PERIOD = "in-notice-period"
USER_STATUS_RELIEVED = "relieved"

BATCH_DURATION_IN_MONTHS = 5

TEST_CREATE = "Test Create"
TEST_EDIT = "Test Edit"

RETEST_CREATE = "Retest Create"
RETEST_EDIT = "Retest Edit"

INFINITE_TEST_CREATE = "Infinite Test Create"
INFINITE_TEST_EDIT = "Infinite Test Edit"
INFINITE_RETEST_CREATE = "Infinite Retest Create"
INFINITE_RETEST_EDIT = "Infinite Retest Edit"

TEST_COMPLETED = "Test Completed"

NO_START_DATE = datetime(1, 1, 1, 1, 0, 0)
NO_END_DATE = datetime(1, 1, 1, 1, 0, 0)

REQUIRED = ["Score", "Comment"]
