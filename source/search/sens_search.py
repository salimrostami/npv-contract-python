from source.definit.project import Project
from source.search.sens_search_var import tm_sens_rate_var, tm_sens_salary_var
from source.search.sens_search_cvar import tm_sens_rate_cvar, tm_sens_salary_cvar


def tm_sens_rate(proj: Project):
    # Backward compatible alias.
    tm_sens_rate_var(proj)


def tm_sens_salary(proj: Project):
    # Backward compatible alias.
    tm_sens_salary_var(proj)

