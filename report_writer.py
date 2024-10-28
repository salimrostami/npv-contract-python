from contract import Contract
from project import Project


class Report:
    def __init__(self):
        # [sim_B_ENPV, sim_B_risk, sim_B_VaR, sim_O_ENPV, sim_O_risk, sim_O_VaR]
        self.simulation = []
        self.exact_B_ENPV = 0
        self.exact_B_risk = 0
        self.exact_O_ENPV = 0
        self.exact_O_risk = 0


def print_header():
    heads = [
        "type",
        "reward",
        "rate",
        "salary",
        "SB_ENPV",
        "B_ENPV",
        "SB_Risk%",
        "B_Risk%",
        "SO_ENPV",
        "O_ENPV",
        "SO_Risk%",
        "O_Risk%",
        "SB_VaR",
        "SO_VaR",
        "T_VaR",
    ]
    print("\n")
    print(" ".join(f"{x:<9}" for x in heads))


def print_reports(report: Report, contract: Contract, project: Project):
    total_VaR = round(report.simulation[2] + report.simulation[5], 0)
    row = [
        contract.type,
        contract.reward,
        contract.reimburse_rate,
        contract.salary,
        report.simulation[0],
        report.exact_B_ENPV,
        report.simulation[1],
        report.exact_B_risk,
        report.simulation[3],
        report.exact_O_ENPV,
        report.simulation[4],
        report.exact_O_risk,
        report.simulation[2],
        report.simulation[5],
        total_VaR,
    ]
    print(" ".join(f"{x:<9}" for x in row))
