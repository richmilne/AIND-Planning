from lp_utils import encode_state, action_bitmaps, decode_state

class Action(object):
    """Defines an action schema using preconditions and effects

    Use this to describe actions in PDDL. Precondition and effect are both
    lists with positive and negated literals

    Example:
    >>> all_fluents = tuple(sorted([
    ...     "Human(Person)", "Hungry(Person)", "Eaten(Food)"
    ... ]))
    >>> precond_pos = ["Human(Person)", "Hungry(Person)"]
    >>> precond_neg = ["Eaten(Food)"]
    >>> effect_add = ["Eaten(Food)"]
    >>> effect_rem = ["Hungry(Person)"]
    >>> eat = Action("Eat(person, food)", all_fluents,
    ...              [precond_pos, precond_neg],
    ...              [effect_add, effect_rem]
    ... )
    >>> kb = encode_state(all_fluents, precond_pos)
    >>> kb = eat(kb)
    >>> print(decode_state(all_fluents, kb))
    ['Human(Person)', 'Eaten(Food)']

    Another Example:
    >>> all_fluents = 'A B C D E'.split()
    >>> precond_pos = ['C', 'A']
    >>> precond_neg = ['B']
    >>> effect_add = ['B', 'D']
    >>> effect_rem = ['C']
    >>> precond = [precond_pos, precond_neg]
    >>> effect = [effect_add, effect_rem]

    >>> action = Action('Test()', all_fluents, precond, effect)
    >>> kb1 = encode_state(all_fluents, ['A', 'B', 'C'])
    >>> kb2 = encode_state(all_fluents, ['A',      'C'])
    >>> action.check_precond(kb1)
    False
    >>> action.check_precond(kb2)
    True
    >>> kb = action.act(kb2)
    >>> print(sorted(decode_state(all_fluents, kb)))
    ['A', 'B', 'D']
    """
    def __init__(self, name, all_fluents, precond, effect):
        self.name = name
        precond = action_bitmaps(all_fluents, *precond)
        self.pos_bitmap, self.neg_bitmap = precond[:2]
        effect = action_bitmaps(all_fluents, *effect)
        self.effect_add, self.effect_rem = effect[0], effect[2]

    def __call__(self, kb):
        return self.act(kb)

    def __str__(self):
        return self.name

    def check_precond(self, kb):
        """Checks if the precondition is satisfied in the current state"""
        # KB - recorded as state bitmap
        if not (kb & self.pos_bitmap == self.pos_bitmap):
            return False
        return kb & self.neg_bitmap == 0

    def act(self, kb):
        """Executes the action on the state's kb"""
        # check if the preconditions are satisfied
        if not self.check_precond(kb):
            raise Exception("Action pre-conditions not satisfied")
        # remove negative literals
        kb = kb & self.effect_rem
        # add positive literals
        kb = kb | self.effect_add

        return kb

if __name__ == '__main__':
    import doctest
    doctest.testmod()