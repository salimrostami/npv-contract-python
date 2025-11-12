import numpy as np
from source.definit.project import Project
from source.definit.contract import Contract, calc_reward
from source.definit.param import params
from source.evaluate.exact_eval import exact_calculations
from source.definit.project import SimResults


def calc_builder_npv(proj: Project, cont: Contract, random_c, random_t):
    df = np.exp(-proj.discount_rate * random_t)
    return (
        proj.c_down_pay
        - cont.rate * proj.c_down_pay * df
        + (1 - cont.rate) * random_c * df
        + cont.salary * random_t * df
        + cont.reward * df
    )


def calc_owner_npv(proj: Project, cont: Contract, random_c, random_t):
    df = np.exp(-proj.discount_rate * random_t)
    return (
        cont.rate * proj.c_down_pay * df
        + cont.rate * random_c * df
        - cont.salary * random_t * df
        + (proj.owner_income - cont.reward) * df
    )


def simulate(
    proj: Project,
    cont: Contract,
    results: SimResults,
    builder_threshold_u: float,
):
    # Validate the distribution argument
    if params.dist not in ["uni", "expo"]:
        raise ValueError(
            "The 'distribution' argument must " "be either 'uni' or 'expo'."
        )

    n = params.simRounds
    rng = np.random.default_rng()  # optional: pass a seed for reproducibility

    # Draws
    random_c = rng.uniform(proj.c_low_b, proj.c_high_a, size=n)
    if params.dist == "expo":
        random_t = rng.exponential(1 / proj.d_lambda, size=n)
    else:
        random_t = rng.uniform(proj.d_low_l, proj.d_high_h, size=n)

    # Common discount factor
    # df = np.exp(-proj.discount_rate * random_t)

    # Vectorized NPVs
    builder_npvs = calc_builder_npv(proj, cont, random_c, random_t)

    owner_npvs = calc_owner_npv(proj, cont, random_c, random_t)

    # Metrics
    builder_enpv = float(np.mean(builder_npvs))
    owner_enpv = float(np.mean(owner_npvs))

    builder_risk = float(100.0 * np.mean(builder_npvs < builder_threshold_u))
    owner_risk = float(100.0 * np.mean(owner_npvs < proj.owner_threshold))

    builder_var = float(np.percentile(builder_npvs, 5) - builder_enpv)
    owner_var = float(np.percentile(owner_npvs, 5) - owner_enpv)

    results.builder.enpv = builder_enpv
    results.builder.risk = builder_risk
    results.builder.var = builder_var
    results.owner.enpv = owner_enpv
    results.owner.risk = owner_risk
    results.owner.var = owner_var


def debug_sim_contract(
    proj: Project, nu: float, salary: float, bthresh: float, othresh: float
):
    # proj = Project("sim-temp", cbar, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000)
    cont = Contract("sim-temp", 0, 0, 0, "tm-sense")
    cont.rate = nu
    cont.salary = salary
    cont.reward = calc_reward(proj, proj.b_t_enpv, cont.rate, cont.salary)
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
