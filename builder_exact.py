import numpy as np
from math_helpers import compute_lambert_w, get_common_interval
from project import Project
from contract import Contract


def builder_enpv_expo(
    project: Project,
    contract: Contract,
):
    return (
        project.c_down_pay
        + (
            contract.reward
            - contract.reimburse_rate * project.c_down_pay
            + (1 - contract.reimburse_rate)
            * (project.c_uni_high_a + project.c_uni_low_b)
            / 2
        )
        * (project.d_expo_lambda / (project.d_expo_lambda + project.discount_rate))
        + (
            +(contract.salary * project.d_expo_lambda)
            / (project.d_expo_lambda + project.discount_rate) ** 2
        )
    )


def builder_enpv_uni(
    project: Project,
    contract: Contract,
):
    return (
        project.c_down_pay
        + (
            contract.reward
            - contract.reimburse_rate * project.c_down_pay
            + (1 - contract.reimburse_rate)
            * (project.c_uni_high_a + project.c_uni_low_b)
            / 2
        )
        * (
            np.exp(-project.discount_rate * project.d_uni_high_h)
            - np.exp(-project.discount_rate * project.d_uni_low_l)
        )
        / (project.discount_rate * (project.d_uni_low_l - project.d_uni_high_h))
        + (
            contract.salary
            * (
                np.exp(-project.discount_rate * project.d_uni_high_h)
                * (project.discount_rate * project.d_uni_high_h + 1)
                - np.exp(-project.discount_rate * project.d_uni_low_l)
                * (project.discount_rate * project.d_uni_low_l + 1)
            )
            / (
                (project.discount_rate**2)
                * (project.d_uni_low_l - project.d_uni_high_h)
            )
        )
    )


def builder_enpv(project: Project, contract: Contract, distribution):
    if distribution == "expo":
        return builder_enpv_expo(project, contract)
    elif distribution == "uni":
        return builder_enpv_uni(project, contract)
    else:
        raise ValueError("The 'distribution' argument must be either 'uni' or 'expo'.")


def builder_calc_w_arg(project: Project, contract: Contract, x):
    return float(
        (
            project.discount_rate
            * (project.c_down_pay - project.builder_threshold)
            / (
                contract.salary
                * np.exp(
                    project.discount_rate
                    * (
                        (1 - contract.reimburse_rate) * x
                        - contract.reimburse_rate * project.c_down_pay
                        + contract.reward
                    )
                    / contract.salary
                )
            )
        )
    )


def builder_calc_alpha_beta(project: Project, contract: Contract, x):
    if contract.salary == 0:
        log_arg = (
            contract.reward
            - contract.reimburse_rate * project.c_down_pay
            + (1 - contract.reimburse_rate) * x
        ) / (project.builder_threshold - project.c_down_pay)
        if log_arg > 0:
            Y1 = np.log(log_arg) / project.discount_rate
        else:
            Y1 = 0
        Y0 = 0
    else:
        W_arg = builder_calc_w_arg(project, contract, x)
        # You can change this to any value
        W0, W1 = compute_lambert_w(W_arg)
        Y = (
            contract.reimburse_rate * project.c_down_pay
            - (1 - contract.reimburse_rate) * x
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


def builder_risk_expo_calc_integral(project: Project, contract: Contract, x):
    if project.discount_rate == project.d_expo_lambda:
        y = (project.c_down_pay - project.builder_threshold) * project.d_expo_lambda * x
    else:
        y = (
            project.d_expo_lambda
            * (project.c_down_pay - project.builder_threshold)
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


def builder_risk_expo(project: Project, contract: Contract):
    alpha0, alpha1 = builder_calc_alpha_beta(project, contract, project.c_uni_high_a)
    # print(f"alpha0: {alpha0}, alpha1: {alpha1}\n")
    risk = np.exp(-project.d_expo_lambda * alpha1)
    if contract.reimburse_rate < 1:
        beta0, beta1 = builder_calc_alpha_beta(project, contract, project.c_uni_low_b)
        # print(f"beta0: {beta0},beta1: {beta1}\n")
        risk += builder_risk_expo_calc_integral(
            project, contract, alpha1
        ) - builder_risk_expo_calc_integral(project, contract, beta1)
    if contract.salary > 0:
        risk += 1 - np.exp(-project.d_expo_lambda * alpha0)
        if contract.reimburse_rate < 1:
            risk += builder_risk_expo_calc_integral(
                project, contract, beta0
            ) - builder_risk_expo_calc_integral(project, contract, alpha0)
    return risk


def builder_risk_uni_calc_integral(project: Project, contract: Contract, x):
    return (
        1
        / (
            (1 - contract.reimburse_rate)
            * (project.c_uni_low_b - project.c_uni_high_a)
            * (project.d_uni_high_h - project.d_uni_low_l)
        )
        * (
            (project.c_down_pay - project.builder_threshold)
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


def builder_risk_uni(project: Project, contract: Contract):
    alpha0, alpha1 = builder_calc_alpha_beta(project, contract, project.c_uni_high_a)
    beta0, beta1 = builder_calc_alpha_beta(project, contract, project.c_uni_low_b)
    # print(f"alpha0: {alpha0}, alpha1: {alpha1}")
    # print(f"beta0: {beta0},beta1: {beta1}\n")
    Lmin, Lmax = get_common_interval(
        (project.d_uni_low_l, project.d_uni_high_h), (alpha0, beta0)
    )
    Hmin, Hmax = get_common_interval(
        (project.d_uni_low_l, project.d_uni_high_h), (beta1, alpha1)
    )
    LM1, LM2 = get_common_interval(
        (project.d_uni_low_l, project.d_uni_high_h), (0, alpha0)
    )
    HP1, HP2 = get_common_interval(
        (project.d_uni_low_l, project.d_uni_high_h), (alpha1, float("inf"))
    )
    # print(
    #     f"Lmin: {Lmin}, Lmax: {Lmax}, Hmin: {Hmin}, Hmax: {Hmax}, "
    #     f"LM1: {LM1}, LM2: {LM2}, HP1: {HP1}, HP2: {HP2}\n"
    # )
    if HP2 and HP1:
        risk = (HP2 - HP1) / (project.d_uni_high_h - project.d_uni_low_l)
    else:  # HP2 is None
        risk = 0
    if contract.reimburse_rate < 1 and Hmax and Hmin:
        risk += builder_risk_uni_calc_integral(
            project, contract, Hmax
        ) - builder_risk_uni_calc_integral(project, contract, Hmin)
    if contract.salary > 0:
        if LM2 and LM1:
            risk += (LM2 - LM1) / (project.d_uni_high_h - project.d_uni_low_l)
        if contract.reimburse_rate < 1 and Lmax and Lmin:
            risk += builder_risk_uni_calc_integral(
                project, contract, Lmax
            ) - builder_risk_uni_calc_integral(project, contract, Lmin)
    return risk


def builder_risk(project: Project, contract: Contract, distribution):
    if distribution == "expo":
        return builder_risk_expo(project, contract)
    elif distribution == "uni":
        return builder_risk_uni(project, contract)
    else:
        raise ValueError("The 'distribution' argument must be either 'uni' or 'expo'.")
