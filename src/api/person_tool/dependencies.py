from person_tool.jobs.application import JobApplication
from person_tool.system.application import SystemApplication
from person_tool.users.application import UserApplication

# ---------------------- system dependencies ----------------------


def provide_system_application() -> SystemApplication:
    return SystemApplication()


# ---------------------- user dependencies ----------------------


def provide_user_application() -> UserApplication:
    return UserApplication()


# ---------------------- job dependencies ----------------------


def provide_job_application() -> JobApplication:
    return JobApplication()
