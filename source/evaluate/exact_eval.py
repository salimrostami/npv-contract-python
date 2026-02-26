from source.definit.contract import Contract
from source.evaluate.builder.builder_risk import builder_risk
from source.evaluate.builder.builder_var import builder_var
from source.evaluate.builder.builder_cvar import builder_CVaR
from source.evaluate.builder.builder_enpv import builder_enpv
from source.evaluate.owner.owner_enpv import owner_enpv
from source.evaluate.owner.owner_risk import owner_risk
from source.evaluate.owner.owner_var import owner_var
from source.evaluate.owner.owner_cvar import owner_CVaR
from source.definit.project import Project, Result


def exact_calculations(
    proj: Project,
    cont: Contract,
    b_results: Result,
    o_results: Result,
    builder_threshold_u: int,
    calc_cvar: bool = False,
):
    b_results.enpv = builder_enpv(proj, cont)
    o_results.enpv = owner_enpv(proj, cont)
    b_results.risk = 100 * builder_risk(proj, cont, builder_threshold_u)
    o_results.risk = 100 * owner_risk(proj, cont, proj.owner_threshold)
    b_results.var = builder_var(proj, cont, 0.05) - b_results.enpv
    o_results.var = owner_var(proj, cont, 0.05) - o_results.enpv
    if calc_cvar:
        b_results.cvar = builder_CVaR(proj, cont) - b_results.enpv
        o_results.cvar = owner_CVaR(proj, cont) - o_results.enpv
