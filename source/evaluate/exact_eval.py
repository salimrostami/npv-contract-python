from source.definit.contract import Contract
from source.evaluate.builder import builder_risk, builder_var
from source.evaluate.builder.builder_enpv import builder_enpv
from source.evaluate.owner import owner_enpv, owner_risk, owner_var
from source.definit.project import Project


def exact_calculations(
    proj: Project, cont: Contract, distribution: str, builder_threshold_u: int
):
    proj.exact_results.builder.enpv = round(builder_enpv(proj, cont, distribution), 6)
    proj.exact_results.owner.enpv = round(owner_enpv(proj, cont, distribution), 6)
    proj.exact_results.builder.risk = round(
        100 * builder_risk(proj, cont, distribution, builder_threshold_u), 6
    )
    proj.exact_results.owner.risk = round(
        100 * owner_risk(proj, cont, distribution, proj.owner_threshold), 6
    )
    proj.exact_results.builder.var = round(
        builder_var(proj, cont, distribution, 0.05) - proj.exact_results.builder.enpv, 6
    )
    proj.exact_results.owner.var = round(
        owner_var(proj, cont, distribution, 0.05) - proj.exact_results.owner.enpv, 6
    )
