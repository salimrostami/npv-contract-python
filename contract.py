from project import Project
import numpy as np


class Contract:
    def __init__(self, cont_id, reward, rate, salary):
        self.id = cont_id
        self.reimburse_rate = rate
        self.salary = salary
        self.reward = reward
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


contracts = []


def calc_reward_expo(project: Project, target_b_enpv, nu, s):
    return (
        (target_b_enpv - project.c_down_pay)
        * (project.d_expo_lambda + project.discount_rate)
        / project.d_expo_lambda
        + nu * project.c_down_pay
        - (1 - nu) * (project.c_uni_low_b + project.c_uni_high_a) / 2
        - s / (project.d_expo_lambda + project.discount_rate)
    )


def calc_reward_uni(project: Project, target_b_enpv, nu, s):
    return (
        (target_b_enpv - project.c_down_pay)
        * (project.discount_rate * (project.d_uni_low_l - project.d_uni_high_h))
        / (
            np.exp(-project.discount_rate * project.d_uni_high_h)
            - np.exp(-project.discount_rate * project.d_uni_low_l)
        )
        + nu * project.c_down_pay
        - (1 - nu) * (project.c_uni_low_b + project.c_uni_high_a) / 2
        - s
        * (
            np.exp(-project.discount_rate * project.d_uni_high_h)
            * (project.discount_rate * project.d_uni_high_h + 1)
            - np.exp(-project.discount_rate * project.d_uni_low_l)
            * (project.discount_rate * project.d_uni_low_l + 1)
        )
        / (
            project.discount_rate
            * (
                np.exp(-project.discount_rate * project.d_uni_high_h)
                - np.exp(-project.discount_rate * project.d_uni_low_l)
            )
        )
    )


def calc_reward(project, target_b_enpv, nu, s, distribution):
    if distribution == "expo":
        return calc_reward_expo(project, target_b_enpv, nu, s)
    elif distribution == "uni":
        return calc_reward_uni(project, target_b_enpv, nu, s)
    else:
        raise ValueError("The 'distribution' argument must be 'expo' or 'uni'.")


def calc_salary_expo(project: Project, target_b_enpv, nu, R):
    return (target_b_enpv - project.c_down_pay) * (
        (project.d_expo_lambda + project.discount_rate) ** 2
    ) / project.d_expo_lambda + (
        nu * project.c_down_pay
        - (1 - nu) * (project.c_uni_low_b + project.c_uni_high_a) / 2
        - R
    ) * (
        project.d_expo_lambda + project.discount_rate
    )


def calc_salary_uni(project: Project, target_b_enpv, nu, R):
    return (
        (
            target_b_enpv
            - project.c_down_pay
            - (
                R
                - nu * project.c_down_pay
                + (1 - nu) * (project.c_uni_low_b + project.c_uni_high_a) / 2
            )
            * (
                np.exp(-project.discount_rate * project.d_uni_high_h)
                - np.exp(-project.discount_rate * project.d_uni_low_l)
            )
            / (project.discount_rate * (project.d_uni_low_l - project.d_uni_high_h))
        )
        * (project.discount_rate**2 * (project.d_uni_low_l - project.d_uni_high_h))
        / (
            (
                np.exp(-project.discount_rate * project.d_uni_high_h)
                * (project.discount_rate * project.d_uni_high_h + 1)
            )
            - (
                np.exp(-project.discount_rate * project.d_uni_low_l)
                * (project.discount_rate * project.d_uni_low_l + 1)
            )
        )
    )


def calc_salary(project, target_b_enpv, nu, R, distribution):
    if distribution == "expo":
        return calc_salary_expo(project, target_b_enpv, nu, R)
    elif distribution == "uni":
        return calc_salary_uni(project, target_b_enpv, nu, R)
    else:
        raise ValueError("The 'distribution' argument must be 'expo' or 'uni'.")


def make_contracts(project: Project, target_b_enpv, distribution):
    counter = 0
    for nu in [0, 0.5, 0.85, 1]:
        Rmax = round(calc_reward(project, target_b_enpv, nu, 0, distribution), 2)
        Smax = round(calc_salary(project, target_b_enpv, nu, 0, distribution), 2)
        R_Smax2 = round(
            calc_reward(project, target_b_enpv, nu, Smax / 2, distribution), 2
        )
        try:
            contracts.append(Contract(f"{(counter+1):03}", Rmax, nu, 0))
            counter += 1
            contracts.append(
                Contract(f"{(counter+1):03}", R_Smax2, nu, round(Smax / 2, 2))
            )
            counter += 1
            contracts.append(Contract(f"{(counter+1):03}", 0, nu, Smax))
            counter += 1
        except ValueError as e:
            print(e)


# try:
#     # contracts.append(Contract("001", 17000, 0, 0))
#     # contracts.append(Contract("002", 12250, 0.5, 0))
#     # contracts.append(Contract("003", 7500, 1, 0))
#     # contracts.append(Contract("004", 16000, 0, 200))
#     # contracts.append(Contract("005", 11250, 0.5, 200))
#     # contracts.append(Contract("006", 6500, 1, 200))
#     # contracts.append(Contract("007", 6450, 0.9, 400))
#     # contracts.append(Contract("008", 5450, 0.9, 600))
#     # contracts.append(Contract("009", 0, 0, 3400))
#     # contracts.append(Contract("010", 0, 0.5, 2450))
#     # contracts.append(Contract("011", 0, 0.9, 1690))
#     # contracts.append(Contract("012", 0, 1, 1500))

#     contracts.append(Contract("001", 27548, 0, 0))
#     contracts.append(Contract("002", 15049, 0.5, 0))
#     contracts.append(Contract("003", 2549, 1, 0))
#     contracts.append(Contract("004", 26680, 0, 583))
#     contracts.append(Contract("005", 14180, 0.5, 583))
#     contracts.append(Contract("006", 4751, 0.9, 200))
#     contracts.append(Contract("007", 2250, 1, 200))
#     contracts.append(Contract("009", 0, 0, 18469))
#     contracts.append(Contract("010", 0, 0.5, 10089))
#     contracts.append(Contract("011", 0, 0.9, 3385))
#     contracts.append(Contract("012", 0, 1, 1709))
# except ValueError as e:
#     print(e)
