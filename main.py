from full_search import full_search
from opt_search import cp_opt_r
from project import all_projects, projects

dist = "uni"
simRounds = 100000
isSim = False
isFullSearch = True


def main():
    all_projects()
    isFullSearch and full_search(dist, isSim, simRounds)
    for proj in projects:
        optimal_cp_r, optimal_cp_tvar = cp_opt_r(proj, dist, 0.000001)
        print(f"Optimal CP r: {optimal_cp_r}, Total VaR: {optimal_cp_tvar}")
        print("End of the program.")


if __name__ == "__main__":
    main()
