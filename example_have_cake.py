from actions import Action
from aimacode.search import (
    Node, breadth_first_search, astar_search, depth_first_graph_search,
    uniform_cost_search, greedy_best_first_graph_search, Problem,
)
from lp_utils import encode_state, decode_state
from my_planning_graph import PlanningGraph
from run_search import run_search

from functools import lru_cache


class HaveCakeProblem(Problem):
    def __init__(self, initial, goal: list):
        pos, neg = initial
        all_fluents = tuple(sorted(pos+neg))
        initial_state = encode_state(all_fluents, pos)
        goal = encode_state(all_fluents, goal)

        self.all_fluents = all_fluents
        self.initial_state = initial_state
        Problem.__init__(self, initial_state, goal=goal)

        self.actions_list = self.get_actions()

    def get_actions(self):
        precond_pos = ["Have(Cake)"]
        precond_neg = []
        effect_add = ["Eaten(Cake)"]
        effect_rem = ["Have(Cake)"]
        eat_action = Action("Eat(Cake)", self.all_fluents,
                            [precond_pos, precond_neg],
                            [effect_add, effect_rem])

        precond_pos = []
        precond_neg = ["Have(Cake)"]
        effect_add = ["Have(Cake)"]
        effect_rem = []
        bake_action = Action("Bake(Cake)", self.all_fluents,
                             [precond_pos, precond_neg],
                             [effect_add, effect_rem])
        return [eat_action, bake_action]

    def actions(self, state: int) -> list:  # of Action
        possible_actions = []

        for action in self.actions_list:
            if action.check_precond(state):
                possible_actions.append(action)
        return possible_actions

    def result(self, state: int, action: Action):
        return action(state)

    def goal_test(self, state: str) -> bool:
        return self.goal & state == self.goal

    def h_1(self, node: Node):
        # note that this is not a true heuristic
        h_const = 1
        return h_const

    @lru_cache(maxsize=8192)
    def h_pg_levelsum(self, node: Node):
        # uses the planning graph level-sum heuristic calculated
        # from this node to the goal
        # requires implementation in PlanningGraph
        pg = PlanningGraph(self, node.state)
        pg_levelsum = pg.h_levelsum()
        return pg_levelsum

    @lru_cache(maxsize=8192)
    def h_ignore_preconditions(self, node: Node):
        # not implemented
        count = 0
        return count


def have_cake():
    pos = ['Have(Cake)']
    neg = ['Eaten(Cake)']
    goal = ['Have(Cake)', 'Eaten(Cake)']

    init = (pos, neg)
    return HaveCakeProblem(init, goal)


if __name__ == '__main__':
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
    for g in decode_state(p.all_fluents, p.goal):
        print('   {}'.format(g))
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