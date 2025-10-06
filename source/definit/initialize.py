from source.definit.project import Project
from source.definit.contract import calc_reward, Contract
from source.evaluate.builder.builder_enpv import builder_enpv
from source.evaluate.exact_eval import exact_calculations
from source.evaluate.owner.owner_enpv import owner_enpv


def initialize(project: Project):
    if project.lsOpt.contract is None:
        Rmax = calc_reward(project, project.builder_target_enpv, 0, 0)
        lsOpt: Contract = Contract("lsBase", Rmax, 0, 0, "0.0-0.0")
        project.lsOpt.contract = lsOpt

        project.lsOpt.builder.enpv = builder_enpv(project, project.lsOpt.contract)
        project.lsOpt.owner.enpv = owner_enpv(project, project.lsOpt.contract)

        project.owner_target_enpv = project.lsOpt.owner.enpv
        project.owner_threshold = project.lsOpt.owner.enpv - project.lsOpt.builder.enpv

        exact_calculations(
            project,
            project.lsOpt.contract,
            project.lsOpt.builder,
            project.lsOpt.owner,
            0,
        )

        project.lsOpt.tvar = project.lsOpt.builder.var + project.lsOpt.owner.var
