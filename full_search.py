from project import projects, Project
from contract import contracts, Contract, make_contracts
from simulation import simulate
from report_writer import full_report, full_header
from builder_risk import builder_risk
from builder_enpv import builder_enpv
from owner_risk import owner_risk
from owner_enpv import owner_enpv
from initialize import set_owner_threshold
from builder_var import builder_var
from owner_var import owner_var


def exact_calculations(
    proj: Project, cont: Contract, distribution: str, builder_threshold_u: int
):
    proj.exact_results.builder.enpv = round(builder_enpv(proj, cont, distribution), 6)
    proj.exact_results.owner.enpv = round(owner_enpv(proj, cont, distribution), 6)
    proj.exact_results.builder.risk = round(
        100 * builder_risk(proj, cont, distribution, builder_threshold_u), 6
    )
    proj.exact_results.owner.risk = round(
        100 * owner_risk(proj, cont, distribution, proj.owner_threshold), 6
    )
    proj.exact_results.builder.var = round(
        builder_var(proj, cont, distribution, 0.05) - proj.exact_results.builder.enpv, 6
    )
    proj.exact_results.owner.var = round(
        owner_var(proj, cont, distribution, 0.05) - proj.exact_results.owner.enpv, 6
    )


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
        set_owner_threshold(proj, distribution)
        for cont in contracts:
            simulation and simulate(proj, cont, num_simulations, distribution, 0)
            exact_calculations(proj, cont, distribution, 0)
            update_min_max_total_VaR(proj)
            full_report(log_file, cont, proj, simulation)
        print(
            f"Min Total VaR: {proj.min_total_VaR}, Max Total VaR: {proj.max_total_VaR}\n"
        )
