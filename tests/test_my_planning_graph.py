import os
import sys

import unittest
from actions import Action
from example_have_cake import have_cake
from my_planning_graph import PlanningGraph, PgNode_a, PgNode_s, mutexify
from planning_problem import PlanningProblem

class TestPlanningGraphLevels(unittest.TestCase):
    def setUp(self):
        self.p = have_cake()
        self.pg = PlanningGraph(self.p, self.p.initial)

    # @unittest.skip('Skipped test_add_action_level')
    def test_add_action_level(self):
        if 0:
            for level, nodeset in enumerate(self.pg.a_levels):
                for node in nodeset:
                    print("Level {}: {})".format(level, node.action.name))
        self.assertEqual(len(self.pg.a_levels[0]), 3, len(self.pg.a_levels[0]))
        self.assertEqual(len(self.pg.a_levels[1]), 6, len(self.pg.a_levels[1]))

    # @unittest.skip('Skipped test_add_literal_level')
    def test_add_literal_level(self):
        if 0:
            for level, nodeset in enumerate(self.pg.s_levels):
                for node in nodeset:
                    print("Level {}: {})".format(level, repr(node)))
        self.assertEqual(len(self.pg.s_levels[0]), 2, len(self.pg.s_levels[0]))
        self.assertEqual(len(self.pg.s_levels[1]), 4, len(self.pg.s_levels[1]))
        self.assertEqual(len(self.pg.s_levels[2]), 4, len(self.pg.s_levels[2]))


def create_test_actions(all_fluents):
    actions = [
        # na1
        Action('Go(here)', all_fluents,
               [[], []],
               [['At(here)'], []]
        ),
        # na2
        Action('Go(there)', all_fluents,
               [[], []],
               [['At(there)'], []]
        ),
        # na3
        Action('Noop(At(there))', all_fluents,
               [['At(there)'], []],
               [['At(there)'], []]
        ),
        # na4
        Action('Noop(At(here))', all_fluents,
               [['At(here)'], []],
               [['At(here)'], []]
        ),
        # na5
        Action('Reverse(At(here))', all_fluents,
               [['At(here)'], []],
               [[], ['At(here)']]
        ),
        # na6
        Action('Go(everywhere)', all_fluents,
               [[], []],
               [['At(here)', 'At(there)'], []]
        ),
        # na7 - New for competing needs test
        Action('NotHere', all_fluents,
               [[], ['At(here)']],
               [[], []]
        )
    ]
    return actions


class TestPlanningGraphMutex(unittest.TestCase):

    fluents = ['At(here)', 'At(there)']

    def setUp(self):

        init = ([], self.fluents)
        goal = [[],[]]
        test_problem = PlanningProblem(init, goal, create_test_actions)
        self.pg = PlanningGraph(test_problem, test_problem.initial)

        # Create some independent nodes for testing mutexes
        action_nodes = {}
        for i, action in enumerate(test_problem.actions_list):
            name = 'na%d' % (i+1)
            node = PgNode_a(action)
            action_nodes[name] = node
        self.__dict__.update(action_nodes)

        self.ns1 = PgNode_s('At(here)', True)
        self.ns2 = PgNode_s('At(there)', True)
        self.ns3 = PgNode_s('At(here)', False)
        self.ns4 = PgNode_s('At(there)', False)
        self.na1.children.add(self.ns1)
        self.ns1.parents.add(self.na1)
        self.na2.children.add(self.ns2)
        self.ns2.parents.add(self.na2)
        self.na1.parents.add(self.ns3)
        self.na2.parents.add(self.ns4)

    # @unittest.skip('Skipped test_serialize_mutex')
    def test_serialize_mutex(self):
        self.assertTrue(
            PlanningGraph.serialize_actions(self.pg, self.na1, self.na2),
            "Two persistence action nodes not marked as mutex"
        )
        self.assertFalse(
            PlanningGraph.serialize_actions(self.pg, self.na3, self.na4),
            "Two No-Ops were marked mutex"
        )
        self.assertFalse(
            PlanningGraph.serialize_actions(self.pg, self.na1, self.na3),
            "No-op and persistence action incorrectly marked as mutex"
        )

    # @unittest.skip('Skipped test_inconsistent_effects_mutex')
    def test_inconsistent_effects_mutex(self):
        self.assertTrue(
            PlanningGraph.inconsistent_effects_mutex(
                self.pg, self.na4, self.na5),
            "Canceling effects not marked as mutex"
        )
        self.assertFalse(
            PlanningGraph.inconsistent_effects_mutex(
                self.pg, self.na1, self.na2),
            "Non-Canceling effects incorrectly marked as mutex"
        )

    # @unittest.skip('Skipped test_interference_mutex')
    def test_interference_mutex(self):
        self.assertTrue(
            PlanningGraph.interference_mutex(self.pg, self.na4, self.na5),
            "Precondition from one node opposite of effect of other node "
            "should be mutex"
        )
        self.assertTrue(
            PlanningGraph.interference_mutex(self.pg, self.na5, self.na4),
            "Precondition from one node opposite of effect of other node "
            "should be mutex"
        )
        self.assertFalse(
            PlanningGraph.interference_mutex(self.pg, self.na1, self.na2),
            "Non-interfering incorrectly marked mutex"
        )

    # TODO: Need to break these tests up. First part should just be testing an
    # action object, and seeing whether the action mutex identification logic
    # is working properly. Once you've confirmed that is working, THEN you can
    # test the literal mutex checks, which identify mutex relationships among
    # literals based on mutexes between their mutual action parents.

    # @unittest.skip('Skipped test_competing_needs_mutex')
    def test_competing_needs_mutex(self):
        self.assertFalse(
            PlanningGraph.competing_needs_mutex(self.pg, self.na1, self.na2),
            "Non-competing action nodes incorrectly marked as mutex"
        )

    @unittest.skip('Assumptions about data structures no longer valid')
    def test_was_once_part_original_competing_needs_mutex_test(self):
        # This test assumes a data structure where the parent literals are
        # held externally from the action object, in separate nodes, and that
        # the only way to determine if action nodes are mutex is if the nodes'
        # parents were previously identified as such.
        # But with the bitmapped preconditions in the Action class, we can
        # tell directly if there'll be any conflicts - see
        # Action.mutex_competing()
        mutexify(self.ns3, self.ns4)
        self.assertTrue(
            PlanningGraph.competing_needs_mutex(self.pg, self.na1, self.na2),
            "Opposite preconditions from two action nodes not marked as mutex"
        )

    def test_new_competing_needs_mutex(self):
        for node in [self.na4, self.na5]:
            # These nodes require the literal 'At(here)' as a pre-condition,
            # while na7 requires that 'At(here)' NOT be present - classic case
            # of competing needs.
            self.assertTrue(
                PlanningGraph.competing_needs_mutex(self.pg, node, self.na7),
                "Opposing conditions from two action nodes not marked as mutex"
        )

    # @unittest.skip('Skipped test_negation_mutex')
    def test_negation_mutex(self):
        self.assertTrue(
            PlanningGraph.negation_mutex(self.pg, self.ns1, self.ns3),
            "Opposite literal nodes not found to be Negation mutex"
        )
        self.assertFalse(
            PlanningGraph.negation_mutex(self.pg, self.ns1, self.ns2),
            "Same literal nodes found to be Negation mutex"
        )

    # @unittest.skip('Skipped test_inconsistent_support_mutex')
    def test_inconsistent_support_mutex(self):
        self.assertFalse(
            PlanningGraph.inconsistent_support_mutex(
                self.pg, self.ns1, self.ns2),
            "Independent node paths should NOT be inconsistent-support mutex"
        )

        mutexify(self.na1, self.na2)
        self.assertTrue(
            PlanningGraph.inconsistent_support_mutex(
                self.pg, self.ns1, self.ns2),
            "Mutex parent actions should result in inconsistent-support mutex"
        )

        self.na6.children.add(self.ns1)
        self.ns1.parents.add(self.na6)
        self.na6.children.add(self.ns2)
        self.ns2.parents.add(self.na6)
        self.na6.parents.add(self.ns3)
        self.na6.parents.add(self.ns4)
        mutexify(self.na1, self.na6)
        mutexify(self.na2, self.na6)

        self.assertFalse(
            PlanningGraph.inconsistent_support_mutex(
                self.pg, self.ns1, self.ns2),
            "If one parent action can achieve both states, should NOT be "
            "inconsistent-support mutex, even if parent actions are "
            "themselves mutex"
        )


class TestPlanningGraphHeuristics(unittest.TestCase):
    def setUp(self):
        self.p = have_cake()
        self.pg = PlanningGraph(self.p, self.p.initial)

    # @unittest.skip('Skipped test_levelsum')
    def test_levelsum(self):
        self.assertEqual(self.pg.h_levelsum(), 1)


if __name__ == '__main__':
    unittest.main()