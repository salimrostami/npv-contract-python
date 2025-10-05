from source.definit.contract import Contract
from source.evaluate.builder.builder_risk import builder_risk
from source.evaluate.builder.builder_var import builder_var
from source.evaluate.builder.builder_enpv import builder_enpv
from source.evaluate.owner.owner_enpv import owner_enpv
from source.evaluate.owner.owner_risk import owner_risk
from source.evaluate.owner.owner_var import owner_var
from source.definit.project import Project
from source.definit.param import params


def exact_calculations(proj: Project, cont: Contract, builder_threshold_u: int):
    proj.exact_results.builder.enpv = builder_enpv(proj, cont, params.dist)
    proj.exact_results.owner.enpv = owner_enpv(proj, cont, params.dist)
    proj.exact_results.builder.risk = 100 * builder_risk(
        proj, cont, params.dist, builder_threshold_u
    )
    proj.exact_results.owner.risk = 100 * owner_risk(
        proj, cont, params.dist, proj.owner_threshold
    )
    proj.exact_results.builder.var = (
        builder_var(proj, cont, params.dist, 0.05) - proj.exact_results.builder.enpv
    )
    proj.exact_results.owner.var = (
        owner_var(proj, cont, params.dist, 0.05) - proj.exact_results.owner.enpv
    )
