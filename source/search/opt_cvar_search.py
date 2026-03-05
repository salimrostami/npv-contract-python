from typing import List, Optional, TextIO, Tuple
from source.definit.contract import Contract, calc_salary, calc_reward
from source.definit.initialize import initialize
from source.definit.project import Project, bestContract
from source.evaluate.builder.builder_cvar import builder_CVaR
from source.evaluate.owner.owner_cvar import owner_CVaR
from source.definit.param import params
from source.evaluate.simulation import simulate
from source.utility.math_helpers import precise_round
from source.utility.report_writer import opt_cvar_header, opt_cvar_report, print_and_log
from source.evaluate.exact_eval import exact_calculations
from source.evaluate.builder.builder_enpv import builder_enpv
from source.evaluate.owner.owner_enpv import owner_enpv

TM_LOCAL_RATE_STEP = 0.01


def _is_geq(a: float, b: float) -> bool:
    rp = params.roundPrecision
    return precise_round(a, rp) >= precise_round(b, rp)


def _is_gt(a: float, b: float) -> bool:
    rp = params.roundPrecision
    return precise_round(a, rp) > precise_round(b, rp)


def _cvar_components(proj: Project, cont: Contract) -> Tuple[float, float, float]:
    benpv = builder_enpv(proj, cont)
    oenpv = owner_enpv(proj, cont)
    bcvar = builder_CVaR(proj, cont) - benpv
    ocvar = owner_CVaR(proj, cont) - oenpv
    return bcvar, ocvar, bcvar + ocvar


def _local_peak_indices(values: List[float]) -> List[int]:
    n_values = len(values)
    if n_values == 0:
        return []

    if n_values == 1:
        return [0]

    raw: List[int] = []
    if _is_gt(values[0], values[1]):
        raw.append(0)

    for i in range(1, n_values - 1):
        better_than_left = _is_gt(values[i], values[i - 1])
        better_than_right = _is_gt(values[i], values[i + 1])
        if (
            _is_geq(values[i], values[i - 1])
            and _is_geq(values[i], values[i + 1])
            and (better_than_left or better_than_right)
        ):
            raw.append(i)

    if _is_gt(values[-1], values[-2]):
        raw.append(n_values - 1)

    if not raw:
        best_i = max(
            range(n_values),
            key=lambda idx: precise_round(values[idx], params.roundPrecision),
        )
        return [best_i]

    merged: List[int] = []
    run_start = raw[0]
    run_end = raw[0]

    for idx in raw[1:]:
        if idx == run_end + 1:
            run_end = idx
            continue

        best_i = run_start
        for j in range(run_start + 1, run_end + 1):
            if _is_gt(values[j], values[best_i]):
                best_i = j
        merged.append(best_i)
        run_start = idx
        run_end = idx

    best_i = run_start
    for j in range(run_start + 1, run_end + 1):
        if _is_gt(values[j], values[best_i]):
            best_i = j
    merged.append(best_i)

    return merged


def _build_tm_contract_for_rate(
    proj: Project, rate: float
) -> Tuple[Contract, float, float, float]:
    cont = Contract("optcont", 0, 0, 0, "---")
    cont.type = "tm"
    cont.rate = rate
    smax = calc_salary(proj, proj.b_t_enpv, cont.rate, 0)
    smin = max(params.minSafeSalary, 0.01 * smax)
    cont.salary, _ = opt_contract_peakfinder(proj, cont, "lh", smin, smax)
    cont.reward = max(0, calc_reward(proj, proj.b_t_enpv, cont.rate, cont.salary))
    bcvar, ocvar, tcvar = _cvar_components(proj, cont)
    return cont, bcvar, ocvar, tcvar


def _opt_tm_contract_with_local_scan(
    proj: Project, log_file: Optional[TextIO] = None
) -> Tuple[float, Contract]:
    step = TM_LOCAL_RATE_STEP
    n_points = int(round(1.0 / step)) + 1
    rates = [i * step for i in range(n_points)]

    scan_cont = Contract("optcont", 0, 0, 0, "---")
    scan_cont.type = "tm"
    coarse_values = [f(proj, scan_cont, "tm", rate) for rate in rates]
    local_idx = _local_peak_indices(coarse_values)

    if log_file is not None:
        print_and_log(
            log_file,
            (
                f"# tm-cvar-local-scan proj={proj.proj_id} step={step:.6f} "
                f"points={len(rates)} local_peaks={len(local_idx)}"
            ),
        )

    best_cont: Optional[Contract] = None
    best_tcvar: Optional[float] = None

    for rank, idx in enumerate(local_idx, start=1):
        nu_local = rates[idx]
        left = max(0.0, nu_local - step)
        right = min(1.0, nu_local + step)

        local_cont = Contract("optcont", 0, 0, 0, "---")
        local_cont.type = "tm"
        nu_opt, _ = opt_contract_peakfinder(proj, local_cont, "tm", left, right)

        refined_cont, bcvar_opt, ocvar_opt, tcvar_opt = _build_tm_contract_for_rate(
            proj, nu_opt
        )

        if log_file is not None:
            print_and_log(
                log_file,
                (
                    f"# tm-cvar-neighborhood idx={rank} nu_local={nu_local:.6f} "
                    f"range=[{left:.6f},{right:.6f}] coarse_tcvar={coarse_values[idx]:.8f}"
                ),
            )
            print_and_log(
                log_file,
                (
                    f"# tm-cvar-refined idx={rank} nu_opt={refined_cont.rate:.8f} "
                    f"salary_opt={refined_cont.salary:.4f} reward={refined_cont.reward:.4f} "
                    f"b_cvar={bcvar_opt:.8f} o_cvar={ocvar_opt:.8f} t_cvar={tcvar_opt:.8f}"
                ),
            )

        if best_tcvar is None or _is_gt(tcvar_opt, best_tcvar):
            best_tcvar = tcvar_opt
            best_cont = refined_cont

    if best_cont is None or best_tcvar is None:
        best_cont, _, _, best_tcvar = _build_tm_contract_for_rate(proj, 0.0)

    if log_file is not None:
        bcvar_best, ocvar_best, _ = _cvar_components(proj, best_cont)
        print_and_log(
            log_file,
            (
                f"# tm-cvar-global-opt nu={best_cont.rate:.8f} salary={best_cont.salary:.4f} "
                f"reward={best_cont.reward:.4f} b_cvar={bcvar_best:.8f} "
                f"o_cvar={ocvar_best:.8f} t_cvar={best_tcvar:.8f}"
            ),
        )

    return best_tcvar, best_cont


def f(proj: Project, cont: Contract, contclass: str, x: float) -> float:
    if contclass == "tm":
        cont.rate = x
        smax = calc_salary(proj, proj.b_t_enpv, cont.rate, 0)
        smin = max(params.minSafeSalary, 0.01 * smax)
        _, best_tcvar = opt_contract_peakfinder(proj, cont, "lh", smin, smax)
        return best_tcvar
    elif contclass == "cp":
        cont.rate = x
    elif contclass == "lh":
        cont.salary = x
    else:
        raise ValueError("Invalid contract class. Choose 'cp', 'lh', or 'tm'.")

    cont.reward = calc_reward(proj, proj.b_t_enpv, cont.rate, cont.salary)
    cont.reward = max(0, cont.reward)
    _, _, tcvar = _cvar_components(proj, cont)
    return tcvar


def opt_contract_peakfinder(
    proj: Project, cont: Contract, contclass: str, x_min: float, x_max: float
) -> Tuple[float, float]:
    rp = params.roundPrecision
    if contclass == "lh":
        y_s0 = f(proj, cont, contclass, 0)
        y_smin = f(proj, cont, contclass, x_min)
        if precise_round(y_s0, rp) > precise_round(y_smin, rp):
            return 0, y_s0

    x_left = x_min
    x_right = x_max
    x_center = (x_left + x_right) / 2.0

    y_left = f(proj, cont, contclass, x_left)
    y_right = f(proj, cont, contclass, x_right)
    y_center = f(proj, cont, contclass, x_center)

    while (x_right - x_left) > params.ePrecision and min(
        precise_round(y_left, rp),
        precise_round(y_center, rp),
        precise_round(y_right, rp),
    ) < max(
        precise_round(y_left, rp),
        precise_round(y_center, rp),
        precise_round(y_right, rp),
    ):
        if precise_round(y_center, rp) >= precise_round(y_left, rp) and precise_round(
            y_center, rp
        ) >= precise_round(y_right, rp):
            x_right = x_center + (x_right - x_center) / 2.0
            x_left = x_center - (x_center - x_left) / 2.0
            y_right = f(proj, cont, contclass, x_right)
            y_left = f(proj, cont, contclass, x_left)
        elif precise_round(y_right, rp) >= precise_round(
            y_center, rp
        ) and precise_round(y_center, rp) >= precise_round(y_left, rp):
            if x_right >= x_max:
                x_left = x_center
                x_center = (x_right + x_left) / 2.0
                y_left = y_center
                y_center = f(proj, cont, contclass, x_center)
            else:
                x_left = x_center
                x_right = min(x_max, x_right + (x_right - x_center))
                x_center = (x_right + x_left) / 2.0
                y_left = y_center
                y_right = f(proj, cont, contclass, x_right)
                y_center = f(proj, cont, contclass, x_center)
        elif precise_round(y_left, rp) >= precise_round(y_center, rp) and precise_round(
            y_center, rp
        ) >= precise_round(y_right, rp):
            if precise_round(x_left, rp) <= precise_round(x_min, rp):
                x_right = x_center
                x_center = (x_right + x_left) / 2.0
                y_right = y_center
                y_center = f(proj, cont, contclass, x_center)
            else:
                x_right = x_center
                x_left = max(x_min, x_left - (x_center - x_left))
                x_center = (x_right + x_left) / 2.0
                y_right = y_center
                y_left = f(proj, cont, contclass, x_left)
                y_center = f(proj, cont, contclass, x_center)
        else:
            print("Unexpected behavior detected.")
            print(f"x_left: {x_left}, y_left: {y_left}")
            print(f"x_center: {x_center}, y_center: {y_center}")
            print(f"x_right: {x_right}, y_right: {y_right}")
            break

    return x_center, y_center


def opt_contract(
    proj: Project, contclass: str, log_file: Optional[TextIO] = None
) -> Tuple[float, Contract]:
    if contclass == "tm":
        return _opt_tm_contract_with_local_scan(proj, log_file)

    cont = Contract("optcont", 0, 0, 0, "---")
    cont.type = contclass
    if contclass == "cp":
        x_min = 0.0
        x_max = 1.0
    elif contclass == "lh":
        x_max = calc_salary(proj, proj.b_t_enpv, cont.rate, 0)
        x_min = max(params.minSafeSalary, 0.01 * x_max)
    else:
        raise ValueError("Invalid contract class. Choose 'cp', 'lh', or 'tm'.")

    x, y = opt_contract_peakfinder(proj, cont, contclass, x_min, x_max)
    if contclass == "cp":
        cont.rate = x
        cont.salary = 0
    elif contclass == "lh":
        cont.salary = x
        cont.rate = 0

    cont.reward = calc_reward(proj, proj.b_t_enpv, cont.rate, cont.salary)
    cont.reward = max(0, cont.reward)

    return y, cont


def opt_print(proj: Project, opt: bestContract):
    r = round
    rp = params.roundPrecision
    print(
        "\t".join(
            [
                str(proj.proj_id),
                str(r(opt.cont.rate, 4)),
                str(r(opt.cont.salary, 4)),
                str(r(opt.cont.reward, 4)),
                str(r(opt.tcvar, rp)),
            ]
        )
    )


def opt_cvar_search(proj: Project):
    log_file = opt_cvar_header()
    initialize(proj)

    exact_calculations(
        proj,
        proj.lsOpt.cont,
        proj.lsOpt.builder,
        proj.lsOpt.owner,
        0,
        calc_cvar=True,
    )
    proj.lsOpt.tvar = proj.lsOpt.builder.var + proj.lsOpt.owner.var
    proj.lsOpt.tcvar = proj.lsOpt.builder.cvar + proj.lsOpt.owner.cvar

    _, proj.cpOpt.cont = opt_contract(proj, "cp")
    params.isSim and simulate(proj, proj.cpOpt.cont, proj.cpOpt.sim_results, 0)
    exact_calculations(
        proj,
        proj.cpOpt.cont,
        proj.cpOpt.builder,
        proj.cpOpt.owner,
        0,
        calc_cvar=True,
    )
    proj.cpOpt.tvar = proj.cpOpt.builder.var + proj.cpOpt.owner.var
    proj.cpOpt.tcvar = proj.cpOpt.builder.cvar + proj.cpOpt.owner.cvar

    _, proj.lhOpt.cont = opt_contract(proj, "lh")
    params.isSim and simulate(proj, proj.lhOpt.cont, proj.lhOpt.sim_results, 0)
    exact_calculations(
        proj,
        proj.lhOpt.cont,
        proj.lhOpt.builder,
        proj.lhOpt.owner,
        0,
        calc_cvar=True,
    )
    proj.lhOpt.tvar = proj.lhOpt.builder.var + proj.lhOpt.owner.var
    proj.lhOpt.tcvar = proj.lhOpt.builder.cvar + proj.lhOpt.owner.cvar

    _, proj.tmOpt.cont = opt_contract(proj, "tm", log_file=log_file)
    params.isSim and simulate(proj, proj.tmOpt.cont, proj.tmOpt.sim_results, 0)
    exact_calculations(
        proj,
        proj.tmOpt.cont,
        proj.tmOpt.builder,
        proj.tmOpt.owner,
        0,
        calc_cvar=True,
    )
    proj.tmOpt.tvar = proj.tmOpt.builder.var + proj.tmOpt.owner.var
    proj.tmOpt.tcvar = proj.tmOpt.builder.cvar + proj.tmOpt.owner.cvar

    opt_cvar_report(proj, log_file)
