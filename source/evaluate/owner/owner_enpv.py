import numpy as np
from source.definit.project import Project
from source.definit.contract import Contract


def owner_enpv_expo(
    project: Project,
    contract: Contract,
):
    return (
        project.owner_income
        - contract.reward
        + (contract.reimburse_rate * project.c_down_pay)
        + (contract.reimburse_rate * (project.c_uni_high_a + project.c_uni_low_b) / 2)
    ) * project.d_expo_lambda / (project.d_expo_lambda + project.discount_rate) - (
        (contract.salary * project.d_expo_lambda)
        / ((project.d_expo_lambda + project.discount_rate) ** 2)
    )


def owner_enpv_uni(
    project: Project,
    contract: Contract,
):
    return (
        project.owner_income
        - contract.reward
        + contract.reimburse_rate * project.c_down_pay
        + contract.reimburse_rate * (project.c_uni_high_a + project.c_uni_low_b) / 2
    ) * (
        np.exp(-project.discount_rate * project.d_uni_high_h)
        - np.exp(-project.discount_rate * project.d_uni_low_l)
    ) / (
        project.discount_rate * (project.d_uni_low_l - project.d_uni_high_h)
    ) - (
        contract.salary
        * (
            np.exp(-project.discount_rate * project.d_uni_high_h)
            * (project.discount_rate * project.d_uni_high_h + 1)
            - np.exp(-project.discount_rate * project.d_uni_low_l)
            * (project.discount_rate * project.d_uni_low_l + 1)
        )
        / ((project.discount_rate**2) * (project.d_uni_low_l - project.d_uni_high_h))
    )


def owner_enpv(project: Project, contract: Contract, distribution):
    if distribution == "expo":
        return owner_enpv_expo(project, contract)
    elif distribution == "uni":
        return owner_enpv_uni(project, contract)
    else:
        raise ValueError("The 'distribution' argument must be either 'uni' or 'expo'.")
