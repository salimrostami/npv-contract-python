from source.definit.project import Project
from source.definit.contract import calc_reward, Contract
from source.evaluate.builder.builder_enpv import builder_enpv
from source.evaluate.builder.builder_risk import builder_risk
from source.evaluate.builder.builder_var import builder_var
from source.evaluate.owner.owner_enpv import owner_enpv
from source.evaluate.owner.owner_risk import owner_risk
from source.evaluate.owner.owner_var import owner_var


def initialize(project: Project, distribution):
    if project.lsOpt.contract is None:
        Rmax = calc_reward(project, project.builder_target_enpv, 0, 0, distribution)
        project.lsOpt.contract = Contract("lsBase", Rmax, 0, 0, "0.0-0.0")

        project.lsOpt.builder.enpv = round(
            builder_enpv(project, project.lsOpt.contract, distribution), 6
        )
        project.lsOpt.owner.enpv = round(
            owner_enpv(project, project.lsOpt.contract, distribution), 6
        )

        project.owner_target_enpv = project.lsOpt.owner.enpv
        project.owner_threshold = project.lsOpt.owner.enpv - project.lsOpt.builder.enpv

        project.lsOpt.builder.risk = round(
            100 * builder_risk(project, project.lsOpt.contract, distribution, 0), 6
        )
        project.lsOpt.owner.risk = round(
            100
            * owner_risk(
                project, project.lsOpt.contract, distribution, project.owner_threshold
            ),
            6,
        )

        project.lsOpt.builder.var = round(
            builder_var(project, project.lsOpt.contract, distribution, 0.05)
            - project.lsOpt.builder.enpv,
            6,
        )
        project.lsOpt.owner.var = round(
            owner_var(project, project.lsOpt.contract, distribution, 0.05)
            - project.lsOpt.owner.enpv,
            6,
        )
