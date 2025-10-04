from contract import Contract, calc_reward, calc_salary
from full_search import exact_calculations, full_search
from initialize import initialize
from opt_search import opt_contract_peakfinder, opt_search
from project import all_projects, projects, Project
import time
import numpy as np
from simulation import simulate

distribution = "uni"
simulationRounds = 100000
isSim = False
isFullSearch = False
isOptSearch = True
E_percision = 0.000001
min_safe_salary = 12


def tm_sensitivity():
    proj: Project
    for proj in projects:
        initialize(proj, distribution)
        cont = Contract(
            "tm-sense",
            0,
            0,
            0,
            "tm-sense",
        )
        print(
            "nu",
            "Salary",
            "Reward",
            "TVaR",
            sep="\t",
        )
        for nu in np.arange(0.0, 1.009, 0.01):
            cont.reimburse_rate = round(nu, 4)
            Smax = round(
                calc_salary(
                    proj, proj.builder_target_enpv, cont.reimburse_rate, 0, distribution
                ),
                4,
            )
            Smin = min(0.01 * Smax, min_safe_salary)
            best_salary, best_tvar = opt_contract_peakfinder(
                proj,
                cont,
                distribution,
                "lh",
                Smin,
                Smax,
                E_percision,
            )
            best_R = round(
                calc_reward(
                    proj,
                    proj.builder_target_enpv,
                    cont.reimburse_rate,
                    best_salary,
                    distribution,
                ),
                6,
            )
            print(
                f"{cont.reimburse_rate}",
                f"{best_salary}",
                f"{best_R}",
                f"{best_tvar}",
                sep="\t",
            )


def simulate_contract(
    cbar: float, nu: float, salary: float, bthresh: float, othresh: float
):
    proj = Project("sim-temp", cbar, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000)
    cont = Contract("sim-temp", 0, 0, 0, "tm-sense")
    cont.reimburse_rate = nu
    cont.salary = salary
    cont.reward = round(
        calc_reward(
            proj,
            proj.builder_target_enpv,
            cont.reimburse_rate,
            cont.salary,
            distribution,
        ),
        6,
    )
    initialize(proj, distribution)
    proj.owner_threshold = othresh
    simulate(proj, cont, simulationRounds, distribution, bthresh)
    # Fixed-width table output for aligned columns
    hdr_fmt = "{:<16}{:<16}{:<16}{:<16}{:<16}"
    num_fmt = "{:>16.6f}{:>16.6f}{:>16.6f}{:>16.6f}{:>16.6f}"
    print(
        hdr_fmt.format(
            "Builder enpv", "Owner enpv", "Builder risk", "Owner risk", "total VaR"
        )
    )
    print(
        num_fmt.format(
            float(proj.sim_results.builder.enpv),
            float(proj.sim_results.owner.enpv),
            float(proj.sim_results.builder.risk),
            float(proj.sim_results.owner.risk),
            float(proj.sim_results.builder.var + proj.sim_results.owner.var),
        )
    )
    exact_calculations(proj, cont, distribution, bthresh)
    print(
        num_fmt.format(
            float(proj.exact_results.builder.enpv),
            float(proj.exact_results.owner.enpv),
            float(proj.exact_results.builder.risk),
            float(proj.exact_results.owner.risk),
            float(proj.exact_results.builder.var + proj.exact_results.owner.var),
        )
    )


def main():
    start_cpu = time.process_time()

    all_projects()
    isFullSearch and full_search(distribution, isSim, simulationRounds)
    isOptSearch and opt_search(distribution, E_percision)

    tm_sensitivity()

    # simulate_contract(-5000, 0, 8, -6000, -1000)
    # previously 1364.2596592179357 # -19704.0699394 7.527561328125 9394

    cpu_elapsed = time.process_time() - start_cpu
    print(f"CPU time (process): {cpu_elapsed:.3f} s")


if __name__ == "__main__":
    main()
