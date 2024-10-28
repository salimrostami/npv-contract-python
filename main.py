from project import projects, Project
from contract import contracts, Contract, make_contracts
from simulation import simulate
from report_writer import Report, print_reports, print_header
from builder_exact import builder_enpv, builder_risk
from owner_exact import owner_enpv, owner_risk
from initialize import set_owner_threshold

num_simulations = 100000
distribution = "uni"

try:
    projects.append(
        Project("001", -5000, -35000, -5000, 0.1, 1, 10, 0.1, 0, 5000, 100000)
    )
except ValueError as e:
    print(e)


def main():
    proj: Project
    cont: Contract
    rep = Report()
    print_header()
    min_total_VaR = -1000000
    max_total_VaR = 0
    for proj in projects:
        make_contracts(proj, proj.builder_target_enpv, distribution)
        set_owner_threshold(proj, distribution)
        for cont in contracts:
            rep.simulation = simulate(proj, cont, num_simulations, distribution)
            rep.exact_B_ENPV = round(builder_enpv(proj, cont, distribution), 2)
            rep.exact_B_risk = round(100 * builder_risk(proj, cont, distribution), 2)
            rep.exact_O_ENPV = round(owner_enpv(proj, cont, distribution), 2)
            rep.exact_O_risk = round(100 * owner_risk(proj, cont, distribution), 2)
            print_reports(rep, cont, proj)
            if round(rep.simulation[2] + rep.simulation[5], 0) > min_total_VaR:
                min_total_VaR = round(rep.simulation[2] + rep.simulation[5], 0)
            if round(rep.simulation[2] + rep.simulation[5], 0) < max_total_VaR:
                max_total_VaR = round(rep.simulation[2] + rep.simulation[5], 0)
        print(f"Min Total VaR: {min_total_VaR}, Max Total VaR: {max_total_VaR}")


if __name__ == "__main__":
    main()
