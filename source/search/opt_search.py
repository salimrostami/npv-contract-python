from typing import Tuple
from source.definit.contract import Contract, calc_salary, calc_reward
from source.definit.initialize import initialize
from source.definit.project import Project, bestContract
from source.evaluate.builder.builder_enpv import builder_enpv
from source.evaluate.owner.owner_enpv import owner_enpv
from source.evaluate.builder.builder_var import builder_var
from source.evaluate.owner.owner_var import owner_var
from source.definit.param import params
from source.utility.math_helpers import precise_round
from source.utility.report_writer import opt_header, opt_report
from source.evaluate.exact_eval import exact_calculations


def f(
    proj: Project,
    cont: Contract,
    contclass: str,
    x: float,
) -> float:
    if contclass == "tm":
        cont.reimburse_rate = x
        Smax = calc_salary(proj, proj.builder_target_enpv, cont.reimburse_rate, 0)
        Smin = min(params.minSafeSalary, 0.01 * Smax)
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
    cont.type = contclass
    if contclass == "cp" or contclass == "tm":
        x_min = 0.0
        x_max = 1.0
    elif contclass == "lh":
        x_max = calc_salary(proj, proj.builder_target_enpv, cont.reimburse_rate, 0)
        x_min = min(params.minSafeSalary, 0.01 * x_max)

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
        Smin = min(params.minSafeSalary, 0.01 * Smax)
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


def opt_print(proj: Project, cont: bestContract):
    print(
        "\t".join(
            [
                str(proj.proj_id),
                str(cont.contract.reimburse_rate),
                str(cont.contract.salary),
                str(cont.contract.reward),
                str(precise_round(cont.tvar, params.roundPrecision)),
            ]
        )
    )


def opt_search(proj: Project):
    log_file = opt_header()
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
    opt_print(proj, proj.lsOpt)
    proj.cpOpt.tvar, proj.cpOpt.contract = opt_contract(proj, "cp")
    exact_calculations(
        proj, proj.cpOpt.contract, proj.cpOpt.builder, proj.cpOpt.owner, 0
    )
    opt_print(proj, proj.cpOpt)
    proj.lhOpt.tvar, proj.lhOpt.contract = opt_contract(proj, "lh")
    exact_calculations(
        proj, proj.lhOpt.contract, proj.lhOpt.builder, proj.lhOpt.owner, 0
    )
    opt_print(proj, proj.lhOpt)
    proj.tmOpt.tvar, proj.tmOpt.contract = opt_contract(proj, "tm")
    exact_calculations(
        proj, proj.tmOpt.contract, proj.tmOpt.builder, proj.tmOpt.owner, 0
    )
    opt_print(proj, proj.tmOpt)
    opt_report(proj, log_file)
