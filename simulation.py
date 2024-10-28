import numpy as np
from project import Project
from contract import Contract


def calc_builder_npv(project: Project, contract: Contract, random_c, random_t):
    return (
        project.c_down_pay
        - contract.reimburse_rate
        * project.c_down_pay
        * np.exp(-project.discount_rate * random_t)
        + (1 - contract.reimburse_rate)
        * random_c
        * np.exp(-project.discount_rate * random_t)
        + contract.salary * random_t * np.exp(-project.discount_rate * random_t)
        + contract.reward * np.exp(-project.discount_rate * random_t)
    )


def calc_owner_npv(project: Project, contract: Contract, random_c, random_t):
    return (
        contract.reimburse_rate
        * project.c_down_pay
        * np.exp(-project.discount_rate * random_t)
        + contract.reimburse_rate * random_c * np.exp(-project.discount_rate * random_t)
        - contract.salary * random_t * np.exp(-project.discount_rate * random_t)
        + (project.owner_income - contract.reward)
        * np.exp(-project.discount_rate * random_t)
    )


def simulate(
    project: Project,
    contract: Contract,
    num_simulations,
    distribution,
):
    # Validate the distribution argument
    if distribution not in ["uni", "expo"]:
        raise ValueError(
            "The 'distribution' argument must " "be either 'uni' or 'expo'."
        )

    builder_npvs = []
    owner_npvs = []
    counter_builder_low_npv = 0
    counter_owner_low_npv = 0
    for _ in range(num_simulations):

        # Simulate a project scenario
        random_c = np.random.uniform(project.c_uni_low_b, project.c_uni_high_a)
        if distribution == "expo":
            random_t = np.random.exponential(1 / project.d_expo_lambda)
        else:
            random_t = np.random.uniform(project.d_uni_low_l, project.d_uni_high_h)

        # Colculate the NPV for the builder and the owner
        # in the current scenario
        builder_npv = calc_builder_npv(project, contract, random_c, random_t)
        owner_npv = calc_owner_npv(project, contract, random_c, random_t)

        # Check if NPV is below threshold
        if builder_npv < project.builder_threshold:
            counter_builder_low_npv += 1
        # Check if NPV is below threshold
        if owner_npv < project.owner_threshold:
            counter_owner_low_npv += 1

        # store the npvs
        builder_npvs.append(builder_npv)
        owner_npvs.append(owner_npv)

    # print(builder_npvs)
    # print(owner_npvs)

    builder_enpv = round(np.mean(builder_npvs), 2)  # expected npv over simulations
    builder_risk = round(
        float(100 * counter_builder_low_npv / num_simulations), 2
    )  # low npv probability over simulations
    builder_var = round(
        np.percentile(builder_npvs, 5) - builder_enpv, 2
    )  # VaR at 5% level

    owner_enpv = round(np.mean(owner_npvs), 2)  # expected npv over simulations
    owner_risk = round(
        float(100 * counter_owner_low_npv / num_simulations), 2
    )  # low npv probability over simulations
    owner_var = round(np.percentile(owner_npvs, 5) - owner_enpv, 2)  # VaR at 5% level

    return [
        builder_enpv,
        builder_risk,
        builder_var,
        owner_enpv,
        owner_risk,
        owner_var,
    ]
