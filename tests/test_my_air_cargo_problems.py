import os
import sys
parent = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(os.path.dirname(parent), "aimacode"))
from actions import Action
from aimacode.utils import expr
from aimacode.search import Node
import unittest
from lp_utils import decode_state
from my_air_cargo_problems import (
    air_cargo_p1, air_cargo_p2, air_cargo_p3,
)
from functools import partial

class TestAirCargoProb1(unittest.TestCase):

    def setUp(self):
        self.prob = air_cargo_p1()
        self.decoder = partial(decode_state, self.prob.all_fluents)

        # This is just restating what was given in the sample air_cargo_p1().
        # Original test just checked number of fluents; we're restating problem
        # initialisation so to better illustrate what we expect to be returned,
        # and to test the decode function.
        self.pos_fluents = [
            'At(C1, SFO)', 'At(C2, JFK)', 'At(P1, SFO)', 'At(P2, JFK)',
        ]
        self.neg_fluents = [
            'At(C2, SFO)', 'At(C1, JFK)', 'At(P1, JFK)', 'At(P2, SFO)',
            'In(C2, P1)',  'In(C2, P2)',  'In(C1, P1)',  'In(C1, P2)',
        ]
        self.goals = ['At(C1, JFK)', 'At(C2, SFO)']

    def test_ACP1_num_all_fluents(self):
        all_fluents = set(self.pos_fluents + self.neg_fluents)
        self.assertEqual(all_fluents, set(self.prob.all_fluents))
        self.assertEqual(len(all_fluents), 12)

    def test_ACP1_num_pos_fluents(self):
        initial_pos = set(self.decoder(self.prob.initial))
        self.assertEqual(initial_pos, set(self.pos_fluents))
        self.assertEqual(len(initial_pos), 4)

    def test_ACP1_num_requirements(self):
        goals = set(self.decoder(self.prob.goal))
        self.assertEqual(goals, set(self.goals))
        self.assertEqual(len(goals), 2)


class TestAirCargoProb2(unittest.TestCase):

    def setUp(self):
        self.prob = air_cargo_p2()
        self.decoder = partial(decode_state, self.prob.all_fluents)

    def test_ACP2_num_all_fluents(self):
        self.assertEqual(len(self.prob.all_fluents), 27)

    def test_ACP2_num_pos_fluents(self):
        self.assertEqual(len(self.decoder(self.prob.initial)), 6)

    def test_ACP2_num_requirements(self):
        self.assertEqual(len(self.decoder(self.prob.goal)),3)


class TestAirCargoProb2(unittest.TestCase):

    def setUp(self):
        self.prob = air_cargo_p3()
        self.decoder = partial(decode_state, self.prob.all_fluents)

    def test_ACP3_num_all_fluents(self):
        self.assertEqual(len(self.prob.all_fluents), 32)

    def test_ACP3_num_pos_fluents(self):
        self.assertEqual(len(self.decoder(self.prob.initial)), 6)

    def test_ACP3_num_requirements(self):
        self.assertEqual(len(self.decoder(self.prob.goal)),4)


class TestAirCargoMethods(unittest.TestCase):

    def setUp(self):
        self.p1 = air_cargo_p1()
        self.act1 = Action(
            'Load(C1, P1, SFO)', self.p1.all_fluents,
            [['At(C1, SFO)', 'At(P1, SFO)'], []],
            [['In(C1, P1)'], ['At(C1, SFO)']]
        )

    def test_AC_get_actions(self):
        # to see a list of the actions, uncomment below
        # print("\nAll actions for the problem")
        # for action in self.p1.actions_list:
        #     # print("{}{}".format(action.name, action.args))
        #     print(str(action))
        # action.__str__() was originally defined as
        # "{}{}".format(action.name, action.args)) ... so just use str()!
        self.assertEqual(len(self.p1.actions_list), 20)

    def test_AC_actions(self):
        # to see list of possible actions, uncomment below
        # print("\nActions possible from initial state:")
        # for action in self.p1.actions(self.p1.initial):
        #     print(str(action))
        self.assertEqual(len(self.p1.actions(self.p1.initial)), 4)

    def test_AC_result(self):
        kb = self.p1.result(self.p1.initial, self.act1)
        fluents = decode_state(self.p1.all_fluents, kb)
        self.assertTrue('In(C1, P1)' in fluents)
        self.assertTrue('At(C1, SFO)' not in fluents)

    @unittest.skip("Skip h_ignore_preconditions test.")
    def test_h_ignore_preconditions(self):
        n = Node(self.p1.initial)
        self.assertEqual(self.p1.h_ignore_preconditions(n),2)

if __name__ == '__main__':
    unittest.main()