from typing import TextIO
from source.definit.contract import Contract
from source.definit.project import ExactResults, Project, bestContract
from datetime import datetime
import os
import atexit
from source.definit.param import params

# from source.utility.math_helpers import precise_round


def print_console(text: str):
    print(text)


def log_report(log_file: TextIO, text: str):
    print(text, file=log_file, flush=True)  # flush right away
    log_file.flush()


def print_and_log(log_file: TextIO, text: str):
    """Backward-compatible helper where console and file output are the same."""
    print_console(text)
    log_report(log_file, text)


def full_header(proj: Project):
    file_heads = [
        "type",
        "subtype",
        "reward",
        "rate",
        "salary",
        "B_ENPV",
        "O_ENPV",
    ]
    if params.isSim:
        file_heads.append("SB_Risk%")
    file_heads.append("B_Risk%")

    if params.isSim:
        file_heads.append("SO_Risk%")
    file_heads.append("O_Risk%")

    # For var values: add simulation results only if simulation is True.
    if params.isSim:
        file_heads.append("SB_VaR")
    file_heads.append("B_VaR")

    if params.isSim:
        file_heads.append("SO_VaR")
    file_heads.append("O_VaR")

    # Always print the final rounded value.
    file_heads.append("T_VaR")

    if params.isSim:
        file_heads.append("SB_CVaR")
    file_heads.append("B_CVaR")

    if params.isSim:
        file_heads.append("SO_CVaR")
    file_heads.append("O_CVaR")

    if params.isSim:
        file_heads.append("ST_CVaR")
    file_heads.append("T_CVaR")

    console_heads = [
        "type",
        "subtype",
        "B_Risk%",
        "O_Risk%",
        "B_VaR",
        "O_VaR",
        "T_VaR",
    ]
    if params.isSim:
        console_heads.append("SB_CVaR")
    console_heads.append("B_CVaR")
    if params.isSim:
        console_heads.append("SO_CVaR")
    console_heads.append("O_CVaR")
    console_heads.append("T_CVaR")

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

    print_console("\t".join(f"{x:<10}" for x in console_heads))
    log_report(log_file, "\t".join(f"{x:<10}" for x in file_heads))

    return log_file


def full_report(proj: Project, cont: Contract, log_file: TextIO):
    r = round  # tiny alias
    rp = params.roundPrecision
    # Full row for report file (do not reduce columns)
    file_row = [
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
        file_row.append(r(proj.sim_results.builder.risk, rp))
    file_row.append(r(proj.exact_results.builder.risk, rp))

    if params.isSim:
        file_row.append(r(proj.sim_results.owner.risk, rp))
    file_row.append(r(proj.exact_results.owner.risk, rp))

    # For var values: add simulation results only if simulation is True.
    if params.isSim:
        file_row.append(r(proj.sim_results.builder.var, rp))
    file_row.append(r(proj.exact_results.builder.var, rp))

    if params.isSim:
        file_row.append(r(proj.sim_results.owner.var, rp))
    file_row.append(r(proj.exact_results.owner.var, rp))

    # Always print the final rounded value.
    file_row.append(r(proj.exact_results.builder.var + proj.exact_results.owner.var, rp))

    if params.isSim:
        file_row.append(r(proj.sim_results.builder.cvar, rp))
    file_row.append(r(proj.exact_results.builder.cvar, rp))

    if params.isSim:
        file_row.append(r(proj.sim_results.owner.cvar, rp))
    file_row.append(r(proj.exact_results.owner.cvar, rp))

    if params.isSim:
        file_row.append(r(proj.sim_results.builder.cvar + proj.sim_results.owner.cvar, rp))
    file_row.append(r(proj.exact_results.builder.cvar + proj.exact_results.owner.cvar, rp))

    # Reduced row for terminal output
    console_row = [
        cont.type,
        cont.subtype,
        r(proj.exact_results.builder.risk, rp),
        r(proj.exact_results.owner.risk, rp),
        r(proj.exact_results.builder.var, rp),
        r(proj.exact_results.owner.var, rp),
        r(proj.exact_results.builder.var + proj.exact_results.owner.var, rp),
    ]
    if params.isSim:
        console_row.append(r(proj.sim_results.builder.cvar, rp))
    console_row.append(r(proj.exact_results.builder.cvar, rp))
    if params.isSim:
        console_row.append(r(proj.sim_results.owner.cvar, rp))
    console_row.append(r(proj.exact_results.owner.cvar, rp))
    console_row.append(
        r(proj.exact_results.builder.cvar + proj.exact_results.owner.cvar, rp)
    )

    print_console("\t".join(f"{x:<10}" for x in console_row))
    log_report(log_file, "\t".join(f"{x:<10}" for x in file_row))
    atexit.register(log_file.close)


def _open_opt_log(file_name: str):
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    reports_dir = os.path.join(root_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    file_path = os.path.join(reports_dir, file_name)
    if os.path.exists(file_path):
        return open(file_path, "a", buffering=1, encoding="utf-8")
    return open(file_path, "w", buffering=1, encoding="utf-8")


def _objective_totals(opt: bestContract):
    tvar = (
        opt.tvar
        if opt.tvar is not None
        else (
            None
            if opt.builder.var is None or opt.owner.var is None
            else opt.builder.var + opt.owner.var
        )
    )
    tcvar = (
        opt.tcvar
        if opt.tcvar is not None
        else (
            None
            if opt.builder.cvar is None or opt.owner.cvar is None
            else opt.builder.cvar + opt.owner.cvar
        )
    )
    return tvar, tcvar


def opt_var_header():
    file_heads = [
        "time",
        "proj_id",
        "cont_type",
        "reward",
        "rate",
        "salary",
        "B_ENPV",
        "O_ENPV",
    ]
    params.isSim and file_heads.append("SB_Risk")
    file_heads.append("B_Risk")
    params.isSim and file_heads.append("SO_Risk")
    file_heads.append("O_Risk")
    file_heads.append("B_VaR")
    file_heads.append("O_VaR")
    params.isSim and file_heads.append("ST_VaR")
    file_heads.append("T_VaR")
    file_heads.append("B_CVaR")
    file_heads.append("O_CVaR")
    params.isSim and file_heads.append("ST_CVaR")
    file_heads.append("T_CVaR")

    console_heads = [
        "time",
        "proj_id",
        "cont_type",
        "B_Risk",
        "O_Risk",
        "B_VaR",
        "O_VaR",
        "T_VaR",
    ]

    log_file = _open_opt_log("~opt_var_report.txt")
    print_console("\t".join(f"{x:<10}" for x in console_heads))
    if log_file.tell() == 0:
        log_report(log_file, "\t".join(f"{x:<10}" for x in file_heads))
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


def _build_opt_var_file_row(opt: bestContract, rp):
    c, b, o = opt.cont, opt.builder, opt.owner
    r = round  # tiny alias
    sr = lambda x: None if x is None else r(x, rp)
    tvar, tcvar = _objective_totals(opt)
    row = [
        c.type,
        r(c.reward, 4),
        r(c.rate, 4),
        r(c.salary, 4),
        sr(b.enpv),
        sr(o.enpv),
    ]

    params.isSim and row.append(sr(opt.sim_results.builder.risk))
    row.append(sr(b.risk))

    params.isSim and row.append(sr(opt.sim_results.owner.risk))
    row.append(sr(o.risk))

    row.append(sr(b.var))
    row.append(sr(o.var))

    params.isSim and row.append(
        sr(
            None
            if opt.sim_results.builder.var is None or opt.sim_results.owner.var is None
            else opt.sim_results.builder.var + opt.sim_results.owner.var
        )
    )
    row.append(sr(tvar))
    row.append(sr(b.cvar))
    row.append(sr(o.cvar))
    params.isSim and row.append(
        sr(
            None
            if opt.sim_results.builder.cvar is None or opt.sim_results.owner.cvar is None
            else opt.sim_results.builder.cvar + opt.sim_results.owner.cvar
        )
    )
    row.append(sr(tcvar))

    return row


def _fmt_line(values):
    return "\t".join("" if x is None else f"{x:<10}" for x in values)


def _build_opt_var_console_row(opt: bestContract, rp):
    b, o = opt.builder, opt.owner
    r = round
    sr = lambda x: None if x is None else r(x, rp)
    tvar, _ = _objective_totals(opt)
    return [
        opt.cont.type,
        sr(b.risk),
        sr(o.risk),
        sr(b.var),
        sr(o.var),
        sr(tvar),
    ]


def opt_var_report(proj: Project, log_file: TextIO):
    common = _build_common_row(proj)
    rp = params.roundPrecision

    for attr in ("lsOpt", "cpOpt", "lhOpt", "tmOpt"):
        opt = getattr(proj, attr)
        console_line = _fmt_line(common + _build_opt_var_console_row(opt, rp))
        file_line = _fmt_line(common + _build_opt_var_file_row(opt, rp))
        print_console(console_line)
        log_report(log_file, file_line)

    atexit.register(log_file.close)


def opt_cvar_header():
    file_heads = [
        "time",
        "proj_id",
        "cont_type",
        "reward",
        "rate",
        "salary",
        "B_ENPV",
        "O_ENPV",
    ]
    params.isSim and file_heads.append("SB_Risk")
    file_heads.append("B_Risk")
    params.isSim and file_heads.append("SO_Risk")
    file_heads.append("O_Risk")
    file_heads.append("B_CVaR")
    file_heads.append("O_CVaR")
    params.isSim and file_heads.append("ST_CVaR")
    file_heads.append("T_CVaR")
    file_heads.append("B_VaR")
    file_heads.append("O_VaR")
    params.isSim and file_heads.append("ST_VaR")
    file_heads.append("T_VaR")

    console_heads = [
        "time",
        "proj_id",
        "cont_type",
        "B_Risk",
        "O_Risk",
        "B_CVaR",
        "O_CVaR",
        "T_CVaR",
    ]

    log_file = _open_opt_log("~opt_cvar_report.txt")
    print_console("\t".join(f"{x:<10}" for x in console_heads))
    if log_file.tell() == 0:
        log_report(log_file, "\t".join(f"{x:<10}" for x in file_heads))
    return log_file


def _build_opt_cvar_file_row(opt: bestContract, rp):
    c, b, o = opt.cont, opt.builder, opt.owner
    r = round
    sr = lambda x: None if x is None else r(x, rp)
    tvar, tcvar = _objective_totals(opt)
    row = [
        c.type,
        r(c.reward, 4),
        r(c.rate, 4),
        r(c.salary, 4),
        sr(b.enpv),
        sr(o.enpv),
    ]

    params.isSim and row.append(sr(opt.sim_results.builder.risk))
    row.append(sr(b.risk))

    params.isSim and row.append(sr(opt.sim_results.owner.risk))
    row.append(sr(o.risk))

    row.append(sr(b.cvar))
    row.append(sr(o.cvar))

    params.isSim and row.append(
        sr(
            None
            if opt.sim_results.builder.cvar is None or opt.sim_results.owner.cvar is None
            else opt.sim_results.builder.cvar + opt.sim_results.owner.cvar
        )
    )
    row.append(sr(tcvar))
    row.append(sr(b.var))
    row.append(sr(o.var))
    params.isSim and row.append(
        sr(
            None
            if opt.sim_results.builder.var is None or opt.sim_results.owner.var is None
            else opt.sim_results.builder.var + opt.sim_results.owner.var
        )
    )
    row.append(sr(tvar))

    return row


def _build_opt_cvar_console_row(opt: bestContract, rp):
    b, o = opt.builder, opt.owner
    r = round
    sr = lambda x: None if x is None else r(x, rp)
    _, tcvar = _objective_totals(opt)
    return [
        opt.cont.type,
        sr(b.risk),
        sr(o.risk),
        sr(b.cvar),
        sr(o.cvar),
        sr(tcvar),
    ]


def opt_cvar_report(proj: Project, log_file: TextIO):
    common = _build_common_row(proj)
    rp = params.roundPrecision

    for attr in ("lsOpt", "cpOpt", "lhOpt", "tmOpt"):
        opt = getattr(proj, attr)
        console_line = _fmt_line(common + _build_opt_cvar_console_row(opt, rp))
        file_line = _fmt_line(common + _build_opt_cvar_file_row(opt, rp))
        print_console(console_line)
        log_report(log_file, file_line)

    atexit.register(log_file.close)


def opt_header():
    # Backward compatible alias for var optimization report.
    return opt_var_header()


def opt_report(proj: Project, log_file: TextIO):
    # Backward compatible alias for var optimization report.
    return opt_var_report(proj, log_file)


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
