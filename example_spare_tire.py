from actions import Action
from planning_problem import PlanningProblem
from functools import partial
from run_search import run_search

from aimacode.search import (
    Node, breadth_first_search, astar_search, depth_first_graph_search,
    uniform_cost_search, greedy_best_first_graph_search, Problem,
)


def spare_tire_actions(tires, locations, all_fluents):
    def remove_actions():
        # Action(Remove(obj, loc),
        #    PRECOND:  At(obj, loc)
        #    EFFECT: ¬ At(obj, loc) ∧ At(obj, Ground)
        actions = []
        for tyre in tires:
            effect_add = ['At(%s, Ground)' % tyre]
            for loc in locations:
                precond_pos = ['At(%s, %s)' % (tyre, loc)]
                remove = Action('Remove(%s, %s)' % (tyre, loc), all_fluents,
                                [precond_pos, []],
                                [effect_add, precond_pos])
                actions.append(remove)
        return actions
        
    def put_on_actions():
        # Action(PutOn(t, Axle),
        #    PRECOND:  Tire(t) ∧ At(t, Ground) ∧  ¬ At(Flat, Axle)
        #    EFFECT: ¬ At(t, Ground) ∧ At(t, Axle)

        # What stops you from putting the Flat back on an Axle, even if the
        # Spare is already there? The fact that a solution will be found
        # before that possibility arises?
        actions = []
        precond_neg = ['At(Flat, Axle)']
        for tyre in tires:
            precond_pos = ['At(%s, Ground)' % tyre]
            effect_add = ['At(%s, Axle)' % tyre]
            put_on = Action('PutOn(%s, Axle)' % tyre, all_fluents,
                            [precond_pos, precond_neg],
                            [effect_add, precond_pos])
            actions.append(put_on)
        return actions

    def leave_overnight_action():
        # Action(LeaveOvernight,
        #    PRECOND:
        #    EFFECT: ¬ At(Spare, Ground) ∧ ¬ At(Spare, Axle)
        #            ¬ At(Spare, Trunk)  ∧ ¬ At(Flat, Ground)
        #            ¬ At(Flat, Axle)    ∧ ¬ At(Flat, Trunk)
        removals = []
        for tyre in tires:
            for loc in locations:
                removals.append('At(%s, %s)' % (tyre, loc))

        leave_overnight = Action('LeaveOvernight', all_fluents,
                                 [[], []],
                                 [[], removals])
        return [leave_overnight]

    return remove_actions() + put_on_actions() + leave_overnight_action()

def spare_tire():
    tires = ['Spare', 'Flat']
    locations = ['Ground', 'Axle', 'Trunk']

    pos = ['At(Flat, Axle)', 'At(Spare, Trunk)']
    neg = ['At(Flat, Ground)', 'At(Flat, Trunk)',
           'At(Spare, Ground)', 'At(Spare, Axle)']
    goal = ['At(Spare, Axle)']
    init = (pos, neg)
    action_fn = partial(spare_tire_actions, tires, locations)
    return PlanningProblem(init, goal, action_fn)


if __name__ == '__main__':
    from lp_utils import decode_state

    p = spare_tire()
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
