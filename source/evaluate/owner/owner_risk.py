import numpy as np
from source.utility.math_helpers import (
    build_interval,
    compute_lambert_w,
    get_common_interval,
)
from source.definit.project import Project
from source.definit.contract import Contract


def owner_calc_w_arg(project: Project, contract: Contract, x_ab, threshold_u):
    exp_arg = (
        project.discount_rate
        * (
            project.owner_income
            + contract.reimburse_rate * (x_ab + project.c_down_pay)
            - contract.reward
        )
        / contract.salary
    )
    # exp_result = np.exp(np.clip(exp_arg, -700, 700))
    exp_result = np.float64(np.exp(exp_arg))

    # limit = np.float64(1.0142320547350045e100)  # np.finfo(np.float64).max  # ~1.797e308
    # if abs(exp_result) > limit:
    #     exp_result = np.inf

    w_arg = np.float64(
        (project.discount_rate * threshold_u * exp_result / contract.salary)
    )

    return w_arg if w_arg != np.inf else np.finfo(np.float64).max


def owner_calc_eps_tau_w(project: Project, contract: Contract, x_ab, threshold_u):
    W_arg = owner_calc_w_arg(project, contract, x_ab, threshold_u)
    # You can change this to any value
    W0, W1 = compute_lambert_w(W_arg)
    Y = (
        project.owner_income
        + contract.reimburse_rate * (project.c_down_pay + x_ab)
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


def owner_calc_eps_tau_log(project: Project, contract: Contract, x_ab, threshold_u):
    log_arg = (
        project.owner_income
        + contract.reimburse_rate * (project.c_down_pay + x_ab)
        - contract.reward
    ) / threshold_u
    value = np.log(log_arg) / project.discount_rate if log_arg > 0 else None
    return value


def owner_calc_intervals(project: Project, contract: Contract, threshold_u):
    if threshold_u < 0:
        if contract.salary > 0:
            eps_0, eps_1 = owner_calc_eps_tau_w(
                project, contract, project.c_uni_high_a, threshold_u
            )
            tau_0, tau_1 = owner_calc_eps_tau_w(
                project, contract, project.c_uni_low_b, threshold_u
            )
        elif contract.salary == 0:
            eps_0 = 0
            tau_0 = 0
            eps_1 = owner_calc_eps_tau_log(
                project, contract, project.c_uni_high_a, threshold_u
            )
            tau_1 = owner_calc_eps_tau_log(
                project, contract, project.c_uni_low_b, threshold_u
            )
        else:
            raise ValueError(
                f"contract.salary: {contract.salary} must be a non-negative number."
            )
    elif threshold_u > 0:
        if contract.salary > 0:
            eps_0, eps_1 = owner_calc_eps_tau_w(
                project, contract, project.c_uni_high_a, threshold_u
            )
            tau_0, tau_1 = owner_calc_eps_tau_w(
                project, contract, project.c_uni_low_b, threshold_u
            )
        elif contract.salary == 0:
            eps_0 = owner_calc_eps_tau_log(
                project, contract, project.c_uni_high_a, threshold_u
            )
            tau_0 = owner_calc_eps_tau_log(
                project, contract, project.c_uni_low_b, threshold_u
            )
            eps_1 = None
            tau_1 = None
        else:
            raise ValueError(
                f"contract.salary: {contract.salary} must be a non-negative number."
            )
    elif threshold_u == 0:
        if contract.salary > 0:
            eps_0, eps_1 = owner_calc_eps_tau_w(
                project, contract, project.c_uni_high_a, threshold_u
            )
            tau_0, tau_1 = owner_calc_eps_tau_w(
                project, contract, project.c_uni_low_b, threshold_u
            )
    else:
        raise ValueError(
            f"unexpected number in threshold_u: {threshold_u} and "
            f"project.c_down_pay: {project.c_down_pay}",
        )

    if threshold_u < 0:
        L = (0, eps_0)
        ML = build_interval(eps_0, tau_0)
        MR = build_interval(tau_1, eps_1)
        R = (eps_1, float("inf"))
    elif threshold_u > 0:
        L = (0, eps_1)
        ML = build_interval(eps_1, tau_1)
        MR = build_interval(tau_0, eps_0)
        R = (eps_0, float("inf"))
    elif threshold_u == 0 and contract.salary == 0:
        L = (0, 0)
        ML = (0, float("inf"))
        MR = (None, None)
        R = (None, None)
    else:  # threshold_u == 0 and contract.salary > 0
        L = ML = MR = R = (None, None)

    return L, ML, MR, R


def owner_risk_expo_calc_integral(
    project: Project, contract: Contract, x_ab, threshold_u
):
    if project.discount_rate == project.d_expo_lambda:
        y = threshold_u * project.d_expo_lambda * x_ab
    else:
        y = (
            project.d_expo_lambda
            * threshold_u
            * np.exp((project.discount_rate - project.d_expo_lambda) * x_ab)
            / (project.discount_rate - project.d_expo_lambda)
        )
    return (
        1
        / (contract.reimburse_rate * (project.c_uni_low_b - project.c_uni_high_a))
        * (
            -y
            + (
                contract.salary
                * (1 + project.d_expo_lambda * x_ab)
                * np.exp(-project.d_expo_lambda * x_ab)
                / project.d_expo_lambda
            )
            - (
                project.owner_income
                + contract.reimburse_rate * (project.c_down_pay + project.c_uni_low_b)
                - contract.reward
            )
            * np.exp(-project.d_expo_lambda * x_ab)
        )
    )


def owner_risk_expo(project: Project, contract: Contract, threshold_u):
    eps0, eps1 = owner_calc_eps_tau_w(
        project, contract, project.c_uni_high_a, threshold_u
    )
    # print(f"eps0: {eps0}, eps1: {eps1}\n")
    risk = np.exp(-project.d_expo_lambda * eps0)
    if contract.reimburse_rate > 0:
        tau0, tau1 = owner_calc_eps_tau_w(
            project, contract, project.c_uni_low_b, threshold_u
        )
        # print(f"tau0: {tau0},tau1: {tau1}\n")
        risk += owner_risk_expo_calc_integral(
            project, contract, eps0, threshold_u
        ) - owner_risk_expo_calc_integral(project, contract, tau0, threshold_u)
    if contract.salary > 0:
        risk += 1 - np.exp(-project.d_expo_lambda * eps1)
        if contract.reimburse_rate > 0:
            risk += owner_risk_expo_calc_integral(
                project, contract, tau1, threshold_u
            ) - owner_risk_expo_calc_integral(project, contract, eps1, threshold_u)
    return risk


def owner_risk_uni_calc_integral(
    project: Project, contract: Contract, x_ab, threshold_u
):
    return (
        1
        / (
            contract.reimburse_rate
            * (project.c_uni_low_b - project.c_uni_high_a)
            * (project.d_uni_high_h - project.d_uni_low_l)
        )
        * (
            -threshold_u * np.exp(project.discount_rate * x_ab) / project.discount_rate
            - (contract.salary * x_ab**2 / 2)
            + (
                project.owner_income
                - contract.reward
                + contract.reimburse_rate * project.c_uni_low_b
                + contract.reimburse_rate * project.c_down_pay
            )
            * x_ab
        )
    )


def owner_risk_uni(project: Project, contract: Contract, threshold_u):
    if threshold_u == 0 and contract.salary == 0 and contract.reimburse_rate == 0:
        risk = 1 if project.owner_income < contract.reward else 0
    else:
        L, ML, MR, R = owner_calc_intervals(project, contract, threshold_u)
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
            risk += owner_risk_uni_calc_integral(
                project, contract, ML[1], threshold_u
            ) - owner_risk_uni_calc_integral(project, contract, ML[0], threshold_u)
        if MR[0] is not None and MR[1] is not None and MR[0] < MR[1]:
            risk += owner_risk_uni_calc_integral(
                project, contract, MR[1], threshold_u
            ) - owner_risk_uni_calc_integral(project, contract, MR[0], threshold_u)
        if R[0] is not None and R[1] is not None:
            risk += (R[1] - R[0]) / (project.d_uni_high_h - project.d_uni_low_l)

    return risk


def owner_risk(project: Project, contract: Contract, distribution, threshold_u):
    if distribution == "expo":
        return owner_risk_expo(project, contract, threshold_u)
    elif distribution == "uni":
        return owner_risk_uni(project, contract, threshold_u)
    else:
        raise ValueError("The 'distribution' argument must be either 'uni' or 'expo'.")
