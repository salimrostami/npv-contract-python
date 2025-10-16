from pyparsing import TextIO
from source.definit.contract import Contract
from source.definit.project import ExactResults, Project, bestContract
from datetime import datetime
import os
import atexit
from source.definit.param import params

# from source.utility.math_helpers import precise_round


def print_and_log(log_file: TextIO, text: str):
    """Helper to print to console and log to file."""
    print(text)
    print(text, file=log_file, flush=True)  # flush right away
    log_file.flush()
    # log_file.write(text + "\n")


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
    file_name = f"{timestamp}-P{project.proj_id}-xFull.txt"

    # Ensure the 'reports' directory exists
    root_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))
    )  # Go up one level
    reports_dir = os.path.join(root_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # Update file path to use the 'reports' directory
    file_path = os.path.join(reports_dir, file_name)
    log_file: TextIO
    # create the file_path file and open it in write mode
    log_file = open(file_path, "w")

    # print_and_log(log_file, "\n")
    print_and_log(log_file, "\t".join(f"{x:<10}" for x in heads))

    return log_file


def full_report(project: Project, contract: Contract, log_file: TextIO):
    r = round  # tiny alias
    rp = params.roundPrecision
    # Always printed items
    row = [
        contract.type,
        contract.subtype,
        r(contract.reward, 4),
        r(contract.reimburse_rate, 4),
        r(contract.salary, 4),
        r(project.exact_results.builder.enpv, rp),
        r(project.exact_results.owner.enpv, rp),
    ]

    # For risk values: add simulation results only if simulation is True.
    if params.isSim:
        row.append(r(project.sim_results.builder.risk, rp))
    row.append(r(project.exact_results.builder.risk, rp))

    if params.isSim:
        row.append(r(project.sim_results.owner.risk, rp))
    row.append(r(project.exact_results.owner.risk, rp))

    # For var values: add simulation results only if simulation is True.
    if params.isSim:
        row.append(r(project.sim_results.builder.var, rp))
    row.append(r(project.exact_results.builder.var, rp))

    if params.isSim:
        row.append(r(project.sim_results.owner.var, rp))
    row.append(r(project.exact_results.owner.var, rp))

    # Always print the final rounded value.
    row.append(
        r(project.exact_results.builder.var + project.exact_results.owner.var, rp)
    )

    print_and_log(log_file, "\t".join(f"{x:<10}" for x in row))
    atexit.register(log_file.close)


def opt_header():
    heads = [
        "time",
        "proj_id",
        # "c_fixed",
        # "c_low",
        # "c_high",
        # "d_low",
        # "d_high",
        # "disc_rate",
        # "b_t_enpv",
        # "o_income",
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

    log_file: TextIO
    # check if opt_report file already exists, if so, open it in append mode
    if os.path.exists(file_path):
        # open in append mode
        log_file = open(file_path, "a", buffering=1, encoding="utf-8")
    else:
        # create the file_path file and open it in write mode
        log_file = open(file_path, "w", buffering=1, encoding="utf-8")
        # print_and_log(log_file, "\n")
        print_and_log(log_file, "\t".join(f"{x:<10}" for x in heads))

    return log_file


def _build_common_row(project: Project):
    return [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        project.proj_id,
        # project.c_down_pay,
        # project.c_uni_low_b,
        # project.c_uni_high_a,
        # project.d_uni_low_l,
        # project.d_uni_high_h,
        # project.discount_rate,
        # project.builder_target_enpv,
        # project.owner_income,
    ]


def _build_opt_row(opt: bestContract, rp):
    c, b, o = opt.contract, opt.builder, opt.owner
    r = round  # tiny alias
    return [
        c.type,
        r(c.reward, 4),
        r(c.reimburse_rate, 4),
        r(c.salary, 4),
        r(b.enpv, rp),
        r(o.enpv, rp),
        r(b.risk, rp),
        r(o.risk, rp),
        r(b.var, rp),
        r(o.var, rp),
        r(opt.tvar, rp),
    ]


def _fmt_line(values):
    return "\t".join("" if x is None else f"{x:<10}" for x in values)


def opt_report(project: Project, log_file: TextIO):
    common = _build_common_row(project)
    rp = params.roundPrecision

    for attr in ("lsOpt", "cpOpt", "lhOpt", "tmOpt"):
        opt = getattr(project, attr)
        line = _fmt_line(common + _build_opt_row(opt, rp))
        print_and_log(log_file, line)

    atexit.register(log_file.close)


def sens_header(project: Project, name: str):
    heads = [
        "type",
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

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{timestamp}-P{project.proj_id}-{name}.txt"

    # Ensure the 'reports' directory exists
    root_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))
    )  # Go up one level
    reports_dir = os.path.join(root_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # Update file path to use the 'reports' directory
    file_path = os.path.join(reports_dir, file_name)
    log_file: TextIO
    # create the file_path file and open it in write mode
    log_file = open(file_path, "w")

    # print_and_log(log_file, "\n")
    print_and_log(log_file, "\t".join("" if x is None else f"{x:<10}" for x in heads))

    return log_file


def sens_report(cont: Contract, res: ExactResults, log_file: TextIO):
    rp = params.roundPrecision
    r = round  # tiny alias
    # Always printed items
    row = [
        cont.type,
        r(cont.reward, 4),
        r(cont.reimburse_rate, 4),
        r(cont.salary, 4),
        r(res.builder.enpv, rp),
        r(res.owner.enpv, rp),
        r(res.builder.risk, rp),
        r(res.owner.risk, rp),
        r(res.builder.var, rp),
        r(res.owner.var, rp),
        r(res.builder.var + res.owner.var, rp),
    ]

    print_and_log(log_file, "\t".join("" if x is None else f"{x:<10}" for x in row))
    atexit.register(log_file.close)
