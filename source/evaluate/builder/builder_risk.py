import numpy as np
from source.utility.math_helpers import (
    build_interval,
    compute_lambert_w,
    get_common_interval,
)
from source.definit.project import Project
from source.definit.contract import Contract
from source.definit.param import params


def builder_calc_w_arg(proj: Project, cont: Contract, x, threshold_u):
    exp_arg = (
        proj.discount_rate
        * ((1 - cont.rate) * x - cont.rate * proj.c_down_pay + cont.reward)
        / cont.salary
    )
    exp_result = np.float64(np.exp(exp_arg))

    # limit = np.finfo(float).max  # ~1.797e308
    # if abs(exp_arg) > limit:
    #     print("Too large!")

    w_arg = np.float64(
        (
            proj.discount_rate
            * (proj.c_down_pay - threshold_u)
            / (cont.salary * exp_result)
        )
    )

    return w_arg if w_arg != np.inf else np.finfo(np.float64).max


def builder_calc_alpha_beta_w(proj: Project, cont: Contract, x, threshold_u):
    W_arg = builder_calc_w_arg(proj, cont, x, threshold_u)
    W0, W1 = compute_lambert_w(W_arg)
    Y = (cont.rate * proj.c_down_pay - (1 - cont.rate) * x - cont.reward) / cont.salary
    if W0 is not None:
        # print(f"W_0({W_arg}) = {W0}")
        Y0 = max(Y - (float(np.real(W0)) / proj.discount_rate), 0)
    else:
        # print(f"W_{{0}} is not defined for {W_arg}\n")
        Y0 = None
    if W1 is not None:
        # print(f"W_{{-1}}({W_arg}) = {W1}\n")
        Y1 = max(Y - (float(np.real(W1)) / proj.discount_rate), 0)
    else:
        # print(f"W_{{-1}} is not defined for {W_arg}\n")
        Y1 = None
    return Y0, Y1


def builder_calc_alpha_beta_log(proj: Project, cont: Contract, x, threshold_u):
    log_arg = (cont.reward - cont.rate * proj.c_down_pay + (1 - cont.rate) * x) / (
        threshold_u - proj.c_down_pay
    )
    value = np.log(log_arg) / proj.discount_rate if log_arg > 0 else None
    return value


def builder_calc_intervals(proj: Project, cont: Contract, threshold_u):
    if threshold_u > proj.c_down_pay:
        if cont.salary > 0:
            alpha_0, alpha_1 = builder_calc_alpha_beta_w(
                proj, cont, proj.c_high_a, threshold_u
            )
            beta_0, beta_1 = builder_calc_alpha_beta_w(
                proj, cont, proj.c_low_b, threshold_u
            )
        elif cont.salary == 0:
            alpha_0 = 0
            beta_0 = 0
            alpha_1 = builder_calc_alpha_beta_log(
                proj, cont, proj.c_high_a, threshold_u
            )
            beta_1 = builder_calc_alpha_beta_log(proj, cont, proj.c_low_b, threshold_u)
        else:
            raise ValueError(
                f"cont.salary: {cont.salary} must be a non-negative number."
            )
    elif threshold_u < proj.c_down_pay:
        if cont.salary > 0:
            alpha_0, alpha_1 = builder_calc_alpha_beta_w(
                proj, cont, proj.c_high_a, threshold_u
            )
            beta_0, beta_1 = builder_calc_alpha_beta_w(
                proj, cont, proj.c_low_b, threshold_u
            )
        elif cont.salary == 0:
            alpha_0 = builder_calc_alpha_beta_log(
                proj, cont, proj.c_high_a, threshold_u
            )
            beta_0 = builder_calc_alpha_beta_log(proj, cont, proj.c_low_b, threshold_u)
            alpha_1 = None
            beta_1 = None
        else:
            raise ValueError(
                f"cont.salary: {cont.salary} must be a non-negative number."
            )
    elif threshold_u == proj.c_down_pay:
        if cont.salary > 0:
            alpha_0, alpha_1 = builder_calc_alpha_beta_w(
                proj, cont, proj.c_high_a, threshold_u
            )
            beta_0, beta_1 = builder_calc_alpha_beta_w(
                proj, cont, proj.c_low_b, threshold_u
            )
    else:
        raise ValueError(
            f"unexpected number in threshold_u: {threshold_u} and "
            f"proj.c_down_pay: {proj.c_down_pay}",
        )

    if threshold_u == proj.c_down_pay and cont.salary == 0:
        L = (0, 0)
        ML = (0, float("inf"))
        MR = (None, None)
        R = (None, None)
    else:
        L = (0, alpha_0)
        ML = build_interval(alpha_0, beta_0)
        MR = build_interval(beta_1, alpha_1)
        R = (alpha_1, float("inf"))

    if (
        L == (None, None)
        and ML == (None, None)
        and MR == (None, None)
        and R == (None, None)
    ):
        raise ValueError("None of the intervals is defined.")

    return L, ML, MR, R


def builder_risk_expo_calc_integral(proj: Project, cont: Contract, x, threshold_u):
    if proj.discount_rate == proj.d_lambda:
        y = (proj.c_down_pay - threshold_u) * proj.d_lambda * x
    else:
        y = (
            proj.d_lambda
            * (proj.c_down_pay - threshold_u)
            * np.exp((proj.discount_rate - proj.d_lambda) * x)
            / (proj.discount_rate - proj.d_lambda)
        )
    return (
        1
        / ((1 - cont.rate) * (proj.c_low_b - proj.c_high_a))
        * (
            y
            - (
                cont.salary
                * (1 + proj.d_lambda * x)
                * np.exp(-proj.d_lambda * x)
                / proj.d_lambda
            )
            - (
                cont.reward
                - cont.rate * proj.c_down_pay
                + (1 - cont.rate) * proj.c_low_b
            )
            * np.exp(-proj.d_lambda * x)
        )
    )


def builder_risk_expo(proj: Project, cont: Contract, threshold_u):
    alpha0, alpha1 = builder_calc_alpha_beta_w(proj, cont, proj.c_high_a, threshold_u)
    # print(f"alpha0: {alpha0}, alpha1: {alpha1}\n")
    if alpha1:
        risk = np.exp(-proj.d_lambda * alpha1)
    else:
        risk = 0
    if cont.rate < 1:
        beta0, beta1 = builder_calc_alpha_beta_w(proj, cont, proj.c_low_b, threshold_u)
        if beta1 is None:
            beta1 = 0
        # print(f"beta0: {beta0},beta1: {beta1}\n")
        if alpha1 and beta1:
            risk += builder_risk_expo_calc_integral(
                proj, cont, alpha1, threshold_u
            ) - builder_risk_expo_calc_integral(proj, cont, beta1, threshold_u)
    if cont.salary > 0 and alpha0:
        risk += 1 - np.exp(-proj.d_lambda * alpha0)
        if cont.rate < 1 and beta0:
            risk += builder_risk_expo_calc_integral(
                proj, cont, beta0, threshold_u
            ) - builder_risk_expo_calc_integral(proj, cont, alpha0, threshold_u)
    return risk


def builder_risk_uni_calc_integral(proj: Project, cont: Contract, x, threshold_u):
    return (
        1
        / (
            (1 - cont.rate)
            * (proj.c_low_b - proj.c_high_a)
            * (proj.d_high_h - proj.d_low_l)
        )
        * (
            (proj.c_down_pay - threshold_u)
            * np.exp(proj.discount_rate * x)
            / proj.discount_rate
            + (cont.salary * x**2 / 2)
            + (
                cont.reward
                + (1 - cont.rate) * proj.c_low_b
                - cont.rate * proj.c_down_pay
            )
            * x
        )
    )


def builder_risk_uni(proj: Project, cont: Contract, threshold_u):
    if threshold_u == proj.c_down_pay and cont.salary == 0 and cont.rate == 1:
        risk = 1 if cont.reward < cont.rate * proj.c_down_pay else 0
    else:
        L, ML, MR, R = builder_calc_intervals(proj, cont, threshold_u)
        common_range = (proj.d_low_l, proj.d_high_h)
        L = get_common_interval(common_range, L)
        ML = get_common_interval(common_range, ML)
        MR = get_common_interval(common_range, MR)
        R = get_common_interval(common_range, R)
        if L[0] is not None and L[1] is not None:
            risk = (L[1] - L[0]) / (proj.d_high_h - proj.d_low_l)
        else:
            risk = 0
        if ML[0] is not None and ML[1] is not None and ML[0] < ML[1]:
            risk += builder_risk_uni_calc_integral(
                proj, cont, ML[1], threshold_u
            ) - builder_risk_uni_calc_integral(proj, cont, ML[0], threshold_u)
        if MR[0] is not None and MR[1] is not None and MR[0] < MR[1]:
            risk += builder_risk_uni_calc_integral(
                proj, cont, MR[1], threshold_u
            ) - builder_risk_uni_calc_integral(proj, cont, MR[0], threshold_u)
        if R[0] is not None and R[1] is not None:
            risk += (R[1] - R[0]) / (proj.d_high_h - proj.d_low_l)

    return risk


def builder_risk(proj: Project, cont: Contract, threshold_u):
    if params.dist == "expo":
        return builder_risk_expo(proj, cont, threshold_u)
    elif params.dist == "uni":
        return builder_risk_uni(proj, cont, threshold_u)
    else:
        raise ValueError("The 'distribution' argument must be either 'uni' or 'expo'.")
