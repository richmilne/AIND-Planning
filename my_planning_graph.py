from actions import Action
from aimacode.search import Problem
from lp_utils import decode_state, encode_state, check_precond_subset
from functools import reduce, partial

class PgNode():
    """Base class for planning graph nodes.

    Includes instance sets common to both types of nodes used in a planning
    graph
    parents: the set of nodes in the previous level
    children: the set of nodes in the subsequent level
    mutex: the set of sibling nodes that are mutually exclusive with this
        node
    """

    def __init__(self):
        self.parents = set()
        self.children = set()
        self.mutex = set()

    def is_mutex(self, other) -> bool:
        """Boolean test for mutual exclusion

        :param other: PgNode
            the other node to compare with
        :return: bool
            True if this node and the other are marked mutually exclusive
            (mutex)
        """
        if other in self.mutex:
            return True
        return False

    def show(self):
        """Helper print for debugging shows counts of parents, children and
        siblings

        :return:
            print only
        """
        print("{} parents".format(len(self.parents)))
        print("{} children".format(len(self.children)))
        print("{} mutex".format(len(self.mutex)))


class PgNode_s(PgNode):
    """A planning graph node representing a state (literal fluent) from a
    planning problem.

    Args:
    ----------
    symbol : str
        A string representing a literal expression from a planning problem
        domain.

    is_pos : bool
        Boolean flag indicating whether the literal expression is positive
        or negative."""

    def __init__(self, symbol: str, is_pos: bool):
        """S-level Planning Graph node constructor

        :param symbol: expr
        :param is_pos: bool

        Instance variables calculated:
        literal: expr
            fluent in its literal form (including negative operator if
            applicable.)

        Instance variables inherited from PgNode:
            parents: set of nodes connected to this node in previous
                A-level; initially empty
            children: set of nodes connected to this node in next A-level;
                initially empty
            mutex: set of sibling S-nodes that this node has mutual
                exclusion with; initially empty

        """
        PgNode.__init__(self)
        self.symbol = symbol
        self.is_pos = is_pos
        self.__hash = None

    def show(self):
        """Helper print for debugging shows literal, plus counts of parents,
        children and siblings

        :return:
            print only
        """
        if self.is_pos:
            print("\n***  {}".format(self.symbol))
        else:
            print("\n*** ~{}".format(self.symbol))
        PgNode.show(self)

    def __repr__(self):
        sign = ' ' if self.is_pos else '~'
        return sign + self.symbol

    def __eq__(self, other):
        """Equality test for nodes - compares only the literal for equality

        :param other: PgNode_s
        :return: bool
        """
        return (isinstance(other, self.__class__) and
                self.is_pos == other.is_pos and
                self.symbol == other.symbol)

    def __hash__(self):
        self.__hash = self.__hash or hash(self.symbol) ^ hash(self.is_pos)
        return self.__hash


class PgNode_a(PgNode):
    """A-type (action) Planning Graph node - inherited from PgNode"""

    def __init__(self, action: Action):
        """A-level Planning Graph node constructor

        :param action: Action
            a ground action, i.e. this action cannot contain any variables

        Instance variables calculated:
            An A-level will always have an S-level as its parent and an
            S-level as its child. The preconditions and effects will become
            the parents and children of the A-level node. However, when this
            node is created, it is not yet connected to the graph.
            prenodes: set of *possible* parent S-nodes
            effnodes: set of *possible* child S-nodes
            is_persistent: bool   True if this is a persistence action, i.e.
            a no-op action

        Instance variables inherited from PgNode:
            parents: set of nodes connected to this node in previous
                S-level; initially empty
            children: set of nodes connected to this node in next S-level;
                initially empty
            mutex: set of sibling A-nodes that this node has mutual
                exclusion with; initially empty
        """
        PgNode.__init__(self)
        self.action = action
        #self.prenodes = self.precond_s_nodes()
        #self.effnodes = self.effect_s_nodes()
        self.is_persistent_ = None
        self.__hash = None

    @property
    def is_persistent(self):
        if self.is_persistent_ is None:
            # A persistence, or maintenance, action, is one where the action
            # has EITHER
            # 1. A literal as a positive precondition, with the same literal as
            #    the additive effect, OR
            # 2. A literal as a negative precondition, with the same literal
            #    removed in the effects.
            # Additionally, judging from what we've read and seen in examples,
            # the action should only cover ONE literal.
            pos, neg = self.action.precond_pos, self.action.precond_neg
            add, rem = self.action.effect_add, self.action.effect_rem
            pos_add = pos and (pos == add) and (neg == rem == 0)
            neg_rem = neg and (neg == rem) and (pos == add == 0)
            check = pos_add ^ neg_rem
            if check:
                combined = pos + neg
                one_bit_check = sum([int(n) for n in bin(combined)[2:]]) == 1
                check = check and one_bit_check
            self.is_persistent_ = check
            # self.is_persistent_ = check and self.action.name[0] in '+-'
        return self.is_persistent_


    def show(self):
        """Helper print for debugging shows action, plus counts of parents,
        children and siblings

        :return:
            print only
        """
        print("\n*** {!s}".format(self.action))
        PgNode.show(self)

    def precond_s_nodes(self):
        """Precondition literals as S-nodes.

        Represents possible parents for this node. It is computationally
        expensive to call this function; it is only called by the class
        constructor to populate the `prenodes` attribute.

        :return: set of PgNode_s
        """
        raise NotImplementedError(
            'This functionality performed in PlanningGraph.add_action_level()'
        )
        nodes = set()
        # for p in self.action.precond_pos:
        #     nodes.add(PgNode_s(p, True))
        # for p in self.action.precond_neg:
        #     nodes.add(PgNode_s(p, False))
        for p in self.action.expand_bitmap(self.action.precond_pos):
            nodes.add(PgNode_s(p, True))
        for p in self.action.expand_bitmap(self.action.precond_neg):
            nodes.add(PgNode_s(p, False))

        return nodes

    def effect_s_nodes(self):
        """Effect literals as S-nodes.

        Represents possible children for this node. It is computationally
        expensive to call this function; it is only called by the class
        constructor to populate the `effnodes` attribute.

        :return: set of PgNode_s
        """
        raise NotImplementedError(
            'This functionality performed in PlanningGraph.add_action_level()'
        )
        nodes = set()
        for e in self.action.expand_bitmap(self.action.effect_add):
            nodes.add(PgNode_s(e, True))
        for e in self.action.expand_bitmap(self.action.effect_rem):
            nodes.add(PgNode_s(e, False))

        return nodes

    def __eq__(self, other):
        """Equality test for nodes - compares only the action name for equality

        :param other: PgNode_a
        :return: bool
        """
        return (isinstance(other, self.__class__) and
                self.is_persistent == other.is_persistent and
                self.action.name == other.action.name # and
                # self.action.args == other.action.args
                )

    def __repr__(self):
        return self.action.name

    def __hash__(self):
        self.__hash = (self.__hash or hash(self.action.name))
        return self.__hash


def mutexify(node1: PgNode, node2: PgNode):
    """Adds sibling nodes to each other's mutual exclusion (mutex) set.

    The two nodes must be sibling nodes!

    :param node1: PgNode (or inherited PgNode_a, PgNode_s types)
    :param node2: PgNode (or inherited PgNode_a, PgNode_s types)
    :return:
        node mutex sets modified
    """
    if type(node1) != type(node2):
        raise TypeError('Attempted to mutex two nodes of different types')
    node1.mutex.add(node2)
    node2.mutex.add(node1)


class PlanningGraph():
    """
    A planning graph as described in chapter 10 of the AIMA text. The
    planning graph can be used to reason about...
    """

    def __init__(self, problem: Problem, state: int, serial_planning=True):
        """
        :param problem: PlanningProblem (or subclass such as AirCargoProblem
            or HaveCakeProblem)
        :param state: int (will be in form 0b011010... representing fluent
            states)
        :param serial_planning: bool (whether or not to assume that only one
            action can occur at a time)

        Instance variable calculated:
            fs: ([pos_fluents], [neg_fluents])
                the state represented as positive and negative fluent
                literal lists
            all_actions: list of the PlanningProblem valid ground actions
                combined with calculated no-op actions
            s_levels: list of sets of PgNode_s, where each set in the list
                represents an S-level in the planning graph
            a_levels: list of sets of PgNode_a, where each set in the list
                represents an A-level in the planning graph
        """
        self.problem = problem
        self.decode_state = partial(decode_state, problem.all_fluents)
        self.encode_state = partial(encode_state, problem.all_fluents)
        self.fs = problem.get_state_fluents(state)
        self.serial = serial_planning

        noop_actions = self.noop_actions(self.problem.all_fluents)
        self.all_actions = self.problem.actions_list + noop_actions

        self.s_levels = []
        self.a_levels = []
        self.create_graph()

    def noop_actions(self, all_fluents):
        """Create persistent actions for each possible fluent

        "No-Op" actions are virtual actions (i.e., actions that only exist in
        the planning graph, not in the planning problem domain) that operate
        on each fluent (literal expression) from the problem domain. No-op
        actions "pass through" the literal expressions from one level of the
        planning graph to the next.

        The no-op action list requires both a positive and a negative action
        for each literal expression. Positive no-op actions require the literal
        as a positive precondition and add the literal expression as an effect
        in the output, and negative no-op actions require the literal as a
        negative precondition and remove the literal expression as an effect in
        the output.

        This function should only be called by the class constructor.

        :param all_fluents: All the fluents in the current problem
        :return: list of Action
        """
        action_list = []

        for fluent in all_fluents:
            action_list.append(
                Action('+NoOp(%s)' % fluent, all_fluents,
                [[fluent], []],
                [[fluent], []])
            )
            action_list.append(
                Action('-NoOp(%s)' % fluent, all_fluents,
                [[], [fluent]],
                [[], [fluent]])
            )

        return action_list

    def create_graph(self):
        """Build a Planning Graph as described in Russell-Norvig 3rd Ed 10.3,
        or 2nd Ed 11.4

        The S0 initial level has been implemented for you. It has no parents
        and includes all of the literal fluents that are part of the initial
        state passed to the constructor. At the start of a problem planning
        search, this will be the same as the initial state of the problem.
        However, the planning graph can be built from any state in the
        Planning Problem

        This function should only be called by the class constructor.

        :return:
            builds the graph by filling s_levels[] and a_levels[] lists with
            node sets for each level
        """
        # The graph should only be built during class construction
        if (len(self.s_levels) != 0) or (len(self.a_levels) != 0):
            raise Exception('Planning Graph already created; construct a new '
                            'planning graph for each new state in the planning '
                            'sequence')

        # Initialize S0 to literals in initial state provided.
        leveled = False
        level = 0
        self.s_levels.append(set())  # S0 set of s_nodes - empty to start
        # For each fluent in the initial state, add correct literal PgNode_s
        for literal in self.fs[0]:
            self.s_levels[level].add(PgNode_s(literal, True))
        for literal in self.fs[1]:
            self.s_levels[level].add(PgNode_s(literal, False))

        # No mutexes at the first level

        # Continue to build the graph alternating A, S-levels until last two
        # S-levels contain the same literals
        # i.e. until it is "leveled"
        while not leveled:
            self.add_action_level(level)
            self.update_a_mutex(self.a_levels[level])

            level += 1
            self.add_literal_level(level)
            self.update_s_mutex(self.s_levels[level])

            if self.s_levels[level] == self.s_levels[level - 1]:
                leveled = True

    def get_level_state(self, level):
        """Return the state of the pos, neg fluents at the given level"""
        pos_fluents = []
        neg_fluents = []
        for node in self.s_levels[level]:
            if node.is_pos:
                pos_fluents.append(node.symbol)
            else:
                neg_fluents.append(node.symbol)

        pos_state = self.encode_state(pos_fluents)
        neg_state = self.encode_state(neg_fluents)

        return pos_state, neg_state

    def return_matching_actions(self, pos_state, neg_state):
        applicable_actions = []
        for action in self.all_actions:
            precond_pos, precond_neg = action.precond_pos, action.precond_neg
            pos = check_precond_subset(precond_pos, pos_state)
            neg = check_precond_subset(precond_neg, neg_state)
            if pos and neg:
                applicable_actions.append(action)
        return applicable_actions

    def add_action_level(self, level):
        """Add an A (action) level to the Planning Graph

        :param level: int
            The level number alternates S0, A0, S1, A1, S2... and so on.
            The level number is also used as the index for the node set lists
            self.a_levels[] and self.s_levels[]
        :return:
            Adds A-nodes to the current level in self.a_levels[level]
        """
        # TODO: Add action A level to the planning graph as described in the
        #      Russell-Norvig text
        # 1. Determine what actions to add and create those PgNode_a objects
        # 2. Connect the nodes to the previous S-literal level.
        #    For example, the A0 level will iterate through all possible
        #    actions for the problem and add a PgNode_a to a_levels[0]
        #    set iff all prerequisite literals for the action hold in S0.
        #    This can be accomplished by testing to see if a proposed PgNode_a
        #    has prenodes that are a subset of the previous S level.
        #    Once an action node is added, it MUST be connected to the S node
        #    instances in the appropriate s_level set.

        # 1. Get the state representation of this level
        s_nodes_dict = dict([(hash(n), n) for n in self.s_levels[level]])
        # TODO: You really must store the literal nodes at each level in a
        # directory, not a set, so you don't have to re-process the nodes at
        # each level. This will also make other lookups (such as the one in the
        # levelsum function) quicker and easier.

        # You can use PgNode_s in set([<PgNode_s>]) - which only tells you
        # the node is in the set, but doesn't give you a reference to the actual
        # node object in the set - and you need the reference to the object in
        # the set (not the temporary one you created, which lacks all parent,
        # child and mutex references) to store as a parent/child.

        # print('Current nodes dict:')
        # for item in sorted(s_nodes_dict.items()):
        #     print(item)
        pos_state, neg_state = self.get_level_state(level)

        # 2. Find all actions whose preconditions match the state of this level.
        actions = self.return_matching_actions(pos_state, neg_state)

        # Create new set to hold the A-nodes at this level
        self.a_levels.append(set())

        # 3. For each action, find all the S-nodes which match the pre-
        #    conditions of that action.
        for action in actions:
            a_node = PgNode_a(action)
            for sign, bitmap in [(True, action.precond_pos),
                                (False, action.precond_neg)]:
                for fluent in self.decode_state(bitmap):
                    temp_s_node = PgNode_s(fluent, sign)
                    s_node = s_nodes_dict[hash(temp_s_node)]
                    # Wire up the s- and a-nodes
                    a_node.parents.add(s_node)
                    s_node.children.add(a_node)
            self.a_levels[level].add(a_node)

    def add_literal_level(self, level):
        """Add an S (literal) level to the Planning Graph

        :param level: int
            The level number alternates S0, A0, S1, A1, S2... and so on.
            The level number is also used as the index for the node set lists
            self.a_levels[] and self.s_levels[]
        :return:
            adds S-nodes to the current level in self.s_levels[level]
        """
        # TODO: Add literal S level to the planning graph as described in the
        #       Russell-Norvig text
        # 1. Determine what literals to add
        # 2. Connect the nodes.
        #    For example, every A node in the previous level has a list of
        #    S-nodes in effnodes that represent the effect produced by the
        #    action. These literals will all be part of the new S-level.
        #    Since we are working with sets, they may be "added" to the set
        #    without fear of duplication. However, it is important to then
        #    correctly create and connect all of the new S-nodes as children
        #    of all the A-nodes that could produce them, and likewise add the
        #    A-nodes to the parent sets of the S-nodes
        self.s_levels.append(set())
        for a_node in self.a_levels[level-1]:
            for sign, bitmap in [(True, a_node.action.effect_add),
                                (False, a_node.action.effect_rem)]:
                for fluent in self.decode_state(bitmap):
                    s_node = PgNode_s(fluent, sign)
                    s_node.parents.add(a_node)
                    a_node.children.add(s_node)
                    self.s_levels[level].add(s_node)


    def update_a_mutex(self, nodeset):
        """Determine and update sibling mutual exclusion for A-level nodes

        Mutex action tests section from 3rd Ed. 10.3 or 2nd Ed. 11.4
        A mutex relation holds between two actions a given level if the
        planning graph is a serial planning graph and the pair are non-
        persistence actions, or if any of the three conditions hold between
        the pair:
           Inconsistent Effects
           Interference
           Competing needs

        :param nodeset: set of PgNode_a (siblings in the same level)
        :return:
            mutex set in each PgNode_a in the set is appropriately updated
        """
        nodelist = list(nodeset)
        for i, n1 in enumerate(nodelist[:-1]):
            for n2 in nodelist[i + 1:]:
                check = (self.serialize_actions(n1, n2) or
                         self.inconsistent_effects_mutex(n1, n2) or
                         self.interference_mutex(n1, n2) or
                         self.competing_needs_mutex(n1, n2))
                if check:
                    mutexify(n1, n2)

    def serialize_actions(self, node_a1: PgNode_a, node_a2: PgNode_a) -> bool:
        """Test a pair of actions for serial mutual exclusion

        Returns True if the planning graph is serial, and if either action is
        persistent; otherwise return False. Two serial actions are mutually
        exclusive if they are both non-persistent.

        :param node_a1: PgNode_a
        :param node_a2: PgNode_a
        :return: bool
        """
        if not self.serial:
            return False
        if node_a1.is_persistent or node_a2.is_persistent:
            return False
        return True

    def inconsistent_effects_mutex(self, node_a1: PgNode_a, node_a2: PgNode_a) -> bool:
        """Test a pair of actions for inconsistent effects

        Returns True if one action negates an effect of the other, and False
        otherwise.

        :param node_a1: PgNode_a
        :param node_a2: PgNode_a
        :return: bool
        """
        # TODO test for Inconsistent Effects between nodes

        # HINT: The Action instance associated with an action node is
        # accessible through the PgNode_a.action attribute. See the Action
        # class documentation for details on accessing the effects and
        # preconditions of an action.
        return node_a1.action.mutex_inconsistent_effects(node_a2.action)

    def interference_mutex(self, node_a1: PgNode_a, node_a2: PgNode_a) -> bool:
        """Test a pair of actions for interfering mutual exclusion

        Returns True if the effect of one action is the negation of a
        precondition of the other.

        :param node_a1: PgNode_a
        :param node_a2: PgNode_a
        :return: bool
        """
        # TODO test for Interference between nodes

        # HINT: The Action instance associated with an action node is
        # accessible through the PgNode_a.action attribute. See the Action
        # class documentation for details on accessing the effects and
        # preconditions of an action.
        return node_a1.action.mutex_interference(node_a2.action)

    def competing_needs_mutex(self, node_a1: PgNode_a, node_a2: PgNode_a) -> bool:
        """Test a pair of actions for competing mutual exclusion

        Returns True if one of the preconditions of one action is mutex with
        a precondition of the other action.

        :param node_a1: PgNode_a
        :param node_a2: PgNode_a
        :return: bool
        """
        return node_a1.action.mutex_competing(node_a2.action)

    def update_s_mutex(self, nodeset: set):
        """Determine and update sibling mutual exclusion for S-level nodes

        Mutex action tests section from 3rd Ed. 10.3 or 2nd Ed. 11.4
        A mutex relation holds between literals at a given level
        if either of the two conditions hold between the pair:
           Negation
           Inconsistent support

        :param nodeset: set of PgNode_a (siblings in the same level)
        :return:
            mutex set in each PgNode_a in the set is appropriately updated
        """
        nodelist = list(nodeset)
        for i, n1 in enumerate(nodelist[:-1]):
            for n2 in nodelist[i + 1:]:
                check = (self.negation_mutex(n1, n2) or
                         self.inconsistent_support_mutex(n1, n2))
                if check:
                    mutexify(n1, n2)

    def negation_mutex(self, node_s1: PgNode_s, node_s2: PgNode_s) -> bool:
        """Test a pair of state literals for negating mutual exclusion

        Returns True if one node is the negation of the other, and False
        otherwise.

        :param node_s1: PgNode_s
        :param node_s2: PgNode_s
        :return: bool
        """
        # TODO test for negation between nodes

        # HINT: Look at the PgNode_s.__eq__ defines the notion of equivalence
        # for literal expression nodes, and the class tracks whether the
        # literal is positive or negative.
        return ((node_s1.symbol == node_s2.symbol) and
                (node_s1.is_pos ^ node_s2.is_pos))

    def inconsistent_support_mutex(self, node_s1: PgNode_s, node_s2: PgNode_s):
        """Test a pair of state literals for mutual exclusion

        Returns True if there are no actions that could achieve the two
        literals at the same time, and False otherwise.

        In other words, the two literal nodes are mutex if all of the actions
        that could achieve the first literal node are pairwise mutually
        exclusive with all of the actions that could achieve the second
        literal node.

        :param node_s1: PgNode_s
        :param node_s2: PgNode_s
        :return: bool
        """
        # TODO test for Inconsistent Support between nodes

        # HINT: The PgNode.is_mutex method can be used to test whether two
        # nodes are mutually exclusive.

        # From http://planning.cs.uiuc.edu/node66.html:
        # Inconsistent support: Every pair of operators (actions), $ o,o' \in
        # O_{i-1}$, that achieve $ l$ and $ l'$ is mutex. In this case, one
        # operator must achieve $ l$, and the other must achieve $ l'$. If
        # there exists an operator that achieves both, then this condition is
        # false, regardless of the other pairs of operators.
        for a_node1 in node_s1.parents:
            for a_node2 in node_s2.parents:
                if not (a_node1.is_mutex(a_node2)):
                    return False
        # I haven't knowingly checked whether an action can effect both literals
        # here. There's a unittest which apparently checks this functionality,
        # though (test_inconsistent_support_mutex) , and it passess... so I must
        # have done!
        return True

    def h_levelsum(self) -> int:
        """The sum of the level costs of the individual goals

        (An admissible heuristic if the goals are independent.)

        :return: int
        """
        # TODO implement
        # For each goal in the problem, determine the level cost,
        # then add them together
        level_sum = 0
        for sign, bitmap in [(True, self.problem.goal_action.precond_pos),
                            (False, self.problem.goal_action.precond_neg)]:
            for fluent in self.decode_state(bitmap):
                s_node = PgNode_s(fluent, sign)
                for level, s_nodes in enumerate(self.s_levels):
                    if s_node in s_nodes:
                        level_sum += level
                        break
        return level_sum