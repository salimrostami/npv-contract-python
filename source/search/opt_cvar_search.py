from typing import Tuple
from source.definit.contract import Contract, calc_salary, calc_reward
from source.definit.initialize import initialize
from source.definit.project import Project, bestContract
from source.evaluate.builder.builder_cvar import builder_CVaR
from source.evaluate.owner.owner_cvar import owner_CVaR
from source.definit.param import params
from source.evaluate.simulation import simulate
from source.utility.math_helpers import precise_round
from source.utility.report_writer import opt_cvar_header, opt_cvar_report
from source.evaluate.exact_eval import exact_calculations
from source.evaluate.builder.builder_enpv import builder_enpv
from source.evaluate.owner.owner_enpv import owner_enpv


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

    benpv = builder_enpv(proj, cont)
    oenpv = owner_enpv(proj, cont)

    bcvar = builder_CVaR(proj, cont) - benpv
    ocvar = owner_CVaR(proj, cont) - oenpv

    return bcvar + ocvar


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


def opt_contract(proj: Project, contclass: str) -> Tuple[float, Contract]:
    cont = Contract("optcont", 0, 0, 0, "---")
    cont.type = contclass
    if contclass == "cp" or contclass == "tm":
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
    elif contclass == "tm":
        cont.rate = x
        smax = calc_salary(proj, proj.b_t_enpv, cont.rate, 0)
        smin = max(params.minSafeSalary, 0.01 * smax)
        cont.salary, _ = opt_contract_peakfinder(
            proj,
            cont,
            "lh",
            smin,
            smax,
        )

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
    proj.lsOpt.tcvar = proj.lsOpt.builder.cvar + proj.lsOpt.owner.cvar

    proj.cpOpt.tcvar, proj.cpOpt.cont = opt_contract(proj, "cp")
    params.isSim and simulate(proj, proj.cpOpt.cont, proj.cpOpt.sim_results, 0)
    exact_calculations(
        proj,
        proj.cpOpt.cont,
        proj.cpOpt.builder,
        proj.cpOpt.owner,
        0,
        calc_cvar=True,
    )

    proj.lhOpt.tcvar, proj.lhOpt.cont = opt_contract(proj, "lh")
    params.isSim and simulate(proj, proj.lhOpt.cont, proj.lhOpt.sim_results, 0)
    exact_calculations(
        proj,
        proj.lhOpt.cont,
        proj.lhOpt.builder,
        proj.lhOpt.owner,
        0,
        calc_cvar=True,
    )

    proj.tmOpt.tcvar, proj.tmOpt.cont = opt_contract(proj, "tm")
    params.isSim and simulate(proj, proj.tmOpt.cont, proj.tmOpt.sim_results, 0)
    exact_calculations(
        proj,
        proj.tmOpt.cont,
        proj.tmOpt.builder,
        proj.tmOpt.owner,
        0,
        calc_cvar=True,
    )

    opt_cvar_report(proj, log_file)
