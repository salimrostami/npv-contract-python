from source.search.full_search import full_search
from source.definit.project import all_projects, projects
from time import process_time
from source.search.opt_search import opt_search
from source.definit.param import params
from source.search.sens_search import tm_sens_rate, tm_sens_salary

from source.definit.initialize import initialize
from source.evaluate.simulation import debug_sim_contract
from source.definit.project import Project


def main():
    start_cpu = process_time()

    all_projects()

    if params.isDebug:
        proj: Project
        proj = projects[0]
        initialize(proj)
        debug_sim_contract(proj, 0.4318, 0, 0, proj.owner_threshold)
        return

    if params.isOptSearch:
        for proj in projects:
            opt_search(proj)
    params.isTmSense and tm_sens_rate(projects[0])
    params.isTmSense and tm_sens_salary(projects[0])
    params.isFullSearch and full_search(projects[0])

    cpu_elapsed = process_time() - start_cpu
    print(f"CPU time (process): {cpu_elapsed:.3f} s")


if __name__ == "__main__":
    main()
