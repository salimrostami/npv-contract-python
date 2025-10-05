from source.definit.project import projects, Project
from source.definit.contract import contracts, Contract, make_contracts
from source.evaluate.simulation import simulate
from source.utility.report_writer import full_report, full_header
from source.definit.initialize import initialize
from source.evaluate.exact_eval import exact_calculations
from source.definit.param import params


def update_min_max_total_VaR(proj: Project):
    total_var = proj.exact_results.builder.var + proj.exact_results.owner.var
    proj.min_total_VaR = max(total_var, proj.min_total_VaR)
    proj.max_total_VaR = min(total_var, proj.max_total_VaR)


def full_search():
    proj: Project
    cont: Contract
    for proj in projects:
        log_file = full_header(proj)
        make_contracts(proj, proj.builder_target_enpv)
        initialize(proj)
        for cont in contracts:
            params.isSim and simulate(proj, cont, 0)
            exact_calculations(proj, cont, 0)
            update_min_max_total_VaR(proj)
            full_report(log_file, cont, proj)
        print(
            f"Min Total VaR: {proj.min_total_VaR}, Max Total VaR: {proj.max_total_VaR}\n"
        )
