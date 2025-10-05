from source.search.full_search import full_search
from source.definit.project import all_projects
from time import process_time
from source.evaluate.simulation import debug_simulate_contract
from source.search.opt_search import opt_search, tm_sensitivity

distribution = "uni"
simulationRounds = 100000
isSim = False
isFullSearch = False
isOptSearch = True
isDebug = False
E_percision = 0.000001
min_safe_salary = 12


def main():
    start_cpu = process_time()

    all_projects()
    isFullSearch and full_search(distribution, isSim, simulationRounds)
    isOptSearch and opt_search(distribution, E_percision)

    tm_sensitivity(distribution, E_percision)

    isDebug and debug_simulate_contract(
        -5000, 0, 8, -6000, -1000, distribution, simulationRounds
    )
    # previously 1364.2596592179357 # -19704.0699394 7.527561328125 9394

    cpu_elapsed = process_time() - start_cpu
    print(f"CPU time (process): {cpu_elapsed:.3f} s")


if __name__ == "__main__":
    main()
