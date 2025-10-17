from source.definit.initialize import initialize
from source.search.full_search import full_search
from source.definit.project import Project, all_projects, projects
from time import process_time
from source.search.opt_search import opt_search
from source.definit.param import params
from source.search.sens_search import tm_sens_rate, tm_sens_salary

# from source.evaluate.simulation import debug_sim_contract


def main():
    start_cpu = process_time()

    all_projects()

    proj: Project

    # proj = projects[6]
    # proj.owner_income = 25000
    # initialize(proj)
    # debug_sim_contract(proj, 1, 0, 0, 0)
    # # -1093.4622544903086 # 859.8066182645362 # -7500
    # return

    for proj in projects:
        initialize(proj)
        opt_search(proj)

    params.isTmSense and tm_sens_rate(projects[0])
    proj = projects[0]
    if proj.tmOpt.contract is not None:
        nu = proj.tmOpt.contract.reimburse_rate
        params.isTmSense and tm_sens_salary(projects[0], nu)
    params.isFullSearch and full_search(projects[0])

    cpu_elapsed = process_time() - start_cpu
    print(f"CPU time (process): {cpu_elapsed:.3f} s")


if __name__ == "__main__":
    main()
