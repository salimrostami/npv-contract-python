from typing import TextIO

from source.definit.contract import Contract, calc_rate_uni, calc_reward, calc_salary
from source.definit.initialize import initialize
from source.definit.param import params
from source.definit.project import ExactResults, Project
from source.evaluate.exact_eval import exact_calculations
from source.search.opt_cvar_search import opt_contract_peakfinder
from source.utility.report_writer import sens_cvar_header, sens_cvar_report


def tm_sens_rate_cvar(proj: Project):
    log_file: TextIO = sens_cvar_header(proj, "tm-sens-rate-cvar")
    initialize(proj)
    cont = Contract("tm-sense-cvar", 0, 0, 0, "tm-sense-cvar")
    cont.type = "tm"

    for i in range(10001):
        cont.rate = i / 10000.0
        smax = calc_salary(proj, proj.b_t_enpv, cont.rate, 0)
        smin = max(0.01 * smax, params.minSafeSalary)
        best_salary, _ = opt_contract_peakfinder(proj, cont, "lh", smin, smax)
        cont.salary = best_salary
        cont.reward = max(0, calc_reward(proj, proj.b_t_enpv, cont.rate, best_salary))

        results = ExactResults()
        exact_calculations(proj, cont, results.builder, results.owner, 0, calc_cvar=True)
        sens_cvar_report(cont, results, log_file)


def tm_sens_salary_cvar(proj: Project):
    log_file: TextIO = sens_cvar_header(proj, "tm-sens-salary-cvar")
    initialize(proj)
    cont = Contract("tm-sense-cvar", 0, 0, 0, "tm-sense-cvar")
    cont.type = "tm"
    smax = calc_salary(proj, proj.b_t_enpv, 0, 0)

    for i in range(101):
        salary_percent = i / 100.0
        if salary_percent > 0 and salary_percent * smax < params.minSafeSalary:
            continue

        cont.salary = salary_percent * smax
        nu_max = calc_rate_uni(proj, proj.b_t_enpv, 0, cont.salary)
        best_rate, _ = opt_contract_peakfinder(proj, cont, "cp", 0, nu_max)
        cont.rate = max(best_rate, 0)
        cont.reward = max(0, calc_reward(proj, proj.b_t_enpv, cont.rate, cont.salary))

        results = ExactResults()
        exact_calculations(proj, cont, results.builder, results.owner, 0, calc_cvar=True)
        sens_cvar_report(cont, results, log_file)
