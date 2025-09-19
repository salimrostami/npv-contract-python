from typing import Tuple
from contract import Contract
from project import Project
from contract import calc_reward
from builder_enpv import builder_enpv
from owner_enpv import owner_enpv
from builder_var import builder_var
from owner_var import owner_var


def f_cp(proj: Project, cont: Contract, target_b_enpv, distribution, x) -> float:
    cont.reimburse_rate = x
    cont.reward = round(calc_reward(proj, target_b_enpv, x, 0, distribution), 6)

    benpv = round(builder_enpv(proj, cont, distribution), 6)
    oenpv = round(owner_enpv(proj, cont, distribution), 6)

    bvar = round(builder_var(proj, cont, distribution, 0.05) - benpv, 7)
    ovar = round(owner_var(proj, cont, distribution, 0.05) - oenpv, 7)

    return bvar + ovar


def cp_opt_r(proj: Project, distribution, E: float) -> Tuple[float, float]:
    """
    Find the peak of a convex function f in the interval [x_min, x_max] using a binary-search-like
    approach.

    Args:
        f: The function to maximize (convex, single peak).
        x_min: The minimum x of the search interval.
        x_max: The maximum x of the search interval.
        E: The threshold below which we stop refining the interval.

    Returns:
        A tuple (x_peak, f_cp(x_peak)) where x_peak is the x-value at the peak and f_cp(x_peak) is
        the corresponding maximum y-value.
    """

    # Initial boundaries
    x_left = 0
    x_right = 1
    x_center = (x_left + x_right) / 2.0

    # Evaluate initial points
    cont = Contract(
        "optcp",
        0,
        0,
        0,
        "---",
    )
    y_center = f_cp(proj, cont, proj.builder_target_enpv, distribution, x_center)
    y_left = f_cp(proj, cont, proj.builder_target_enpv, distribution, x_left)
    y_right = f_cp(proj, cont, proj.builder_target_enpv, distribution, x_right)

    while (x_right - x_left) > E:
        # Check the slope and determine the direction
        if y_center > y_left and y_center > y_right:
            # Local maximum found at the center
            # Halve the interval: keep the left half
            x_right = x_center
            x_center = (x_left + x_center) / 2.0
            y_right = y_center  # since x_center is the new right boundary
            y_center = f_cp(
                proj, cont, proj.builder_target_enpv, distribution, x_center
            )  # re-eval center
        elif y_right > y_center:
            # Check if we are at the boundary and still going uphill
            if x_right >= 1 and y_right > y_center:
                return 1, y_right
            # Move right if it's uphill to the right
            x_left = x_center
            x_center = x_right
            x_right = min(1, x_center + (x_center - x_left))
            y_left = y_center
            y_center = y_right
            y_right = f_cp(
                proj, cont, proj.builder_target_enpv, distribution, x_right
            )  # re-eval right
        else:
            # Check if we are at the boundary and still going uphill
            if x_left <= 0 and y_left > y_center:
                return 0, y_left
            # Move left if it's uphill to the left
            x_right = x_center
            x_center = x_left
            x_left = max(0, x_center - (x_right - x_center))
            y_right = y_center
            y_center = y_left
            y_left = f_cp(
                proj, cont, proj.builder_target_enpv, distribution, x_left
            )  # re-eval left

    # After loop, the interval is smaller than E
    # Return the best found in the final interval
    # The peak is likely around the center
    return x_center, y_center
