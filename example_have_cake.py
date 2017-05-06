from actions import Action
from planning_problem import PlanningProblem
from functools import partial
from run_search import run_search

from aimacode.search import (
    Node, breadth_first_search, astar_search, depth_first_graph_search,
    uniform_cost_search, greedy_best_first_graph_search, Problem,
)


def cake_actions(all_fluents):
    precond_pos = ["Have(Cake)"]
    precond_neg = []
    effect_add = ["Eaten(Cake)"]
    effect_rem = ["Have(Cake)"]
    eat_action = Action("Eat(Cake)", all_fluents,
                        [precond_pos, precond_neg],
                        [effect_add, effect_rem])

    precond_pos = []
    precond_neg = ["Have(Cake)"]
    effect_add = ["Have(Cake)"]
    effect_rem = []
    bake_action = Action("Bake(Cake)", all_fluents,
                         [precond_pos, precond_neg],
                         [effect_add, effect_rem])
    return [eat_action, bake_action]


def have_cake():
    pos = ['Have(Cake)']
    neg = ['Eaten(Cake)']
    goal = [['Have(Cake)', 'Eaten(Cake)'], []]
    init = (pos, neg)
    return PlanningProblem(init, goal, cake_actions)

if __name__ == '__main__':
    from lp_utils import decode_state

    p = have_cake()
    print("**** Have Cake example problem setup ****")
    initial = decode_state(p.all_fluents, p.initial)
    print("Initial state for this problem is {}".format(initial))
    print("Actions for this domain are:")
    for a in p.actions_list:
        print('  ', str(a))

    print("Fluents in this problem are:")
    for f in p.all_fluents:
        print('   {}'.format(f))

    print("Goal requirement for this problem are:")
    for g in decode_state(p.all_fluents, p.goal_action.precond_pos):
        print('   {}'.format(g))
    for g in decode_state(p.all_fluents, p.goal_action.precond_neg):
        print('  ~{}'.format(g))

    print()
    print("*** Breadth First Search")
    run_search(p, breadth_first_search)
    print("*** Depth First Search")
    run_search(p, depth_first_graph_search)
    print("*** Uniform Cost Search")
    run_search(p, uniform_cost_search)
    print("*** Greedy Best First Graph Search - null heuristic")
    run_search(p, greedy_best_first_graph_search, parameter=p.h_1)
    print("*** A-star null heuristic")
    run_search(p, astar_search, p.h_1)
    # print("A-star ignore preconditions heuristic")
    # rs(p, "astar_search - ignore preconditions heuristic", astar_search, p.h_ignore_preconditions)
    # print(""A-star levelsum heuristic)
    # rs(p, "astar_search - levelsum heuristic", astar_search, p.h_pg_levelsum)
