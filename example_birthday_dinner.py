# See:
# https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-825-techniques-in-artificial-intelligence-sma-5504-fall-2002/lecture-notes/Lecture12FinalPart1.pdf

from actions import Action
from planning_problem import PlanningProblem
from functools import partial
from run_search import run_search

from aimacode.search import (
    Node, breadth_first_search, astar_search, depth_first_graph_search,
    uniform_cost_search, greedy_best_first_graph_search, Problem,
)

def bday_dinner_actions(all_fluents):
    return [
        # Action(Cook,
        #    PRECOND: CleanHands
        #    EFFECT:  Dinner
        Action('Cook', all_fluents,
            [['CleanHands'], []],
            [['Dinner'], []]),

        # Action(Wrap,
        #    PRECOND: Quiet
        #    EFFECT:  Present
        Action('Wrap', all_fluents,
            [['Quiet'], []],
            [['Present'], []]),

        # Action(Carry,
        #    PRECOND: Garbage
        #    EFFECT:  ¬ Garbage ∧ ¬ CleanHands
        Action('Carry', all_fluents,
            [['Garbage'], []],
            [[], ['Garbage', 'CleanHands']]),

        # Action(Dolly,
        #    PRECOND: Garbage
        #    EFFECT:  ¬ Garbage ∧ ¬ Quiet
        Action('Dolly', all_fluents,
            [['Garbage'], []],
            [[], ['Garbage', 'Quiet']]),
    ]


def birthday_dinner():
    pos = ['Garbage', 'CleanHands', 'Quiet']
    neg = ['Dinner', 'Present']
    init = (pos, neg)
    goal = [neg, ['Garbage']]

    return PlanningProblem(init, goal, bday_dinner_actions)


if __name__ == '__main__':
    from lp_utils import decode_state

    p = birthday_dinner()
    print("**** Spare Tire example problem setup ****")
    initial = decode_state(p.all_fluents, p.initial)
    print("Initial state for this problem is {}".format(initial))
    print("Actions for this domain are:")
    for a in p.actions_list:
        print('  ', str(a))

    print("Fluents in this problem are:")
    for f in p.all_fluents:
        print('   {}'.format(f))

    print("Goal requirement for this problem are:")
    for g in decode_state(p.all_fluents, p.goal_pos):
        print('   {}'.format(g))
    for g in decode_state(p.all_fluents, p.goal_neg):
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
