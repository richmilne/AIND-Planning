from actions import Action
from lp_utils import encode_state, decode_state
from aimacode.search import Node, Problem
from my_planning_graph import PlanningGraph

from functools import lru_cache


class PlanningProblem(Problem):
    def __init__(self, initial, goal, action_fn):
        """
        :param initial: 2-tuple of positive and negative literal fluents,
            describing the initial state of the problem
        :param goal: 2-tuple of positive and negative literal fluents,
            describing the problem's goal state
        :param action_fn: Function which creates all the concrete actions for
            the problem. This function will be passed an ordered, immutable
            reference tuple of all the fluents in the problem. The function
            will only be called once, during class construction."""
        pos, neg = initial
        all_fluents = tuple(sorted(pos+neg))
        initial_state = encode_state(all_fluents, pos)

        # Simpler to encode goal fluents as the pos and neg preconditions of an
        # action, so we can use the Action's precondition check methods.
        self.goal_action = Action('GoalAction', all_fluents, goal,  [[], []])

        self.all_fluents = all_fluents
        # self.initial_state = initial_state - not needed; initial state
        # saved in Parent class as .initial
        Problem.__init__(self, initial_state, goal=goal)

        self.actions_list = action_fn(all_fluents)

    def get_state_fluents(self, state=None):
        """Decode state bitmap into lists of positive and negative fluents.

        If not state is given, decodes current state of this instance."""
        if state is None:
            state = self.initial
        pos = set(decode_state(self.all_fluents, state))
        neg = set(self.all_fluents) - pos
        return (sorted(pos), sorted(neg))

    def actions(self, state: int) -> list:
        """Return the actions that can be executed in the given state.

        :param state: int
            state represented as bitmap of mapped fluents (state
            variables) e.g. 0b011100
        :return: list of Action objects"""
        possible_actions = []
        for action in self.actions_list:
            if action.check_precond(state):
                possible_actions.append(action)
        return possible_actions

    def result(self, state: int, action: Action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state).

        :param state: state entering node
        :param action: Action applied
        :return: resulting state after action"""
        return action(state)

    def goal_test(self, state: int) -> bool:
        """Test the state to see if goal is reached

        :param state: int representing state
        :return: bool"""
        return self.goal_action.check_precond(state)

    def h_1(self, node: Node):
        # note that this is not a true heuristic
        h_const = 1
        return h_const

    @lru_cache(maxsize=8192)
    def h_pg_levelsum(self, node: Node):
        """This heuristic uses a planning graph representation of the problem
        state space to estimate the sum of all actions that must be carried
        out from the current state in order to satisfy each individual goal
        condition."""
        # requires implemented PlanningGraph class
        pg = PlanningGraph(self, node.state)
        pg_levelsum = pg.h_levelsum()
        return pg_levelsum

    @lru_cache(maxsize=8192)
    def h_ignore_preconditions(self, node: Node):
        """This heuristic estimates the minimum number of actions that must be
        carried out from the current state in order to satisfy all of the
        goal conditions by ignoring the preconditions required for an action
        to be executed."""
        # TODO implement (see Russell-Norvig Ed-3 10.2.3  or Russell-Norvig Ed-2 11.2)
        count = 0
        return count