from source.definit.contract import Contract
from source.definit.project import Project
from datetime import datetime
import os
import atexit
from source.definit.param import params


def print_and_log(log_file, text: str):
    """Helper to print to console and log to file."""
    print(text)
    log_file.write(text + "\n")


def full_header(project: Project, isSim: bool):
    heads = [
        "type",
        "subtype",
        "reward",
        "rate",
        "salary",
        "B_ENPV",
        "O_ENPV",
    ]
    if isSim:
        heads.append("SB_Risk%")
    heads.append("B_Risk%")

    if isSim:
        heads.append("SO_Risk%")
    heads.append("O_Risk%")

    # For var values: add simulation results only if simulation is True.
    if isSim:
        heads.append("SB_VaR")
    heads.append("B_VaR")

    if isSim:
        heads.append("SO_VaR")
    heads.append("O_VaR")

    # Always print the final rounded value.
    heads.append("T_VaR")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{timestamp}_P{project.proj_id}.txt"

    # Ensure the 'reports' directory exists
    reports_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # Update file path to use the 'reports' directory
    file_path = os.path.join(reports_dir, file_name)
    log_file = open(file_path, "w")

    # print_and_log(log_file, "\n")
    print_and_log(log_file, "\t".join(f"{x:<9}" for x in heads))

    return log_file


def full_report(log_file, contract: Contract, project: Project, isSim: bool):
    # Always printed items
    row = [
        contract.type,
        contract.subtype,
        contract.reward,
        contract.reimburse_rate,
        contract.salary,
        project.exact_results.builder.enpv,
        project.exact_results.owner.enpv,
    ]

    # For risk values: add simulation results only if simulation is True.
    if isSim:
        row.append(project.sim_results.builder.risk)
    row.append(project.exact_results.builder.risk)

    if isSim:
        row.append(project.sim_results.owner.risk)
    row.append(project.exact_results.owner.risk)

    # For var values: add simulation results only if simulation is True.
    if isSim:
        row.append(project.sim_results.builder.var)
    row.append(project.exact_results.builder.var)

    if isSim:
        row.append(project.sim_results.owner.var)
    row.append(project.exact_results.owner.var)

    # Always print the final rounded value.
    row.append(
        round(
            project.exact_results.builder.var + project.exact_results.owner.var,
            params.roundPrecision,
        )
    )

    print_and_log(log_file, "\t".join(f"{x:<9}" for x in row))
    atexit.register(log_file.close)
