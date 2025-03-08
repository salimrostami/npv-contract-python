from project import projects, Project
from contract import contracts, Contract, make_contracts
from simulation import simulate
from report_writer import print_reports, print_header
from builder_risk import builder_risk
from builder_enpv import builder_enpv
from owner_risk import owner_risk
from owner_enpv import owner_enpv
from initialize import set_owner_threshold
from builder_var import builder_var
from owner_var import owner_var

num_simulations = 1000
distribution = "uni"
simulation = True

try:
    projects.append(Project("001", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000))
except ValueError as e:
    print(e)


def exact_calculations(
    proj: Project, cont: Contract, distribution: str, builder_threshold_u: int
):
    proj.exact_results.builder.enpv = round(builder_enpv(proj, cont, distribution), 2)
    proj.exact_results.owner.enpv = round(owner_enpv(proj, cont, distribution), 2)
    proj.exact_results.builder.risk = round(
        100 * builder_risk(proj, cont, distribution, builder_threshold_u), 2
    )
    proj.exact_results.owner.risk = round(
        100 * owner_risk(proj, cont, distribution, proj.owner_threshold), 2
    )
    proj.exact_results.builder.var = round(
        builder_var(proj, cont, distribution, 0.05) - proj.exact_results.builder.enpv, 2
    )
    proj.exact_results.owner.var = round(
        owner_var(proj, cont, distribution, 0.05) - proj.exact_results.owner.enpv, 2
    )


def update_min_max_total_VaR(proj: Project):
    total_var = round(proj.exact_results.builder.var + proj.exact_results.owner.var, 0)
    if total_var > proj.min_total_VaR:
        proj.min_total_VaR = total_var
    if total_var < proj.max_total_VaR:
        proj.max_total_VaR = total_var


def main():
    proj: Project
    cont: Contract
    print_header(simulation)
    for proj in projects:
        make_contracts(proj, proj.builder_target_enpv, distribution)
        set_owner_threshold(proj, distribution)
        for cont in contracts:
            simulation and simulate(proj, cont, num_simulations, distribution, 0)
            exact_calculations(proj, cont, distribution, 0)
            update_min_max_total_VaR(proj)
            print_reports(cont, proj, simulation)
        print(
            f"Min Total VaR: {proj.min_total_VaR}, Max Total VaR: {proj.max_total_VaR}\n"
        )


if __name__ == "__main__":
    main()
