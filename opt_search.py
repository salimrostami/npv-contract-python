from typing import Tuple
from contract import Contract, calc_salary
from initialize import initialize
from project import Project, projects
from contract import calc_reward
from builder_enpv import builder_enpv
from owner_enpv import owner_enpv
from builder_var import builder_var
from owner_var import owner_var

min_safe_salary = 12


def f(
    proj: Project,
    cont: Contract,
    distribution: str,
    contclass: str,
    x: float,
    E: float,
) -> float:
    if contclass == "tm":
        cont.reimburse_rate = x
        Smax = round(
            calc_salary(
                proj, proj.builder_target_enpv, cont.reimburse_rate, 0, distribution
            ),
            4,
        )
        Smin = min(min_safe_salary, 0.01 * Smax)
        _, best_tvar = opt_contract_peakfinder(
            proj,
            cont,
            distribution,
            "lh",
            Smin,
            Smax,
            E,
        )
        return best_tvar
    if contclass == "cp":
        cont.reimburse_rate = x
    if contclass == "lh":
        cont.salary = x

    cont.reward = round(
        calc_reward(
            proj,
            proj.builder_target_enpv,
            cont.reimburse_rate,
            cont.salary,
            distribution,
        ),
        6,
    )

    benpv = round(builder_enpv(proj, cont, distribution), 6)
    oenpv = round(owner_enpv(proj, cont, distribution), 6)

    bvar = round(builder_var(proj, cont, distribution, 0.05) - benpv, 7)
    ovar = round(owner_var(proj, cont, distribution, 0.05) - oenpv, 7)

    return bvar + ovar


def opt_contract_peakfinder(
    proj: Project,
    cont: Contract,
    distribution: str,
    contclass: str,
    x_min: float,
    x_max: float,
    E: float,
) -> Tuple[float, float]:

    # Initial boundaries
    x_left = x_min
    x_right = x_max
    x_center = (x_left + x_right) / 2.0
    # if contclass == "tm":
    #     x_center = 0.7891697883605957

    # Evaluate initial points
    y_left = f(proj, cont, distribution, contclass, x_left, E)
    y_right = f(proj, cont, distribution, contclass, x_right, E)
    y_center = f(proj, cont, distribution, contclass, x_center, E)

    while (x_right - x_left) > E and min(y_left, y_center, y_right) < max(
        y_left, y_center, y_right
    ):
        # Check the slope and determine the direction
        if y_center >= y_left and y_center >= y_right:
            # Local maximum found at the center
            # Halve the interval: keep the center half
            x_right = x_center + (x_right - x_center) / 2.0
            x_left = x_center - (x_center - x_left) / 2.0
            y_right = f(proj, cont, distribution, contclass, x_right, E)
            y_left = f(proj, cont, distribution, contclass, x_left, E)
        elif y_right >= y_center and y_center >= y_left:
            # Check if we are at the boundary and still going uphill
            if x_right >= x_max:
                x_left = x_center
                x_center = (x_right + x_left) / 2.0
                y_left = y_center
                y_center = f(proj, cont, distribution, contclass, x_center, E)
            # Move right if it's uphill to the right
            else:
                x_left = x_center
                x_right = min(x_max, x_right + (x_right - x_center))
                x_center = (x_right + x_left) / 2.0
                y_left = y_center
                y_right = f(
                    proj,
                    cont,
                    distribution,
                    contclass,
                    x_right,
                    E,
                )
                y_center = f(proj, cont, distribution, contclass, x_center, E)
        elif y_left >= y_center and y_center >= y_right:
            # Check if we are at the boundary and still going uphill
            if x_left <= x_min and y_left > y_center:
                x_right = x_center
                x_center = (x_right + x_left) / 2.0
                y_right = y_center
                y_center = f(proj, cont, distribution, contclass, x_center, E)
            # Move left if it's downhill to the right
            else:
                x_right = x_center
                x_left = max(x_min, x_left - (x_center - x_left))
                x_center = (x_right + x_left) / 2.0
                y_right = y_center
                y_left = f(proj, cont, distribution, contclass, x_left, E)
                y_center = f(proj, cont, distribution, contclass, x_center, E)
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
    distribution: str,
    contclass: str,
    E: float,
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
        x_max = round(
            calc_salary(
                proj, proj.builder_target_enpv, cont.reimburse_rate, 0, distribution
            ),
            4,
        )
        x_min = min(min_safe_salary, 0.01 * x_max)

    x, y = opt_contract_peakfinder(proj, cont, distribution, contclass, x_min, x_max, E)
    if contclass == "cp":
        cont.reimburse_rate = x
        cont.salary = 0
    elif contclass == "lh":
        cont.salary = x
        cont.reimburse_rate = 0
    elif contclass == "tm":
        cont.reimburse_rate = x
        Smax = round(
            calc_salary(
                proj, proj.builder_target_enpv, cont.reimburse_rate, 0, distribution
            ),
            4,
        )
        Smin = min(min_safe_salary, 0.01 * Smax)
        cont.salary, _ = opt_contract_peakfinder(
            proj,
            cont,
            distribution,
            "lh",
            Smin,
            Smax,
            E,
        )
    else:
        raise ValueError("Invalid contract class. Choose 'cp', 'lh', or 'tm'.")

    cont.reward = round(
        calc_reward(
            proj,
            proj.builder_target_enpv,
            cont.reimburse_rate,
            cont.salary,
            distribution,
        ),
        6,
    )

    return y, cont


def opt_search(distribution: str, E: float):
    proj: Project
    for proj in projects:
        initialize(proj, distribution)  # sets lsBase and owner_threshold
        proj.cpOpt.tvar, proj.cpOpt.contract = opt_contract(proj, distribution, "cp", E)
        print(
            (
                f"Project {proj.proj_id} optimized CP contract: "
                f"Reimburse Rate = {proj.cpOpt.contract.reimburse_rate}, "
                f"Salary = {proj.cpOpt.contract.salary}, "
                f"Reward = {proj.cpOpt.contract.reward}, "
                f"Total VaR = {proj.cpOpt.tvar}"
            )
        )
        proj.lhOpt.tvar, proj.lhOpt.contract = opt_contract(proj, distribution, "lh", E)
        print(
            (
                f"Project {proj.proj_id} optimized LH contract: "
                f"Reimburse Rate = {proj.lhOpt.contract.reimburse_rate}, "
                f"Salary = {proj.lhOpt.contract.salary}, "
                f"Reward = {proj.lhOpt.contract.reward}, "
                f"Total VaR = {proj.lhOpt.tvar}"
            )
        )
        proj.tmOpt.tvar, proj.tmOpt.contract = opt_contract(proj, distribution, "tm", E)
        print(
            (
                f"Project {proj.proj_id} optimized TM contract: "
                f"Reimburse Rate = {proj.tmOpt.contract.reimburse_rate}, "
                f"Salary = {proj.tmOpt.contract.salary}, "
                f"Reward = {proj.tmOpt.contract.reward}, "
                f"Total VaR = {proj.tmOpt.tvar}"
            )
        )
