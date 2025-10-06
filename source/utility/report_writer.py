from source.definit.contract import Contract
from source.definit.project import Project
from datetime import datetime
import os
import atexit
from source.definit.param import params

# from source.utility.math_helpers import precise_round


def print_and_log(log_file, text: str):
    """Helper to print to console and log to file."""
    print(text)
    log_file.write(text + "\n")


def full_header(project: Project):
    heads = [
        "type",
        "subtype",
        "reward",
        "rate",
        "salary",
        "B_ENPV",
        "O_ENPV",
    ]
    if params.isSim:
        heads.append("SB_Risk%")
    heads.append("B_Risk%")

    if params.isSim:
        heads.append("SO_Risk%")
    heads.append("O_Risk%")

    # For var values: add simulation results only if simulation is True.
    if params.isSim:
        heads.append("SB_VaR")
    heads.append("B_VaR")

    if params.isSim:
        heads.append("SO_VaR")
    heads.append("O_VaR")

    # Always print the final rounded value.
    heads.append("T_VaR")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{timestamp}_P{project.proj_id}.txt"

    # Ensure the 'reports' directory exists
    root_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))
    )  # Go up one level
    reports_dir = os.path.join(root_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # Update file path to use the 'reports' directory
    file_path = os.path.join(reports_dir, file_name)
    log_file = open(file_path, "w")

    # print_and_log(log_file, "\n")
    print_and_log(log_file, "\t".join(f"{x:<9}" for x in heads))

    return log_file


def full_report(project: Project, contract: Contract, log_file):
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
    if params.isSim:
        row.append(project.sim_results.builder.risk)
    row.append(project.exact_results.builder.risk)

    if params.isSim:
        row.append(project.sim_results.owner.risk)
    row.append(project.exact_results.owner.risk)

    # For var values: add simulation results only if simulation is True.
    if params.isSim:
        row.append(project.sim_results.builder.var)
    row.append(project.exact_results.builder.var)

    if params.isSim:
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


def opt_header():
    heads = [
        "time",
        "proj_id",
        "c_fixed",
        "c_low",
        "c_high",
        "d_low",
        "d_high",
        "disc_rate",
        "b_t_enpv",
        "o_income",
        "cont_type",
        "reward",
        "rate",
        "salary",
        "B_ENPV",
        "O_ENPV",
        "B_Risk",
        "O_Risk",
        "B_VaR",
        "O_VaR",
        "T_VaR",
    ]
    # if params.isSim:
    #     heads.append("SB_Risk%")
    # heads.append("B_Risk%")

    # Ensure the 'reports' directory exists
    root_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))
    )  # Go up one level
    reports_dir = os.path.join(root_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    file_name = "~opt_report.txt"
    file_path = os.path.join(reports_dir, file_name)

    # check if opt_report file already exists, if so, open it in append mode
    if os.path.exists(file_path):
        # open in append mode
        log_file = open(file_path, "a")
    else:
        # create the file_path file and open it in write mode
        log_file = open(file_path, "w")
        # print_and_log(log_file, "\n")
        print_and_log(log_file, "\t".join(f"{x:<10}" for x in heads))

    return log_file


def opt_report(project: Project, log_file):
    # print the opt report to opt_report.txt file
    common_row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        project.proj_id,
        project.c_down_pay,
        project.c_uni_low_b,
        project.c_uni_high_a,
        project.d_uni_low_l,
        project.d_uni_high_h,
        project.discount_rate,
        project.builder_target_enpv,
        project.owner_income,
        project.owner_target_enpv,
        project.owner_threshold,
    ]
    ls_row = [
        project.lsOpt.contract.type,
        round(project.lsOpt.contract.reward, params.roundPrecision),
        round(project.lsOpt.contract.reimburse_rate, params.roundPrecision),
        round(project.lsOpt.contract.salary, params.roundPrecision),
        round(project.lsOpt.builder.enpv, params.roundPrecision),
        round(project.lsOpt.owner.enpv, params.roundPrecision),
        round(project.lsOpt.builder.risk, params.roundPrecision),
        round(project.lsOpt.owner.risk, params.roundPrecision),
        round(project.lsOpt.builder.var, params.roundPrecision),
        round(project.lsOpt.owner.var, params.roundPrecision),
        round(project.lsOpt.tvar, params.roundPrecision),
    ]
    cp_row = [
        project.cpOpt.contract.type,
        round(project.cpOpt.contract.reward, params.roundPrecision),
        round(project.cpOpt.contract.reimburse_rate, params.roundPrecision),
        round(project.cpOpt.contract.salary, params.roundPrecision),
        round(project.cpOpt.builder.enpv, params.roundPrecision),
        round(project.cpOpt.owner.enpv, params.roundPrecision),
        round(project.cpOpt.builder.risk, params.roundPrecision),
        round(project.cpOpt.owner.risk, params.roundPrecision),
        round(project.cpOpt.builder.var, params.roundPrecision),
        round(project.cpOpt.owner.var, params.roundPrecision),
        round(project.cpOpt.tvar, params.roundPrecision),
    ]
    lh_row = [
        project.lhOpt.contract.type,
        round(project.lhOpt.contract.reward, params.roundPrecision),
        round(project.lhOpt.contract.reimburse_rate, params.roundPrecision),
        round(project.lhOpt.contract.salary, params.roundPrecision),
        round(project.lhOpt.builder.enpv, params.roundPrecision),
        round(project.lhOpt.owner.enpv, params.roundPrecision),
        round(project.lhOpt.builder.risk, params.roundPrecision),
        round(project.lhOpt.owner.risk, params.roundPrecision),
        round(project.lhOpt.builder.var, params.roundPrecision),
        round(project.lhOpt.owner.var, params.roundPrecision),
        round(project.lhOpt.tvar, params.roundPrecision),
    ]
    tm_row = [
        project.tmOpt.contract.type,
        round(project.tmOpt.contract.reward, params.roundPrecision),
        round(project.tmOpt.contract.reimburse_rate, params.roundPrecision),
        round(project.tmOpt.contract.salary, params.roundPrecision),
        round(project.tmOpt.builder.enpv, params.roundPrecision),
        round(project.tmOpt.owner.enpv, params.roundPrecision),
        round(project.tmOpt.builder.risk, params.roundPrecision),
        round(project.tmOpt.owner.risk, params.roundPrecision),
        round(project.tmOpt.builder.var, params.roundPrecision),
        round(project.tmOpt.owner.var, params.roundPrecision),
        round(project.tmOpt.tvar, params.roundPrecision),
    ]

    print_and_log(
        log_file,
        "\t".join(f"{'' if x is None else x:<10}" for x in common_row + ls_row),
    )
    print_and_log(
        log_file,
        "\t".join(f"{'' if x is None else x:<10}" for x in common_row + cp_row),
    )
    print_and_log(
        log_file,
        "\t".join(f"{'' if x is None else x:<10}" for x in common_row + lh_row),
    )
    print_and_log(
        log_file,
        "\t".join(f"{'' if x is None else x:<10}" for x in common_row + tm_row),
    )
    atexit.register(log_file.close)
