import numpy as np
from source.definit.project import Project
from source.definit.contract import Contract
from source.definit.param import params


def builder_enpv_expo(
    proj: Project,
    cont: Contract,
):
    return (
        proj.c_down_pay
        + (
            cont.reward
            - cont.rate * proj.c_down_pay
            + (1 - cont.rate) * (proj.c_high_a + proj.c_low_b) / 2
        )
        * (proj.d_lambda / (proj.d_lambda + proj.discount_rate))
        + (+(cont.salary * proj.d_lambda) / (proj.d_lambda + proj.discount_rate) ** 2)
    )


def builder_enpv_uni(
    proj: Project,
    cont: Contract,
):
    return (
        proj.c_down_pay
        + (
            cont.reward
            - cont.rate * proj.c_down_pay
            + (1 - cont.rate) * (proj.c_high_a + proj.c_low_b) / 2
        )
        * (
            np.exp(-proj.discount_rate * proj.d_high_h)
            - np.exp(-proj.discount_rate * proj.d_low_l)
        )
        / (proj.discount_rate * (proj.d_low_l - proj.d_high_h))
        + (
            cont.salary
            * (
                np.exp(-proj.discount_rate * proj.d_high_h)
                * (proj.discount_rate * proj.d_high_h + 1)
                - np.exp(-proj.discount_rate * proj.d_low_l)
                * (proj.discount_rate * proj.d_low_l + 1)
            )
            / ((proj.discount_rate**2) * (proj.d_low_l - proj.d_high_h))
        )
    )


def builder_enpv(proj: Project, cont: Contract):
    if params.dist == "expo":
        return builder_enpv_expo(proj, cont)
    elif params.dist == "uni":
        return builder_enpv_uni(proj, cont)
    else:
        raise ValueError("The 'distribution' argument must be either 'uni' or 'expo'.")
