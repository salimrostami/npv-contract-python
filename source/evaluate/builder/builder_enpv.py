import numpy as np
from source.definit.project import Project
from source.definit.contract import Contract
from source.definit.param import params


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


def builder_enpv(project: Project, contract: Contract):
    if params.dist == "expo":
        return builder_enpv_expo(project, contract)
    elif params.dist == "uni":
        return builder_enpv_uni(project, contract)
    else:
        raise ValueError("The 'distribution' argument must be either 'uni' or 'expo'.")
