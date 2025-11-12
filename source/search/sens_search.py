from source.definit.initialize import initialize
from source.definit.contract import Contract, calc_rate_uni, calc_reward, calc_salary
from source.definit.project import Project, ExactResults
from source.evaluate.exact_eval import exact_calculations
from source.search.opt_search import opt_contract_peakfinder
import numpy as np
from source.definit.param import params
from source.utility.report_writer import sens_header, sens_report
from pyparsing import TextIO


def tm_sens_rate(proj: Project):
    log_file: TextIO = sens_header(proj, "tm-sens-rate")
    initialize(proj)
    cont = Contract("tm-sense", 0, 0, 0, "tm-sense")
    cont.type = "tm"
    for nu in np.arange(0.0, 1.009, 0.01):
        cont.rate = nu
        Smax = calc_salary(proj, proj.b_t_enpv, cont.rate, 0)
        Smin = max(0.01 * Smax, params.minSafeSalary)
        best_salary, _ = opt_contract_peakfinder(proj, cont, "lh", Smin, Smax)
        cont.salary = best_salary
        best_R = calc_reward(proj, proj.b_t_enpv, cont.rate, best_salary)
        cont.reward = max(0, best_R)
        results: ExactResults = ExactResults()
        exact_calculations(proj, cont, results.builder, results.owner, 0)
        sens_report(cont, results, log_file)


def tm_sens_salary(proj: Project):
    log_file: TextIO = sens_header(proj, "tm-sens-salary")
    initialize(proj)
    cont = Contract("tm-sense", 0, 0, 0, "tm-sense")
    cont.type = "tm"
    Smax = calc_salary(proj, proj.b_t_enpv, 0, 0)
    for sp in np.arange(0.0, 1.009, 0.01):
        if sp > 0 and sp * Smax < params.minSafeSalary:
            continue
        cont.salary = sp * Smax
        nu_max = calc_rate_uni(proj, proj.b_t_enpv, 0, cont.salary)
        x, y = opt_contract_peakfinder(proj, cont, "cp", 0, nu_max)
        cont.rate = max(x, 0)
        cont.reward = calc_reward(proj, proj.b_t_enpv, cont.rate, cont.salary)
        cont.reward = max(0, cont.reward)
        results: ExactResults = ExactResults()
        exact_calculations(proj, cont, results.builder, results.owner, 0)
        sens_report(cont, results, log_file)
