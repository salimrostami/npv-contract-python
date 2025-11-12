from source.definit.project import Project
from source.definit.contract import calc_reward, Contract
from source.evaluate.builder.builder_enpv import builder_enpv
from source.evaluate.exact_eval import exact_calculations
from source.evaluate.owner.owner_enpv import owner_enpv
from source.evaluate.simulation import simulate
from source.definit.param import params


def initialize(proj: Project):
    if proj.lsOpt.cont is None:
        Rmax = calc_reward(proj, proj.b_t_enpv, 0, 0)
        lsOpt: Contract = Contract("lsBase", Rmax, 0, 0, "0.0-0.0")
        proj.lsOpt.cont = lsOpt

        proj.lsOpt.builder.enpv = builder_enpv(proj, proj.lsOpt.cont)
        proj.lsOpt.owner.enpv = owner_enpv(proj, proj.lsOpt.cont)

        proj.owner_target_enpv = proj.lsOpt.owner.enpv
        proj.owner_threshold = 0  # proj.lsOpt.owner.enpv - proj.lsOpt.builder.enpv

        exact_calculations(
            proj,
            proj.lsOpt.cont,
            proj.lsOpt.builder,
            proj.lsOpt.owner,
            0,
        )

        proj.lsOpt.tvar = proj.lsOpt.builder.var + proj.lsOpt.owner.var
        params.isSim and simulate(proj, proj.lsOpt.cont, proj.lsOpt.sim_results, 0)
