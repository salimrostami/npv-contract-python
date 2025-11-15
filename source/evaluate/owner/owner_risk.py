import numpy as np

# from source.evaluate.simulation import debug_sim_contract
from source.evaluate.simulation import calc_owner_npv, sim_o_risk
from source.utility.math_helpers import (
    build_interval,
    compute_lambert_w,
    get_common_interval,
)
from source.definit.project import Project
from source.definit.contract import Contract
from source.definit.param import params


def owner_calc_w_arg(proj: Project, cont: Contract, x_ab, threshold_u):
    exp_arg = (
        proj.discount_rate
        * (proj.owner_income + cont.rate * (x_ab + proj.c_down_pay) - cont.reward)
        / cont.salary
    )
    exp_result = np.exp(exp_arg)
    w_arg = proj.discount_rate * threshold_u * exp_result / cont.salary
    return w_arg if w_arg != np.inf else np.finfo(np.float64).max


def owner_calc_eps_tau_w(proj: Project, cont: Contract, x_ab, threshold_u):
    W_arg = owner_calc_w_arg(proj, cont, x_ab, threshold_u)
    # You can change this to any value
    W0, W1 = compute_lambert_w(W_arg)
    if W0 is not None or W1 is not None:
        Y = (
            proj.owner_income + cont.rate * (proj.c_down_pay + x_ab) - cont.reward
        ) / cont.salary
    if W0 is not None:
        Y0 = max(Y - (float(np.real(W0)) / proj.discount_rate), 0)
    else:
        Y0 = None
    if W1 is not None:
        Y1 = max(Y - (float(np.real(W1)) / proj.discount_rate), 0)
    else:
        Y1 = None
    return Y0, Y1


def owner_calc_eps_tau_log(proj: Project, cont: Contract, x_ab, threshold_u):
    log_arg = (
        proj.owner_income + cont.rate * (proj.c_down_pay + x_ab) - cont.reward
    ) / threshold_u
    value = np.log(log_arg) / proj.discount_rate if log_arg > 0 else None
    return value


def owner_calc_intervals(proj: Project, cont: Contract, threshold_u):
    if cont.salary > 0:
        eps_0, eps_1 = owner_calc_eps_tau_w(proj, cont, proj.c_high_a, threshold_u)
        tau_0, tau_1 = owner_calc_eps_tau_w(proj, cont, proj.c_low_b, threshold_u)
    elif cont.salary == 0:
        if threshold_u < 0:
            eps_0 = tau_0 = 0
            eps_1 = owner_calc_eps_tau_log(proj, cont, proj.c_high_a, threshold_u)
            tau_1 = owner_calc_eps_tau_log(proj, cont, proj.c_low_b, threshold_u)
        elif threshold_u > 0:
            eps_0 = owner_calc_eps_tau_log(proj, cont, proj.c_high_a, threshold_u)
            tau_0 = owner_calc_eps_tau_log(proj, cont, proj.c_low_b, threshold_u)
            eps_1 = tau_1 = None
    else:
        raise ValueError(
            f"owner_calc_intervals - Unexpected value of salary: {cont.salary}."
        )

    if threshold_u < 0:
        C = build_interval(eps_0, eps_1)
        if eps_0 is None and eps_1 is None:
            ML = build_interval(tau_0, tau_1)
            MR = (None, None)
        else:
            ML = build_interval(tau_0, eps_0)
            MR = build_interval(eps_1, tau_1)
    elif threshold_u > 0:
        ML = build_interval(tau_0, eps_0)
        C = (eps_0, float("inf"))
        MR = (None, None)
    elif threshold_u == 0 and cont.salary > 0:
        ML = build_interval(tau_0, eps_0)
        C = (eps_0, float("inf"))
        MR = (None, None)
    elif threshold_u == 0 and cont.salary == 0:
        ML = (0, float("inf"))
        C = (None, None)
        MR = (None, None)
    else:  # threshold_u == 0 and cont.salary > 0
        ML = C = MR = (None, None)

    return ML, C, MR


def owner_risk_expo_calc_integral(proj: Project, cont: Contract, x_ab, threshold_u):
    if proj.discount_rate == proj.d_lambda:
        y = threshold_u * proj.d_lambda * x_ab
    else:
        y = (
            proj.d_lambda
            * threshold_u
            * np.exp((proj.discount_rate - proj.d_lambda) * x_ab)
            / (proj.discount_rate - proj.d_lambda)
        )
    return (
        1
        / (cont.rate * (proj.c_low_b - proj.c_high_a))
        * (
            -y
            + (
                cont.salary
                * (1 + proj.d_lambda * x_ab)
                * np.exp(-proj.d_lambda * x_ab)
                / proj.d_lambda
            )
            - (
                proj.owner_income
                + cont.rate * (proj.c_down_pay + proj.c_low_b)
                - cont.reward
            )
            * np.exp(-proj.d_lambda * x_ab)
        )
    )


def owner_risk_expo(proj: Project, cont: Contract, threshold_u):
    eps0, eps1 = owner_calc_eps_tau_w(proj, cont, proj.c_high_a, threshold_u)
    # print(f"eps0: {eps0}, eps1: {eps1}\n")
    risk = np.exp(-proj.d_lambda * eps0)
    if cont.rate > 0:
        tau0, tau1 = owner_calc_eps_tau_w(proj, cont, proj.c_low_b, threshold_u)
        # print(f"tau0: {tau0},tau1: {tau1}\n")
        risk += owner_risk_expo_calc_integral(
            proj, cont, eps0, threshold_u
        ) - owner_risk_expo_calc_integral(proj, cont, tau0, threshold_u)
    if cont.salary > 0:
        risk += 1 - np.exp(-proj.d_lambda * eps1)
        if cont.rate > 0:
            risk += owner_risk_expo_calc_integral(
                proj, cont, tau1, threshold_u
            ) - owner_risk_expo_calc_integral(proj, cont, eps1, threshold_u)
    return risk


def owner_risk_uni_calc_integral(proj: Project, cont: Contract, x_ab, threshold_u):
    return (
        1
        / (cont.rate * (proj.c_low_b - proj.c_high_a) * (proj.d_high_h - proj.d_low_l))
        * (
            -threshold_u * np.exp(proj.discount_rate * x_ab) / proj.discount_rate
            - (cont.salary * x_ab**2 / 2)
            + (
                proj.owner_income
                - cont.reward
                + cont.rate * proj.c_low_b
                + cont.rate * proj.c_down_pay
            )
            * x_ab
        )
    )


def owner_risk_uni(proj: Project, cont: Contract, threshold_u):
    if threshold_u == 0 and cont.salary == 0 and cont.rate == 0:
        risk = 1 if proj.owner_income < cont.reward else 0
    elif threshold_u == 0 and cont.salary == 0:
        delta = (
            cont.reward - cont.rate * proj.c_down_pay - proj.owner_income
        ) / cont.rate
        if delta > proj.c_high_a:
            return 1
        elif delta < proj.c_low_b:
            return 0
        return (delta - proj.c_low_b) / (proj.c_high_a - proj.c_low_b)
    else:
        ML, C, MR = owner_calc_intervals(proj, cont, threshold_u)
        common_range = (proj.d_low_l, proj.d_high_h)
        ML = get_common_interval(common_range, ML)
        C = get_common_interval(common_range, C)
        MR = get_common_interval(common_range, MR)
        if ML == C == MR == (None, None):
            # test if prob is 1 or 0
            test_onpv = calc_owner_npv(proj, cont, proj.c_low_b, proj.d_low_l)
            risk = 1 if test_onpv < threshold_u else 0
            sim_orisk = sim_o_risk(proj, cont, threshold_u)
            if sim_orisk != risk:
                raise ValueError(
                    f"Intervals None; sim_risk: {sim_orisk} differs from risk: {risk}"
                )
        else:
            if ML[0] is not None and ML[1] is not None and ML[0] < ML[1]:
                risk = owner_risk_uni_calc_integral(
                    proj, cont, ML[1], threshold_u
                ) - owner_risk_uni_calc_integral(proj, cont, ML[0], threshold_u)
            else:
                risk = 0
            if C[0] is not None and C[1] is not None:
                risk += (C[1] - C[0]) / (proj.d_high_h - proj.d_low_l)
            if MR[0] is not None and MR[1] is not None and MR[0] < MR[1]:
                risk += owner_risk_uni_calc_integral(
                    proj, cont, MR[1], threshold_u
                ) - owner_risk_uni_calc_integral(proj, cont, MR[0], threshold_u)

    return risk


def owner_risk(proj: Project, cont: Contract, threshold_u):
    if params.dist == "expo":
        return owner_risk_expo(proj, cont, threshold_u)
    elif params.dist == "uni":
        return owner_risk_uni(proj, cont, threshold_u)
    else:
        raise ValueError("The 'distribution' argument must be either 'uni' or 'expo'.")
