import numpy as np
from source.definit.project import Project
from source.definit.contract import Contract, calc_reward
from source.definit.param import params
from source.evaluate.exact_eval import exact_calculations
from source.definit.project import SimResults


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
    results: SimResults,
    builder_threshold_u: float,
):
    # Validate the distribution argument
    if params.dist not in ["uni", "expo"]:
        raise ValueError(
            "The 'distribution' argument must " "be either 'uni' or 'expo'."
        )

    builder_npvs = []
    owner_npvs = []
    counter_builder_low_npv = 0
    counter_owner_low_npv = 0
    for _ in range(params.simRounds):

        # Simulate a project scenario
        random_c = np.random.uniform(project.c_uni_low_b, project.c_uni_high_a)
        if params.dist == "expo":
            random_t = np.random.exponential(1 / project.d_expo_lambda)
        else:
            random_t = np.random.uniform(project.d_uni_low_l, project.d_uni_high_h)

        # Colculate the NPV for the builder and the owner
        # in the current scenario
        builder_npv = calc_builder_npv(project, contract, random_c, random_t)
        owner_npv = calc_owner_npv(project, contract, random_c, random_t)

        # Check if NPV is below threshold
        if builder_npv < builder_threshold_u:
            counter_builder_low_npv += 1
        # Check if NPV is below threshold
        if owner_npv < project.owner_threshold:
            counter_owner_low_npv += 1

        # store the npvs
        builder_npvs.append(builder_npv)
        owner_npvs.append(owner_npv)

    # print(builder_npvs)
    # print(owner_npvs)

    builder_enpv = np.mean(builder_npvs)
    builder_risk = float(100 * counter_builder_low_npv / params.simRounds)
    builder_var = np.percentile(builder_npvs, 5) - builder_enpv

    owner_enpv = np.mean(owner_npvs)
    owner_risk = float(100 * counter_owner_low_npv / params.simRounds)
    owner_var = np.percentile(owner_npvs, 5) - owner_enpv

    results.builder.enpv = builder_enpv
    results.builder.risk = builder_risk
    results.builder.var = builder_var
    results.owner.enpv = owner_enpv
    results.owner.risk = owner_risk
    results.owner.var = owner_var


def debug_sim_contract(
    proj: Project,
    nu: float,
    salary: float,
    bthresh: float,
    othresh: float,
):
    # proj = Project("sim-temp", cbar, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000)
    cont = Contract("sim-temp", 0, 0, 0, "tm-sense")
    cont.reimburse_rate = nu
    cont.salary = salary
    cont.reward = calc_reward(
        proj,
        proj.builder_target_enpv,
        cont.reimburse_rate,
        cont.salary,
    )
    cont.reward = max(0, cont.reward)
    # initialize(proj)
    proj.owner_threshold = othresh
    simulate(proj, cont, proj.sim_results, bthresh)
    # Fixed-width table output for aligned columns
    hdr_fmt = "{:<16}{:<16}{:<16}{:<16}{:<16}{:<16}{:<16}"
    num_fmt = "{:>16.6f}{:>16.6f}{:>16.6f}{:>16.6f}{:>16.6f}{:>16.6f}{:>16.6f}"
    print(
        hdr_fmt.format(
            "Builder enpv",
            "Owner enpv",
            "Builder risk",
            "Owner risk",
            "Builder VaR",
            "Owner VaR",
            "total VaR",
        )
    )
    print(
        num_fmt.format(
            float(proj.sim_results.builder.enpv),
            float(proj.sim_results.owner.enpv),
            float(proj.sim_results.builder.risk),
            float(proj.sim_results.owner.risk),
            float(proj.sim_results.builder.var),
            float(proj.sim_results.owner.var),
            float(proj.sim_results.builder.var + proj.sim_results.owner.var),
        )
    )
    exact_calculations(
        proj, cont, proj.exact_results.builder, proj.exact_results.owner, bthresh
    )
    print(
        num_fmt.format(
            float(proj.exact_results.builder.enpv),
            float(proj.exact_results.owner.enpv),
            float(proj.exact_results.builder.risk),
            float(proj.exact_results.owner.risk),
            float(proj.exact_results.builder.var),
            float(proj.exact_results.owner.var),
            float(proj.exact_results.builder.var + proj.exact_results.owner.var),
        )
    )
