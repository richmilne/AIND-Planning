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
        self.all_fluents = all_fluents

        pos, neg, _ = action_bitmaps(all_fluents, *precond)
        self.precond_pos, self.precond_neg = pos, neg

        add, rem, mask = action_bitmaps(all_fluents, *effect)
        self.effect_add, self.effect_rem, self.effect_mask = add, rem, mask

        assert pos & neg == 0

        # You can only remove what was previously asserted or given in the
        # preconditions... or can you? Can you have an effect which removes
        # something that isn't there, as an assurance that it will never be
        # there?
        # For answer, see the Spare Tire Problem (Figure 10.2 3rd ed AIMA).
        # If you leave car out overnight, everything is retracted, no matter
        # what state it was before.
        # assert (pos & rem == rem)

        # Can have an example where a removal is the negative of an add.
        # The effects of Remove(Flat, Ground) are
        # ¬ At(Flat, Ground) and At(Flat, Ground)
        # It works because in the action below, we do the removal first, then
        # we add in the new literal(s).

        # If the problem has cases like this, either comment out assertion
        # below, or modify the Action creation function so as not to produce
        # redundant, no-op actions like this.
        assert add & rem == 0

    def __call__(self, kb):
        return self.act(kb)

    def __str__(self):
        return self.name

    def check_precond(self, kb):
        """Checks if the precondition is satisfied in the current state"""
        # KB - recorded as state bitmap
        if not (kb & self.precond_pos == self.precond_pos):
            return False
        return kb & self.precond_neg == 0

    def act(self, kb):
        """Executes the action on the state's kb"""
        # check if the preconditions are satisfied
        if not self.check_precond(kb):
            raise Exception("Action pre-conditions not satisfied")
        # remove negative literals
        kb = kb & self.effect_mask
        # add positive literals
        kb = kb | self.effect_add

        return kb

    def expand_bitmap(self, bitmap):
        """Returns the fluent literals corresponding to the bits set in bitmap.
        """
        return decode_state(self.all_fluents, bitmap)

    def mutex_inconsistent_effects(self, other):
        """Test a pair of actions for inconsistent effects.

        Returns True if one action negates an effect of the other; False
        otherwise."""
        return     ( (self.effect_add & other.effect_rem) |
                     (self.effect_rem & other.effect_add) )

    def mutex_interference(self, other):
        """Test a pair of actions for interfering mutual exclusion

        Returns True if the effect of one action is the negation of a
        precondition of the other."""
#        print('\nComparing %s and %s' % (str(self), str(other)))
#        for obj in (self, other):
#            for attr in 'precond_pos precond_neg effect_add effect_rem'.split():
#                val = getattr(obj, attr)
#                print('\t%s %s - %s' % (attr, str(obj), bin(val)[2:].zfill(2)))

        return     ( (self.precond_pos & other.effect_rem) or
                     (self.effect_rem  & other.precond_pos) or
                     (self.precond_neg & other.effect_add) or
                     (self.effect_add  & other.precond_neg)
                   )

    def mutex_competing(self, other):
        """Test a pair of actions for competing mutual exclusion

        Returns True if any of the preconditions of one action are mutually
        exclusive with any of the preconditions of the other action."""
        return     ( (self.precond_pos & other.precond_neg) |
                     (self.precond_neg & other.precond_pos) )


if __name__ == '__main__':
    import doctest
    doctest.testmod()