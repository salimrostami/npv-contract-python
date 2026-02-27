from source.search.full_search import full_search
from source.definit.project import all_projects, projects
from time import process_time
from source.search.opt_var_search import opt_var_search
from source.search.opt_cvar_search import opt_cvar_search
from source.definit.param import params
from source.search.sens_search_var import tm_sens_rate_var, tm_sens_salary_var
from source.search.sens_search_cvar import tm_sens_rate_cvar, tm_sens_salary_cvar
from source.definit.initialize import initialize
from source.evaluate.simulation import debug_sim_contract
from source.definit.project import Project


def main():
    start_cpu = process_time()

    all_projects()

    if params.isDebug:
        proj: Project = projects[1]
        initialize(proj)
        debug_sim_contract(proj, 1, 1327.0490291091646, 7500, proj.owner_threshold)
        return

    if params.isOptVarSearch:
        for proj in projects:
            opt_var_search(proj)
    if params.isOptCVaRSearch:
        for proj in projects:
            opt_cvar_search(proj)
    if params.isTmSensRateVar:
        tm_sens_rate_var(projects[0])
    if params.isTmSensSalaryVar:
        tm_sens_salary_var(projects[0])
    if params.isTmSensRateCVaR:
        tm_sens_rate_cvar(projects[0])
    if params.isTmSensSalaryCVaR:
        tm_sens_salary_cvar(projects[0])
    if params.isFullSearch:
        full_search(projects[0])

    cpu_elapsed = process_time() - start_cpu
    print(f"CPU time (process): {cpu_elapsed:.3f} s")


if __name__ == "__main__":
    main()
