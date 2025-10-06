from source.search.full_search import full_search
from source.definit.project import all_projects
from time import process_time
from source.evaluate.simulation import debug_sim_contract
from source.search.opt_search import opt_search
from source.definit.param import params
from source.search.sens_search import tm_sens_rate, tm_sens_salary


def main():
    start_cpu = process_time()

    all_projects()

    params.isFullSearch and full_search()
    params.isOptSearch and opt_search()
    params.isTmSense and tm_sens_rate()
    params.isTmSense and tm_sens_salary(0.875)
    params.isDebug and debug_sim_contract(
        -5000,
        0,
        8,
        -6000,
        -1000,
    )

    cpu_elapsed = process_time() - start_cpu
    print(f"CPU time (process): {cpu_elapsed:.3f} s")


if __name__ == "__main__":
    main()
