import numpy as np
from math_helpers import build_interval, compute_lambert_w, get_common_interval
from project import Project
from contract import Contract


def builder_calc_w_arg(project: Project, contract: Contract, x, threshold_u):
    exp_arg = (
        project.discount_rate
        * (
            (1 - contract.reimburse_rate) * x
            - contract.reimburse_rate * project.c_down_pay
            + contract.reward
        )
        / contract.salary
    )
    exp_result = np.float64(np.exp(exp_arg))

    # limit = np.finfo(float).max  # ~1.797e308
    # if abs(exp_arg) > limit:
    #     print("Too large!")

    w_arg = np.float64(
        (
            project.discount_rate
            * (project.c_down_pay - threshold_u)
            / (contract.salary * exp_result)
        )
    )

    return w_arg if w_arg != np.inf else np.finfo(np.float64).max


def builder_calc_alpha_beta_w(project: Project, contract: Contract, x, threshold_u):
    W_arg = builder_calc_w_arg(project, contract, x, threshold_u)
    W0, W1 = compute_lambert_w(W_arg)
    Y = (
        contract.reimburse_rate * project.c_down_pay
        - (1 - contract.reimburse_rate) * x
        - contract.reward
    ) / contract.salary
    if W0 is not None:
        # print(f"W_0({W_arg}) = {W0}")
        Y0 = max(Y - (float(np.real(W0)) / project.discount_rate), 0)
    else:
        # print(f"W_{{0}} is not defined for {W_arg}\n")
        Y0 = None
    if W1 is not None:
        # print(f"W_{{-1}}({W_arg}) = {W1}\n")
        Y1 = max(Y - (float(np.real(W1)) / project.discount_rate), 0)
    else:
        # print(f"W_{{-1}} is not defined for {W_arg}\n")
        Y1 = None
    return Y0, Y1


def builder_calc_alpha_beta_log(project: Project, contract: Contract, x, threshold_u):
    log_arg = (
        contract.reward
        - contract.reimburse_rate * project.c_down_pay
        + (1 - contract.reimburse_rate) * x
    ) / (threshold_u - project.c_down_pay)
    value = np.log(log_arg) / project.discount_rate if log_arg > 0 else None
    return value


def builder_calc_intervals(project: Project, contract: Contract, threshold_u):
    if threshold_u > project.c_down_pay:
        if contract.salary > 0:
            alpha_0, alpha_1 = builder_calc_alpha_beta_w(
                project, contract, project.c_uni_high_a, threshold_u
            )
            beta_0, beta_1 = builder_calc_alpha_beta_w(
                project, contract, project.c_uni_low_b, threshold_u
            )
        elif contract.salary == 0:
            alpha_0 = 0
            beta_0 = 0
            alpha_1 = builder_calc_alpha_beta_log(
                project, contract, project.c_uni_high_a, threshold_u
            )
            beta_1 = builder_calc_alpha_beta_log(
                project, contract, project.c_uni_low_b, threshold_u
            )
        else:
            raise ValueError(
                f"contract.salary: {contract.salary} must be a non-negative number."
            )
    elif threshold_u < project.c_down_pay:
        if contract.salary > 0:
            alpha_0, alpha_1 = builder_calc_alpha_beta_w(
                project, contract, project.c_uni_high_a, threshold_u
            )
            beta_0, beta_1 = builder_calc_alpha_beta_w(
                project, contract, project.c_uni_low_b, threshold_u
            )
        elif contract.salary == 0:
            alpha_0 = builder_calc_alpha_beta_log(
                project, contract, project.c_uni_high_a, threshold_u
            )
            beta_0 = builder_calc_alpha_beta_log(
                project, contract, project.c_uni_low_b, threshold_u
            )
            alpha_1 = None
            beta_1 = None
        else:
            raise ValueError(
                f"contract.salary: {contract.salary} must be a non-negative number."
            )
    elif threshold_u == project.c_down_pay:
        if contract.salary > 0:
            alpha_0, alpha_1 = builder_calc_alpha_beta_w(
                project, contract, project.c_uni_high_a, threshold_u
            )
            beta_0, beta_1 = builder_calc_alpha_beta_w(
                project, contract, project.c_uni_low_b, threshold_u
            )
    else:
        raise ValueError(
            f"unexpected number in threshold_u: {threshold_u} and "
            f"project.c_down_pay: {project.c_down_pay}",
        )

    if threshold_u == project.c_down_pay and contract.salary == 0:
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


def builder_risk_expo_calc_integral(
    project: Project, contract: Contract, x, threshold_u
):
    if project.discount_rate == project.d_expo_lambda:
        y = (project.c_down_pay - threshold_u) * project.d_expo_lambda * x
    else:
        y = (
            project.d_expo_lambda
            * (project.c_down_pay - threshold_u)
            * np.exp((project.discount_rate - project.d_expo_lambda) * x)
            / (project.discount_rate - project.d_expo_lambda)
        )
    return (
        1
        / ((1 - contract.reimburse_rate) * (project.c_uni_low_b - project.c_uni_high_a))
        * (
            y
            - (
                contract.salary
                * (1 + project.d_expo_lambda * x)
                * np.exp(-project.d_expo_lambda * x)
                / project.d_expo_lambda
            )
            - (
                contract.reward
                - contract.reimburse_rate * project.c_down_pay
                + (1 - contract.reimburse_rate) * project.c_uni_low_b
            )
            * np.exp(-project.d_expo_lambda * x)
        )
    )


def builder_risk_expo(project: Project, contract: Contract, threshold_u):
    alpha0, alpha1 = builder_calc_alpha_beta_w(
        project, contract, project.c_uni_high_a, threshold_u
    )
    # print(f"alpha0: {alpha0}, alpha1: {alpha1}\n")
    if alpha1:
        risk = np.exp(-project.d_expo_lambda * alpha1)
    else:
        risk = 0
    if contract.reimburse_rate < 1:
        beta0, beta1 = builder_calc_alpha_beta_w(
            project, contract, project.c_uni_low_b, threshold_u
        )
        if beta1 is None:
            beta1 = 0
        # print(f"beta0: {beta0},beta1: {beta1}\n")
        if alpha1 and beta1:
            risk += builder_risk_expo_calc_integral(
                project, contract, alpha1, threshold_u
            ) - builder_risk_expo_calc_integral(project, contract, beta1, threshold_u)
    if contract.salary > 0 and alpha0:
        risk += 1 - np.exp(-project.d_expo_lambda * alpha0)
        if contract.reimburse_rate < 1 and beta0:
            risk += builder_risk_expo_calc_integral(
                project, contract, beta0, threshold_u
            ) - builder_risk_expo_calc_integral(project, contract, alpha0, threshold_u)
    return risk


def builder_risk_uni_calc_integral(
    project: Project, contract: Contract, x, threshold_u
):
    return (
        1
        / (
            (1 - contract.reimburse_rate)
            * (project.c_uni_low_b - project.c_uni_high_a)
            * (project.d_uni_high_h - project.d_uni_low_l)
        )
        * (
            (project.c_down_pay - threshold_u)
            * np.exp(project.discount_rate * x)
            / project.discount_rate
            + (contract.salary * x**2 / 2)
            + (
                contract.reward
                + (1 - contract.reimburse_rate) * project.c_uni_low_b
                - contract.reimburse_rate * project.c_down_pay
            )
            * x
        )
    )


def builder_risk_uni(project: Project, contract: Contract, threshold_u):
    if (
        threshold_u == project.c_down_pay
        and contract.salary == 0
        and contract.reimburse_rate == 1
    ):
        risk = (
            1 if contract.reward < contract.reimburse_rate * project.c_down_pay else 0
        )
    else:
        L, ML, MR, R = builder_calc_intervals(project, contract, threshold_u)
        common_range = (project.d_uni_low_l, project.d_uni_high_h)
        L = get_common_interval(common_range, L)
        ML = get_common_interval(common_range, ML)
        MR = get_common_interval(common_range, MR)
        R = get_common_interval(common_range, R)
        if L[0] is not None and L[1] is not None:
            risk = (L[1] - L[0]) / (project.d_uni_high_h - project.d_uni_low_l)
        else:
            risk = 0
        if ML[0] is not None and ML[1] is not None and ML[0] < ML[1]:
            risk += builder_risk_uni_calc_integral(
                project, contract, ML[1], threshold_u
            ) - builder_risk_uni_calc_integral(project, contract, ML[0], threshold_u)
        if MR[0] is not None and MR[1] is not None and MR[0] < MR[1]:
            risk += builder_risk_uni_calc_integral(
                project, contract, MR[1], threshold_u
            ) - builder_risk_uni_calc_integral(project, contract, MR[0], threshold_u)
        if R[0] is not None and R[1] is not None:
            risk += (R[1] - R[0]) / (project.d_uni_high_h - project.d_uni_low_l)

    return risk


def builder_risk(project: Project, contract: Contract, distribution, threshold_u):
    if distribution == "expo":
        return builder_risk_expo(project, contract, threshold_u)
    elif distribution == "uni":
        return builder_risk_uni(project, contract, threshold_u)
    else:
        raise ValueError("The 'distribution' argument must be either 'uni' or 'expo'.")
