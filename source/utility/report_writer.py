from typing import TextIO
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


def full_header(proj: Project):
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

    if params.isSim:
        heads.append("SB_CVaR")
    heads.append("B_CVaR")

    if params.isSim:
        heads.append("SO_CVaR")
    heads.append("O_CVaR")

    if params.isSim:
        heads.append("ST_CVaR")
    heads.append("T_CVaR")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{timestamp}-P{proj.proj_id}-xFull.txt"

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


def full_report(proj: Project, cont: Contract, log_file: TextIO):
    r = round  # tiny alias
    rp = params.roundPrecision
    # Always printed items
    row = [
        cont.type,
        cont.subtype,
        r(cont.reward, 4),
        r(cont.rate, 4),
        r(cont.salary, 4),
        r(proj.exact_results.builder.enpv, rp),
        r(proj.exact_results.owner.enpv, rp),
    ]

    # For risk values: add simulation results only if simulation is True.
    if params.isSim:
        row.append(r(proj.sim_results.builder.risk, rp))
    row.append(r(proj.exact_results.builder.risk, rp))

    if params.isSim:
        row.append(r(proj.sim_results.owner.risk, rp))
    row.append(r(proj.exact_results.owner.risk, rp))

    # For var values: add simulation results only if simulation is True.
    if params.isSim:
        row.append(r(proj.sim_results.builder.var, rp))
    row.append(r(proj.exact_results.builder.var, rp))

    if params.isSim:
        row.append(r(proj.sim_results.owner.var, rp))
    row.append(r(proj.exact_results.owner.var, rp))

    # Always print the final rounded value.
    row.append(r(proj.exact_results.builder.var + proj.exact_results.owner.var, rp))

    if params.isSim:
        row.append(r(proj.sim_results.builder.cvar, rp))
    row.append(r(proj.exact_results.builder.cvar, rp))

    if params.isSim:
        row.append(r(proj.sim_results.owner.cvar, rp))
    row.append(r(proj.exact_results.owner.cvar, rp))

    if params.isSim:
        row.append(r(proj.sim_results.builder.cvar + proj.sim_results.owner.cvar, rp))
    row.append(r(proj.exact_results.builder.cvar + proj.exact_results.owner.cvar, rp))

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
    ]
    params.isSim and heads.append("SB_Risk")
    heads.append("B_Risk")

    params.isSim and heads.append("SO_Risk")
    heads.append("O_Risk")

    heads.append("B_VaR")
    heads.append("O_VaR")

    params.isSim and heads.append("ST_VaR")
    heads.append("T_VaR")

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


def _build_common_row(proj: Project):
    return [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        proj.proj_id,
        # proj.c_down_pay,
        # proj.c_low_b,
        # proj.c_high_a,
        # proj.d_low_l,
        # proj.d_high_h,
        # proj.discount_rate,
        # proj.b_t_enpv,
        # proj.owner_income,
    ]


def _build_opt_row(opt: bestContract, rp):
    c, b, o = opt.cont, opt.builder, opt.owner
    r = round  # tiny alias
    row = [
        c.type,
        r(c.reward, 4),
        r(c.rate, 4),
        r(c.salary, 4),
        r(b.enpv, rp),
        r(o.enpv, rp),
    ]

    params.isSim and row.append(r(opt.sim_results.builder.risk, rp))
    row.append(r(b.risk, rp))

    params.isSim and row.append(r(opt.sim_results.owner.risk, rp))
    row.append(r(o.risk, rp))

    row.append(r(b.var, rp))
    row.append(r(o.var, rp))

    params.isSim and row.append(
        r(opt.sim_results.builder.var + opt.sim_results.owner.var, rp)
    )
    row.append(r(opt.tvar, rp))

    return row


def _fmt_line(values):
    return "\t".join("" if x is None else f"{x:<10}" for x in values)


def opt_report(proj: Project, log_file: TextIO):
    common = _build_common_row(proj)
    rp = params.roundPrecision

    for attr in ("lsOpt", "cpOpt", "lhOpt", "tmOpt"):
        opt = getattr(proj, attr)
        line = _fmt_line(common + _build_opt_row(opt, rp))
        print_and_log(log_file, line)

    atexit.register(log_file.close)


def sens_header(proj: Project, name: str):
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
    file_name = f"{timestamp}-P{proj.proj_id}-{name}.txt"

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
        r(cont.rate, 4),
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
