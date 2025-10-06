from typing import Tuple
from source.definit.contract import Contract, calc_salary, calc_reward
from source.definit.initialize import initialize
from source.definit.project import Project, projects
from source.evaluate.builder.builder_enpv import builder_enpv
from source.evaluate.owner.owner_enpv import owner_enpv
from source.evaluate.builder.builder_var import builder_var
from source.evaluate.owner.owner_var import owner_var
import numpy as np
from source.definit.param import params
from source.utility.math_helpers import precise_round
from source.utility.report_writer import opt_header, opt_report
from source.evaluate.exact_eval import exact_calculations

min_safe_salary = 12


def f(
    proj: Project,
    cont: Contract,
    contclass: str,
    x: float,
) -> float:
    if contclass == "tm":
        cont.reimburse_rate = x
        Smax = calc_salary(proj, proj.builder_target_enpv, cont.reimburse_rate, 0)
        Smin = min(min_safe_salary, 0.01 * Smax)
        _, best_tvar = opt_contract_peakfinder(
            proj,
            cont,
            "lh",
            Smin,
            Smax,
        )
        return best_tvar
    elif contclass == "cp":
        cont.reimburse_rate = x
    elif contclass == "lh":
        cont.salary = x
    else:
        raise ValueError("Invalid contract class. Choose 'cp', 'lh', or 'tm'.")

    cont.reward = calc_reward(
        proj,
        proj.builder_target_enpv,
        cont.reimburse_rate,
        cont.salary,
    )

    benpv = builder_enpv(proj, cont)
    oenpv = owner_enpv(proj, cont)

    bvar = builder_var(proj, cont, 0.05) - benpv
    ovar = owner_var(proj, cont, 0.05) - oenpv

    return bvar + ovar


def opt_contract_peakfinder(
    proj: Project,
    cont: Contract,
    contclass: str,
    x_min: float,
    x_max: float,
) -> Tuple[float, float]:

    if contclass == "lh":
        y_s0 = f(proj, cont, contclass, 0)
        y_smin = f(proj, cont, contclass, x_min)
        if precise_round(y_s0, params.roundPrecision) > precise_round(
            y_smin, params.roundPrecision
        ):
            return 0, y_s0

    # Initial boundaries
    x_left = x_min
    x_right = x_max
    x_center = (x_left + x_right) / 2.0
    # if contclass == "tm":
    #     x_center = 0.7891697883605957

    # Evaluate initial points
    y_left = f(proj, cont, contclass, x_left)
    y_right = f(proj, cont, contclass, x_right)
    y_center = f(proj, cont, contclass, x_center)

    while (x_right - x_left) > params.ePrecision and min(
        precise_round(y_left, params.roundPrecision),
        precise_round(y_center, params.roundPrecision),
        precise_round(y_right, params.roundPrecision),
    ) < max(
        precise_round(y_left, params.roundPrecision),
        precise_round(y_center, params.roundPrecision),
        precise_round(y_right, params.roundPrecision),
    ):
        # Check the slope and determine the direction
        if precise_round(y_center, params.roundPrecision) >= precise_round(
            y_left, params.roundPrecision
        ) and precise_round(y_center, params.roundPrecision) >= precise_round(
            y_right, params.roundPrecision
        ):
            # Local maximum found at the center
            # Halve the interval: keep the center half
            x_right = x_center + (x_right - x_center) / 2.0
            x_left = x_center - (x_center - x_left) / 2.0
            y_right = f(proj, cont, contclass, x_right)
            y_left = f(proj, cont, contclass, x_left)
        elif precise_round(y_right, params.roundPrecision) >= precise_round(
            y_center, params.roundPrecision
        ) and precise_round(y_center, params.roundPrecision) >= precise_round(
            y_left, params.roundPrecision
        ):
            # uphill to the right
            # Check if we are at the boundary and still going uphill
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
                y_right = f(
                    proj,
                    cont,
                    contclass,
                    x_right,
                )
                y_center = f(proj, cont, contclass, x_center)
        elif precise_round(y_left, params.roundPrecision) >= precise_round(
            y_center, params.roundPrecision
        ) and precise_round(y_center, params.roundPrecision) >= precise_round(
            y_right, params.roundPrecision
        ):
            # downhill to the right
            # Check if we are at the boundary and still going uphill
            if precise_round(x_left, params.roundPrecision) <= precise_round(
                x_min, params.roundPrecision
            ):
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
            # This case should not happen if the function is well-behaved
            print("Unexpected behavior detected.")
            print(f"x_left: {x_left}, y_left: {y_left}")
            print(f"x_center: {x_center}, y_center: {y_center}")
            print(f"x_right: {x_right}, y_right: {y_right}")
            break

    # After loop, the interval is smaller than E
    # Return the best found in the final interval
    # The peak is likely around the center
    return x_center, y_center


def opt_contract(
    proj: Project,
    contclass: str,
) -> Tuple[float, Contract]:
    cont = Contract(
        "optcont",
        0,
        0,
        0,
        "---",
    )
    if contclass == "cp" or contclass == "tm":
        x_min = 0.0
        x_max = 1.0
    elif contclass == "lh":
        x_max = calc_salary(proj, proj.builder_target_enpv, cont.reimburse_rate, 0)
        x_min = min(min_safe_salary, 0.01 * x_max)

    x, y = opt_contract_peakfinder(proj, cont, contclass, x_min, x_max)
    if contclass == "cp":
        cont.reimburse_rate = x
        cont.salary = 0
    elif contclass == "lh":
        cont.salary = x
        cont.reimburse_rate = 0
    elif contclass == "tm":
        cont.reimburse_rate = x
        Smax = calc_salary(proj, proj.builder_target_enpv, cont.reimburse_rate, 0)
        Smin = min(min_safe_salary, 0.01 * Smax)
        cont.salary, _ = opt_contract_peakfinder(
            proj,
            cont,
            "lh",
            Smin,
            Smax,
        )
    else:
        raise ValueError("Invalid contract class. Choose 'cp', 'lh', or 'tm'.")

    cont.reward = calc_reward(
        proj,
        proj.builder_target_enpv,
        cont.reimburse_rate,
        cont.salary,
    )

    return y, cont


def opt_search():
    proj: Project
    log_file = opt_header()
    for proj in projects:
        initialize(proj)  # sets lsBase and owner_threshold
        # print headers
        header = [
            "proj_id",
            "cont_type",
            "reward",
            "reimburse_rate",
            "salary",
            "tvar",
        ]
        print("\t".join(header))
        # print optimization results
        print(
            "\t".join(
                [
                    str(proj.proj_id),
                    str(proj.lsOpt.contract.reimburse_rate),
                    str(proj.lsOpt.contract.salary),
                    str(proj.lsOpt.contract.reward),
                    str(precise_round(proj.lsOpt.tvar, params.roundPrecision)),
                ]
            )
        )
        proj.cpOpt.tvar, proj.cpOpt.contract = opt_contract(proj, "cp")
        exact_calculations(
            proj, proj.cpOpt.contract, proj.cpOpt.builder, proj.cpOpt.owner, 0
        )
        print(
            "\t".join(
                [
                    str(proj.proj_id),
                    str(proj.cpOpt.contract.reimburse_rate),
                    str(proj.cpOpt.contract.salary),
                    str(proj.cpOpt.contract.reward),
                    str(precise_round(proj.cpOpt.tvar, params.roundPrecision)),
                ]
            )
        )
        proj.lhOpt.tvar, proj.lhOpt.contract = opt_contract(proj, "lh")
        exact_calculations(
            proj, proj.lhOpt.contract, proj.lhOpt.builder, proj.lhOpt.owner, 0
        )
        print(
            "\t".join(
                [
                    str(proj.proj_id),
                    str(proj.lhOpt.contract.reimburse_rate),
                    str(proj.lhOpt.contract.salary),
                    str(proj.lhOpt.contract.reward),
                    str(precise_round(proj.lhOpt.tvar, params.roundPrecision)),
                ]
            )
        )
        proj.tmOpt.tvar, proj.tmOpt.contract = opt_contract(proj, "tm")
        exact_calculations(
            proj, proj.tmOpt.contract, proj.tmOpt.builder, proj.tmOpt.owner, 0
        )
        print(
            "\t".join(
                [
                    str(proj.proj_id),
                    str(proj.tmOpt.contract.reimburse_rate),
                    str(proj.tmOpt.contract.salary),
                    str(proj.tmOpt.contract.reward),
                    str(precise_round(proj.tmOpt.tvar, params.roundPrecision)),
                ]
            )
        )
    opt_report(proj, log_file)


def tm_sensitivity():
    proj: Project
    for proj in projects:
        initialize(proj)
        cont = Contract(
            "tm-sense",
            0,
            0,
            0,
            "tm-sense",
        )
        print(
            "nu",
            "Salary",
            "Reward",
            "TVaR",
            sep="\t",
        )
        for nu in np.arange(0.0, 1.009, 0.01):
            cont.reimburse_rate = nu
            Smax = calc_salary(proj, proj.builder_target_enpv, cont.reimburse_rate, 0)
            Smin = min(0.01 * Smax, min_safe_salary)
            best_salary, best_tvar = opt_contract_peakfinder(
                proj,
                cont,
                "lh",
                Smin,
                Smax,
            )
            best_R = calc_reward(
                proj,
                proj.builder_target_enpv,
                cont.reimburse_rate,
                best_salary,
            )
            print(
                f"{round(cont.reimburse_rate, 2)}",
                f"{best_salary}",
                f"{best_R}",
                f"{round(best_tvar, params.roundPrecision)}",
                sep="\t",
            )
