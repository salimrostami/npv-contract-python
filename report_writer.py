from contract import Contract
from project import Project


def print_header():
    heads = [
        "type",
        "reward",
        "rate",
        "salary",
        "SB_ENPV",
        "B_ENPV",
        "SO_ENPV",
        "O_ENPV",
        "SB_Risk%",
        "B_Risk%",
        "SO_Risk%",
        "O_Risk%",
        "SB_VaR",
        "B_VaR",
        "SO_VaR",
        "T_VaR",
    ]
    print("\n")
    print(" ".join(f"{x:<9}" for x in heads))


def print_reports(contract: Contract, project: Project):
    row = [
        contract.type,
        contract.reward,
        contract.reimburse_rate,
        contract.salary,
        project.sim_results.builder.enpv,
        project.exact_results.builder.enpv,
        project.sim_results.owner.enpv,
        project.exact_results.owner.enpv,
        project.sim_results.builder.risk,
        project.exact_results.builder.risk,
        project.sim_results.owner.risk,
        project.exact_results.owner.risk,
        project.sim_results.builder.var,
        project.exact_results.builder.var,
        project.sim_results.owner.var,
        round(project.sim_results.builder.var + project.sim_results.owner.var, 0),
    ]
    print(" ".join(f"{x:<9}" for x in row))
