from source.definit.project import projects, Project
from source.definit.contract import contracts, Contract, make_contracts
from source.evaluate.simulation import simulate
from source.utility.report_writer import full_report, full_header
from source.definit.initialize import initialize
from source.evaluate.exact_eval import exact_calculations


def update_min_max_total_VaR(proj: Project):
    total_var = round(proj.exact_results.builder.var + proj.exact_results.owner.var, 6)
    proj.min_total_VaR = max(total_var, proj.min_total_VaR)
    proj.max_total_VaR = min(total_var, proj.max_total_VaR)


def full_search(
    distribution: str,
    simulation: bool,
    num_simulations: int,
):
    proj: Project
    cont: Contract
    for proj in projects:
        log_file = full_header(proj, simulation)
        make_contracts(proj, proj.builder_target_enpv, distribution)
        initialize(proj, distribution)
        for cont in contracts:
            simulation and simulate(proj, cont, num_simulations, distribution, 0)
            exact_calculations(proj, cont, distribution, 0)
            update_min_max_total_VaR(proj)
            full_report(log_file, cont, proj, simulation)
        print(
            f"Min Total VaR: {proj.min_total_VaR}, Max Total VaR: {proj.max_total_VaR}\n"
        )
