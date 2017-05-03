from actions import Action
from planning_problem import PlanningProblem
from functools import partial

def air_cargo_actions(cargos, planes, airports, all_fluents):
    """
    This method creates concrete actions (no variables) for all actions in
    the in the problem domain action schema and turns them into complete
    Action objects as defined in the aimacode.planning module. It is
    computationally expensive to call this method directly; however, it is
    called by the constructor and the results cached in the `actions_list`
    property.

    Returns:
    ----------
    list<Action>
        list of Action objects"""
    # TODO create concrete Action objects based on the domain action schema
    # for: Load, Unload, and Fly
    # Concrete actions definition: specific literal action that does not
    # include variables as with the schema. For example, the action schema
    # 'Load(c, p, a)' can represent the concrete actions 'Load(C1, P1, SFO)'
    # or 'Load(C2, P2, JFK)'. The actions for the planning problem must be
    # concrete because the problems in forward search and Planning Graphs
    # must use Propositional Logic

    def load_actions():
        """Create all concrete Load actions and return a list

        :return: list of Action objects"""
        # Action(Load(c, p, a),
        #    PRECOND: At(c, a) ∧ At(p, a) ∧ Cargo(c) ∧ Plane(p) ∧ Airport(a)
        #    EFFECT: ¬ At(c, a) ∧ In(c, p)
        loads = []
        for cargo in cargos:
            for plane in planes:
                for airport in airports:
                    precond = ['At(%s, %s)' % (cargo, airport)]
                    precond.append('At(%s, %s)' % (plane, airport))
                    effect_add = ['In(%s, %s)' % (cargo, plane)]
                    effect_rem = ['At(%s, %s)' % (cargo, airport)]
                    load = 'Load(%s, %s, %s)' % (cargo, plane, airport)
                    action = Action(load, all_fluents,
                                    [precond, []],
                                    [effect_add, effect_rem])
                    loads.append(action)
        return loads

    def unload_actions():
        """Create all concrete Unload actions and return a list

        :return: list of Action objects"""
        # Action(Unload(c, p, a),
        #    PRECOND: In(c, p) ∧ At(p, a) ∧ Cargo(c) ∧ Plane(p) ∧ Airport(a)
        #    EFFECT: At(c, a) ∧ ¬ In(c, p)
        unloads = []
        for cargo in cargos:
            for plane in planes:
                for airport in airports:
                    precond = ['In(%s, %s)' % (cargo, plane)]
                    precond.append('At(%s, %s)' % (plane, airport))
                    effect_rem = ['In(%s, %s)' % (cargo, plane)]
                    effect_add = ['At(%s, %s)' % (cargo, airport)]
                    unload = 'Unload(%s, %s, %s)' % (cargo, plane, airport)
                    action = Action(unload, all_fluents,
                                    [precond, []],
                                    [effect_add, effect_rem])
                    unloads.append(action)
        return unloads

    def fly_actions():
        """Create all concrete Fly actions and return a list

        :return: list of Action objects"""
        # Action(Fly(p, from, to),
        #    PRECOND: At(p, from) ∧ Plane(p) ∧ Airport(from) ∧ Airport(to)
        #    EFFECT: ¬ At(p, from) ∧ At(p, to)
        flys = []
        for fr in airports:
            for to in airports:
                if fr != to:
                    for p in planes:
                        precond_pos = ["At({}, {})".format(p, fr)]
                        precond_neg = []
                        effect_add = ["At({}, {})".format(p, to)]
                        effect_rem = ["At({}, {})".format(p, fr)]
                        fly = Action("Fly({}, {}, {})".format(p, fr, to),
                                     all_fluents,
                                     [precond_pos, precond_neg],
                                     [effect_add, effect_rem])
                        flys.append(fly)
        return flys

    return load_actions() + unload_actions() + fly_actions()


def air_cargo_p1() -> PlanningProblem:
    cargos = ['C1', 'C2']
    planes = ['P1', 'P2']
    airports = ['JFK', 'SFO']
    pos = ['At(C1, SFO)',
           'At(C2, JFK)',
           'At(P1, SFO)',
           'At(P2, JFK)',
           ]
    neg = ['At(C2, SFO)',
           'In(C2, P1)',
           'In(C2, P2)',
           'At(C1, JFK)',
           'In(C1, P1)',
           'In(C1, P2)',
           'At(P1, JFK)',
           'At(P2, SFO)',
           ]
    init = (pos, neg)
    goal = [['At(C1, JFK)',
             'At(C2, SFO)'], []]
    action_fn = partial(air_cargo_actions, cargos, planes, airports)
    return PlanningProblem(init, goal, action_fn)


def cross_product(function, objects1, objects2):
    products = []
    for obj1 in objects1:
        for obj2 in objects2:
            products.append('%s(%s, %s)' % (function, obj1, obj2))
    return set(products)


def create_problem(cargos, planes, airports, pos_cargos, pos_planes, goals):
    all_cargos = cross_product('At', cargos, airports)
    neg_cargos = all_cargos - set(pos_cargos)

    all_planes = cross_product('At', planes, airports)
    neg_planes = all_planes - set(pos_planes)

    neg_loads = cross_product('In', cargos, planes)

    expr_list = [
        pos_cargos + pos_planes,
        sorted(sum([list(n) for n in [neg_cargos, neg_planes, neg_loads]], [])),
        goals
    ]
    pos, neg, goals = expr_list

    if 0:
        for label, obj in [('pos', pos), ('neg', neg), ('goals', goals)]:
            print()
            print(label+':')
            print(type(obj[0]), obj)

    init = (pos, neg)
    action_fn = partial(air_cargo_actions, cargos, planes, airports)
    return PlanningProblem(init, goals, action_fn)


def air_cargo_p2() -> PlanningProblem:
    cargos = ['C1', 'C2', 'C3']
    planes = ['P1', 'P2', 'P3']
    airports = ['JFK', 'SFO', 'ATL']

    pos_cargos = ['At(C1, SFO)', 'At(C2, JFK)', 'At(C3, ATL)']
    pos_planes = ['At(P1, SFO)', 'At(P2, JFK)', 'At(P3, ATL)']

    goals = [['At(C1, JFK)', 'At(C2, SFO)', 'At(C3, SFO)'], []]

    args = (cargos, planes, airports, pos_cargos, pos_planes, goals)
    return create_problem(*args)


def air_cargo_p3() -> PlanningProblem:
    cargos = ['C1', 'C2', 'C3', 'C4']
    planes = ['P1', 'P2']
    airports = ['JFK', 'SFO', 'ATL', 'ORD']

    pos_cargos = ['At(C1, SFO)', 'At(C2, JFK)', 'At(C3, ATL)', 'At(C4, ORD)']
    pos_planes = ['At(P1, SFO)', 'At(P2, JFK)']

    goals = [['At(C1, JFK)', 'At(C3, JFK)', 'At(C2, SFO)', 'At(C4, SFO)'], []]

    args = (cargos, planes, airports, pos_cargos, pos_planes, goals)
    return create_problem(*args)
