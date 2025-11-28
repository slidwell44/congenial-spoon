from person_tool.coverage.application import CoverageApplication
from person_tool.employees.application import EmployeeApplication
from person_tool.jobs.application import JobApplication
from person_tool.one_on_ones.application import OneOnOneApplication
from person_tool.skills.application import SkillApplication
from person_tool.system.application import SystemApplication

# ---------------------- system dependencies ----------------------


def provide_system_application() -> SystemApplication:
    return SystemApplication()


# ---------------------- user dependencies ----------------------


def provide_employee_application() -> EmployeeApplication:
    return EmployeeApplication()


# ---------------------- job dependencies ----------------------


def provide_job_application() -> JobApplication:
    return JobApplication()


# ---------------------- skill dependencies ----------------------


def provide_skill_application() -> SkillApplication:
    return SkillApplication()


# ---------------------- 1:1 dependencies ----------------------


def provide_one_on_one_application() -> OneOnOneApplication:
    return OneOnOneApplication()


# ---------------------- coverage dependencies ----------------------


def provide_coverage_application() -> CoverageApplication:
    return CoverageApplication()
