from source.definit.project import Project
from source.definit.contract import calc_reward, calc_salary, contracts, Contract
from source.evaluate.simulation import simulate
from source.utility.report_writer import full_report, full_header
from source.definit.initialize import initialize
from source.evaluate.exact_eval import exact_calculations
from source.definit.param import params
import numpy as np


def full_contracts(proj: Project, target_b_enpv):
    contracts.clear()
    counter = 0
    for nu in np.arange(0, 1.009, 0.01):
        Rmax = calc_reward(proj, target_b_enpv, nu, 0)
        Smax = calc_salary(proj, target_b_enpv, nu, 0)
        for s in np.arange(0, 1.009, 0.01):
            try:
                contracts.append(
                    Contract(
                        f"{(counter+1):03}",
                        Rmax * (1 - s),
                        nu,
                        Smax * s,
                        f"{round(nu, 2)}-{round(s, 2)}",
                    )
                )
                counter += 1
            except ValueError as e:
                print(e)


def update_min_max_total_VaR(proj: Project):
    total_var = proj.exact_results.builder.var + proj.exact_results.owner.var
    proj.min_total_VaR = max(total_var, proj.min_total_VaR)
    proj.max_total_VaR = min(total_var, proj.max_total_VaR)


def full_search(proj: Project):
    cont: Contract
    log_file = full_header(proj)
    full_contracts(proj, proj.b_t_enpv)
    initialize(proj)
    for cont in contracts:
        params.isSim and simulate(proj, cont, proj.sim_results, 0)
        exact_calculations(
            proj,
            cont,
            proj.exact_results.builder,
            proj.exact_results.owner,
            0,
            calc_cvar=True,
        )
        update_min_max_total_VaR(proj)
        full_report(proj, cont, log_file)
    print(f"Min Total VaR: {proj.min_total_VaR}, Max Total VaR: {proj.max_total_VaR}\n")
