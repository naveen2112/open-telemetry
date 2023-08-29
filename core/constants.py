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
]

GOOD = "Good"
MEET_EXPECTATION = "Meet Expectation"
ABOVE_AVERAGE = "Above Average"
AVERAGE = "Average"
POOR = "Poor"
NOT_YET_STARTED = "Not Yet Started"
