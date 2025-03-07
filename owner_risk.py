import numpy as np
from math_helpers import compute_lambert_w, get_common_interval
from project import Project
from contract import Contract


def owner_calc_w_arg(project: Project, contract: Contract, x_ab, threshold_u):
    return float(
        (
            project.discount_rate
            * threshold_u
            * np.exp(
                project.discount_rate
                * (
                    project.owner_income
                    + contract.reimburse_rate * (x_ab + project.c_down_pay)
                    - contract.reward
                )
                / contract.salary
            )
            / contract.salary
        )
    )


def owner_calc_eps_tau(project: Project, contract: Contract, x_ab, threshold_u):
    if contract.salary == 0:
        log_arg = (
            project.owner_income
            + contract.reimburse_rate * (project.c_down_pay + x_ab)
            - contract.reward
        ) / threshold_u
        if log_arg > 0:
            Y0 = np.log(log_arg) / project.discount_rate
        else:
            Y0 = 0
        Y1 = 0
    else:
        W_arg = owner_calc_w_arg(project, contract, x_ab, threshold_u)
        # You can change this to any value
        W0, W1 = compute_lambert_w(W_arg)
        Y = (
            project.owner_income
            + contract.reimburse_rate * (project.c_down_pay + x_ab)
            - contract.reward
        ) / contract.salary
        if W0:
            # print(f"W_0({W_arg}) = {W0}")
            Y0 = max(Y - (float(np.real(W0)) / project.discount_rate), 0)
        else:
            # print(f"W_{{0}} is not defined for {W_arg}\n")
            Y0 = 0
        if W1:
            # print(f"W_{{-1}}({W_arg}) = {W1}\n")
            Y1 = max(Y - (float(np.real(W1)) / project.discount_rate), 0)
        else:
            # print(f"W_{{-1}} is not defined for {W_arg}\n")
            Y1 = 0
    return Y0, Y1


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
    eps0, eps1 = owner_calc_eps_tau(
        project, contract, project.c_uni_high_a, threshold_u
    )
    # print(f"eps0: {eps0}, eps1: {eps1}\n")
    risk = np.exp(-project.d_expo_lambda * eps0)
    if contract.reimburse_rate > 0:
        tau0, tau1 = owner_calc_eps_tau(
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
    eps0, eps1 = owner_calc_eps_tau(
        project, contract, project.c_uni_high_a, threshold_u
    )
    tau0, tau1 = owner_calc_eps_tau(project, contract, project.c_uni_low_b, threshold_u)
    # print(f"alpha0: {alpha0}, alpha1: {alpha1}")
    # print(f"beta0: {beta0},beta1: {beta1}\n")
    Emin, Emax = get_common_interval(
        (project.d_uni_low_l, project.d_uni_high_h), (eps1, tau1)
    )
    Tmin, Tmax = get_common_interval(
        (project.d_uni_low_l, project.d_uni_high_h), (tau0, eps0)
    )
    EM1, EM2 = get_common_interval(
        (project.d_uni_low_l, project.d_uni_high_h), (0, eps1)
    )
    TP1, TP2 = get_common_interval(
        (project.d_uni_low_l, project.d_uni_high_h), (eps0, float("inf"))
    )
    # print(
    #     f"Emin: {Emin}, Emax: {Emax}, Tmin: {Tmin}, Tmax: {Tmax}, "
    #     f"EM1: {EM1}, EM2: {EM2}, TP1: {TP1}, TP2: {TP2}\n"
    # )
    if TP2 and TP1:
        risk = (TP2 - TP1) / (project.d_uni_high_h - project.d_uni_low_l)
    else:  # HP2 is None
        risk = 0
    if contract.reimburse_rate > 0 and Tmax and Tmin:
        risk += owner_risk_uni_calc_integral(
            project, contract, Tmax, threshold_u
        ) - owner_risk_uni_calc_integral(project, contract, Tmin, threshold_u)
    if contract.salary > 0:
        if EM2 and EM1:
            risk += (EM2 - EM1) / (project.d_uni_high_h - project.d_uni_low_l)
        if contract.reimburse_rate > 0 and Emax and Emin:
            risk += owner_risk_uni_calc_integral(
                project, contract, Emax, threshold_u
            ) - owner_risk_uni_calc_integral(project, contract, Emin, threshold_u)
    return risk


def owner_risk(project: Project, contract: Contract, distribution, threshold_u):
    if distribution == "expo":
        return owner_risk_expo(project, contract, threshold_u)
    elif distribution == "uni":
        return owner_risk_uni(project, contract, threshold_u)
    else:
        raise ValueError("The 'distribution' argument must be either 'uni' or 'expo'.")
