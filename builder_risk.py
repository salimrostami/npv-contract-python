import numpy as np
from math_helpers import compute_lambert_w, get_common_interval
from project import Project
from contract import Contract


def builder_calc_w_arg(project: Project, contract: Contract, x, threshold_u):
    return float(
        (
            project.discount_rate
            * (project.c_down_pay - threshold_u)
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


def builder_calc_alpha_beta(project: Project, contract: Contract, x, threshold_u):
    if contract.salary == 0:
        log_arg = (
            contract.reward
            - contract.reimburse_rate * project.c_down_pay
            + (1 - contract.reimburse_rate) * x
        ) / (threshold_u - project.c_down_pay)
        value = np.log(log_arg) / project.discount_rate if log_arg > 0 else 0
        if threshold_u - project.c_down_pay > 0:
            Y0, Y1 = None, value
        else:
            Y0, Y1 = value, None
    else:
        W_arg = builder_calc_w_arg(project, contract, x, threshold_u)
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
            Y0 = None
        if W1:
            # print(f"W_{{-1}}({W_arg}) = {W1}\n")
            Y1 = max(Y - (float(np.real(W1)) / project.discount_rate), 0)
        else:
            # print(f"W_{{-1}} is not defined for {W_arg}\n")
            Y1 = None
    return Y0, Y1


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
    alpha0, alpha1 = builder_calc_alpha_beta(
        project, contract, project.c_uni_high_a, threshold_u
    )
    # print(f"alpha0: {alpha0}, alpha1: {alpha1}\n")
    if alpha1:
        risk = np.exp(-project.d_expo_lambda * alpha1)
    else:
        risk = 0
    if contract.reimburse_rate < 1:
        beta0, beta1 = builder_calc_alpha_beta(
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
        and contract.reimburse_rate < 1
    ):
        x = (contract.reimburse_rate * project.c_down_pay - contract.reward) / (
            1 - contract.reimburse_rate
        )
        risk = 1 - (
            (x - project.c_uni_high_a) / (project.c_uni_low_b - project.c_uni_high_a)
        )
        return risk
    else:
        if threshold_u == project.c_down_pay and contract.reimburse_rate < 1:
            alpha = (
                contract.reimburse_rate * project.c_down_pay
                - (1 - contract.reimburse_rate) * project.c_uni_high_a
                - contract.reward
            ) / contract.salary
            beta = (
                contract.reimburse_rate * project.c_down_pay
                - (1 - contract.reimburse_rate) * project.c_uni_low_b
                - contract.reward
            ) / contract.salary
            HP1, HP2 = get_common_interval(
                (project.d_uni_low_l, project.d_uni_high_h), (0, alpha)
            )
            Hmin, Hmax = get_common_interval(
                (project.d_uni_low_l, project.d_uni_high_h),
                (alpha, beta),
            )
            Lmin, Lmax, LM1, LM2 = None, None, None, None
        else:
            alpha0, alpha1 = builder_calc_alpha_beta(
                project, contract, project.c_uni_high_a, threshold_u
            )
            beta0, beta1 = builder_calc_alpha_beta(
                project, contract, project.c_uni_low_b, threshold_u
            )
            # print(f"alpha0: {alpha0}, alpha1: {alpha1}")
            # print(f"beta0: {beta0},beta1: {beta1}\n")
            common_range = (project.d_uni_low_l, project.d_uni_high_h)
            intervals = {
                "hp": get_common_interval(common_range, (0, alpha0)),
                "h": get_common_interval(common_range, (alpha0, beta0)),
                "l": get_common_interval(common_range, (beta1, alpha1)),
                "lm": get_common_interval(common_range, (alpha1, float("inf"))),
            }
            if threshold_u - project.c_down_pay < 0:
                HP1, HP2 = intervals["hp"]
                Hmin, Hmax = intervals["h"]
                Lmin, Lmax = intervals["l"]
                LM1, LM2 = intervals["lm"]
            else:
                LM1, LM2 = intervals["hp"]
                Lmin, Lmax = intervals["h"]
                Hmin, Hmax = intervals["l"]
                HP1, HP2 = intervals["lm"]
        if HP2 and HP1:
            risk = (HP2 - HP1) / (project.d_uni_high_h - project.d_uni_low_l)
        else:  # HP2 is None
            risk = 0
        if contract.reimburse_rate < 1 and Hmax and Hmin:
            risk += builder_risk_uni_calc_integral(
                project, contract, Hmax, threshold_u
            ) - builder_risk_uni_calc_integral(project, contract, Hmin, threshold_u)
        if contract.salary > 0:
            if LM2 and LM1:
                risk += (LM2 - LM1) / (project.d_uni_high_h - project.d_uni_low_l)
            if contract.reimburse_rate < 1 and Lmax and Lmin:
                risk += builder_risk_uni_calc_integral(
                    project, contract, Lmax, threshold_u
                ) - builder_risk_uni_calc_integral(project, contract, Lmin, threshold_u)
        return risk


def builder_risk(project: Project, contract: Contract, distribution, threshold_u):
    if distribution == "expo":
        return builder_risk_expo(project, contract, threshold_u)
    elif distribution == "uni":
        return builder_risk_uni(project, contract, threshold_u)
    else:
        raise ValueError("The 'distribution' argument must be either 'uni' or 'expo'.")
