from source.definit.project import Project
from source.definit.contract import calc_reward, Contract
from source.evaluate.builder.builder_enpv import builder_enpv
from source.evaluate.builder.builder_risk import builder_risk
from source.evaluate.builder.builder_var import builder_var
from source.evaluate.owner.owner_enpv import owner_enpv
from source.evaluate.owner.owner_risk import owner_risk
from source.evaluate.owner.owner_var import owner_var


def initialize(project: Project):
    if project.lsOpt.contract is None:
        Rmax = calc_reward(project, project.builder_target_enpv, 0, 0)
        project.lsOpt.contract = Contract("lsBase", Rmax, 0, 0, "0.0-0.0")

        project.lsOpt.builder.enpv = builder_enpv(project, project.lsOpt.contract)
        project.lsOpt.owner.enpv = owner_enpv(project, project.lsOpt.contract)

        project.owner_target_enpv = project.lsOpt.owner.enpv
        project.owner_threshold = project.lsOpt.owner.enpv - project.lsOpt.builder.enpv

        project.lsOpt.builder.risk = 100 * builder_risk(
            project, project.lsOpt.contract, 0
        )
        project.lsOpt.owner.risk = 100 * owner_risk(
            project,
            project.lsOpt.contract,
            project.owner_threshold,
        )

        project.lsOpt.builder.var = (
            builder_var(project, project.lsOpt.contract, 0.05)
            - project.lsOpt.builder.enpv
        )
        project.lsOpt.owner.var = (
            owner_var(project, project.lsOpt.contract, 0.05) - project.lsOpt.owner.enpv
        )
