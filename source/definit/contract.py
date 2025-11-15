from source.definit.param import params
from source.definit.project import Project
import numpy as np


class Contract:
    def __init__(self, cont_id, reward, rate, salary, subtype):
        self.id: str = cont_id
        self.rate: float = rate
        self.salary: float = salary
        self.reward: float = reward
        self.type: str = ""
        if salary == 0 and rate == 0:
            self.type = "ls"
        elif salary == 0 and rate > 0:
            self.type = "cp"
        elif salary > 0 and rate == 0:
            self.type = "lh"
        elif salary > 0 and rate > 0:
            self.type = "tm"
        else:
            self.type = "unknown"
            raise ValueError(
                "Unexpected contract type: "
                f"reward={reward}, rate={rate}, salary={salary}"
            )
        self.subtype: str = subtype


contracts = []


def calc_reward_expo(proj: Project, target_b_enpv, nu, s):
    return (
        (target_b_enpv - proj.c_down_pay)
        * (proj.d_lambda + proj.discount_rate)
        / proj.d_lambda
        + nu * proj.c_down_pay
        - (1 - nu) * (proj.c_low_b + proj.c_high_a) / 2
        - s / (proj.d_lambda + proj.discount_rate)
    )


def calc_reward_uni(proj: Project, target_b_enpv, nu, s):
    A = params.enpvs_factor
    erh = np.exp(-proj.discount_rate * proj.d_high_h)
    erl = np.exp(-proj.discount_rate * proj.d_low_l)
    c_mean = (proj.c_low_b + proj.c_high_a) / 2
    if A == 0:
        return (
            (target_b_enpv - proj.c_down_pay)
            * (proj.discount_rate * (proj.d_low_l - proj.d_high_h))
            / (erh - erl)
            + nu * proj.c_down_pay
            - (1 - nu) * c_mean
            - s
            * (
                erh * (proj.discount_rate * proj.d_high_h + 1)
                - erl * (proj.discount_rate * proj.d_low_l + 1)
            )
            / (proj.discount_rate * (erh - erl))
        )
    elif A > 0:
        X = (erh - erl) / (proj.discount_rate * (proj.d_low_l - proj.d_high_h))
        Y = (
            erh * (proj.discount_rate * proj.d_high_h + 1)
            - erl * (proj.discount_rate * proj.d_low_l + 1)
        ) / (proj.discount_rate**2 * (proj.d_low_l - proj.d_high_h))
        Z = (proj.owner_income * X - A * proj.c_down_pay - A * X * c_mean) / (A + 1)

        return max(0, (Z + nu * X * (proj.c_down_pay + c_mean) - s * Y) / X)
    else:
        raise ValueError("enpvs_factor must be non-negative.")


def calc_reward(proj, target_b_enpv, nu, s):
    if params.dist == "expo":
        return calc_reward_expo(proj, target_b_enpv, nu, s)
    elif params.dist == "uni":
        return calc_reward_uni(proj, target_b_enpv, nu, s)
    else:
        raise ValueError("The 'distribution' argument must be 'expo' or 'uni'.")


def calc_salary_expo(proj: Project, target_b_enpv, nu, R):
    return (target_b_enpv - proj.c_down_pay) * (
        (proj.d_lambda + proj.discount_rate) ** 2
    ) / proj.d_lambda + (
        nu * proj.c_down_pay - (1 - nu) * (proj.c_low_b + proj.c_high_a) / 2 - R
    ) * (
        proj.d_lambda + proj.discount_rate
    )


def calc_salary_uni(proj: Project, target_b_enpv, nu, R):
    A = params.enpvs_factor
    erh = np.exp(-proj.discount_rate * proj.d_high_h)
    erl = np.exp(-proj.discount_rate * proj.d_low_l)
    c_mean = (proj.c_low_b + proj.c_high_a) / 2
    if A == 0:
        return (
            (
                target_b_enpv
                - proj.c_down_pay
                - (
                    R
                    - nu * proj.c_down_pay
                    + (1 - nu) * (proj.c_low_b + proj.c_high_a) / 2
                )
                * (
                    np.exp(-proj.discount_rate * proj.d_high_h)
                    - np.exp(-proj.discount_rate * proj.d_low_l)
                )
                / (proj.discount_rate * (proj.d_low_l - proj.d_high_h))
            )
            * (proj.discount_rate**2 * (proj.d_low_l - proj.d_high_h))
            / (
                (
                    np.exp(-proj.discount_rate * proj.d_high_h)
                    * (proj.discount_rate * proj.d_high_h + 1)
                )
                - (
                    np.exp(-proj.discount_rate * proj.d_low_l)
                    * (proj.discount_rate * proj.d_low_l + 1)
                )
            )
        )
    elif A > 0:
        X = (erh - erl) / (proj.discount_rate * (proj.d_low_l - proj.d_high_h))
        Y = (
            erh * (proj.discount_rate * proj.d_high_h + 1)
            - erl * (proj.discount_rate * proj.d_low_l + 1)
        ) / (proj.discount_rate**2 * (proj.d_low_l - proj.d_high_h))
        Z = (proj.owner_income * X - A * proj.c_down_pay - A * X * c_mean) / (A + 1)
        return max(0, (Z + nu * X * (proj.c_down_pay + c_mean) - R * X) / Y)
    else:
        raise ValueError("enpvs_factor must be non-negative.")


def calc_salary(proj, target_b_enpv, nu, R):
    if params.dist == "expo":
        return calc_salary_expo(proj, target_b_enpv, nu, R)
    elif params.dist == "uni":
        return calc_salary_uni(proj, target_b_enpv, nu, R)
    else:
        raise ValueError("The 'distribution' argument must be 'expo' or 'uni'.")


def calc_rate_uni(proj: Project, target_b_enpv, R, s):
    A = params.enpvs_factor
    erh = np.exp(-proj.discount_rate * proj.d_high_h)
    erl = np.exp(-proj.discount_rate * proj.d_low_l)
    c_mean = (proj.c_low_b + proj.c_high_a) / 2
    if A == 0:
        x = (
            (target_b_enpv - proj.c_down_pay)
            * (proj.discount_rate * (proj.d_low_l - proj.d_high_h))
            / (
                np.exp(-proj.discount_rate * proj.d_high_h)
                - np.exp(-proj.discount_rate * proj.d_low_l)
            )
            - R
            - s
            * (
                np.exp(-proj.discount_rate * proj.d_high_h)
                * (proj.discount_rate * proj.d_high_h + 1)
                - np.exp(-proj.discount_rate * proj.d_low_l)
                * (proj.discount_rate * proj.d_low_l + 1)
            )
            / (
                proj.discount_rate
                * (
                    np.exp(-proj.discount_rate * proj.d_high_h)
                    - np.exp(-proj.discount_rate * proj.d_low_l)
                )
            )
        )
        rate = (c_mean - x) / (c_mean + proj.c_down_pay)
        return min(1, rate)
    elif A > 0:
        X = (erh - erl) / (proj.discount_rate * (proj.d_low_l - proj.d_high_h))
        Y = (
            erh * (proj.discount_rate * proj.d_high_h + 1)
            - erl * (proj.discount_rate * proj.d_low_l + 1)
        ) / (proj.discount_rate**2 * (proj.d_low_l - proj.d_high_h))
        Z = (proj.owner_income * X - A * proj.c_down_pay - A * X * c_mean) / (A + 1)

        return max(0, min(1, (R * X + s * Y - Z) / (X * (proj.c_down_pay + c_mean))))
    else:
        raise ValueError("enpvs_factor must be non-negative.")
