def check_precond_subset(precond, state):
    """Check whether the bits set in precond are a subset of the state bits
    
    >>> precond = 0b1010
    >>> check_precond_subset(precond, precond) # Exact match
    True
    >>> check_precond_subset(precond, 0b1011)  # Extra bits set in state
    True
    >>> check_precond_subset(precond, 0b1001)  # No match - different bits
    False
    >>> check_precond_subset(precond, 0)       # No match - zero state
    False
    >>> check_precond_subset(0, 1)             # Match - extra bits set in state
    True
    >>> check_precond_subset(0, 0)             # Exact match
    True
    """
    if not precond:
        return True
    return (precond & state == precond)


def check_precond_invert(precond, state):
    """Check whether the bits set in precond are reset in state
    
    >>> precond = 0b1010
    >>> check_precond_invert(precond, 0b0101)  # Exact inverse
    True
    >>> check_precond_invert(precond, 0b0100)  # Extra bits reset in state
    True
    >>> check_precond_invert(precond, 0b0010)  # No match - bit should be reset
    False
    >>> check_precond_invert(precond, 0)       # Match - zero state
    True
    >>> check_precond_invert(0, 1)             # Match - bits need not be reset
    True
    >>> check_precond_invert(0, 0)             # Exact match
    True
    """
    # if not precond or not state:
    if not (precond and state):
        return True
    return ((precond ^ state) & precond) == precond


def action_bitmaps(all_fluents: tuple, add_pos, rem_neg):
    """Encode fluent lists as precondition/effect bitmaps.

    Creates bitmaps which can be used as masks (against a state bitmap) to
    recognise whether the preconditions of an Action hold, and to represent
    the effects of an Action, as a (re)setting of bits in the state bitmap.

    See the Action class for details on how the bitmaps are used.

    >>> all_fluents = tuple('A B C D E F'.split())
    >>> bitmaps = action_bitmaps(all_fluents, ['B', 'D'], ['E', 'C'])
    >>> for b in bitmaps:
    ...   print(bin(b)[2:].rjust(6))
     10100
      1010
    110101

    :param all_fluents: tuple of all possible fluents for the problem
    :param add_pos: fluents which must be, or will be asserted.
    :param rem_neg: fluents which must not be asserted, or which will be
    removed.
    :return: a tuple containing the positive bitmap, negative bitmap, and a
    bitmap (with the same number of bits as the length of all fluents) with
    the negative fluent positions reset."""
    num_fluents = len(all_fluents)
    fluent_mask = (2**num_fluents) - 1

    add_pos_bitmap = encode_state(all_fluents, add_pos)
    rem_neg_bitmap = encode_state(all_fluents, rem_neg)
    rem_mask = fluent_mask ^ rem_neg_bitmap

    return (add_pos_bitmap, rem_neg_bitmap, rem_mask)


def encode_state(all_fluents: tuple, fluents) -> int:
    """Encode fluents as an integer bitmap.

    For each element in the fluents list, set a bit in the bitmap
    corresponding to the index of that element in the all_fluents list.

    >>> all_fluents = ('At(P2, JFK)', 'At(C2, SFO)', 'In(C2, P1)')
    >>> fluents = ['In(C2, P1)', 'At(P2, JFK)']
    >>> print(bin(encode_state(all_fluents, fluents))[2:])
    101

    :param all_fluents: tuple of all possible fluents for the problem
    :param fluents: subset of all_fluents you wish to be encoded
    :return: bitmap representing positive and negative fluents"""
    bitmap = 0
    num_fluents = len(all_fluents)
    for fluent in fluents:
        index = all_fluents.index(fluent)
        bit = 2**(num_fluents - index - 1)
        bitmap |= bit
    return bitmap


def decode_state(all_fluents: tuple, fluent_bitmap: int) -> list:
    """Decode a fluent bitmap according to the all_fluents tuple.

    Return a list of all the fluents from all_fluents which are indexed by
    the set bits in the bitmap.

    >>> all_fluents = tuple('A B C D E F'.split())
    >>> print(decode_state(all_fluents, 0b11010))
    ['E', 'C', 'B']

    :param all_fluents: tuple of all possible fluents for the problem
    :param fluent_bitmap: integer bitmap stating which of the elements of
    the all_fluent list are asserted.
    :return: list of asserted fluents"""
    num_fluents = len(all_fluents)
    index = 0
    fluents = []
    while fluent_bitmap:
        if fluent_bitmap & 1:
            fluents.append(all_fluents[num_fluents-index-1])
        index += 1
        fluent_bitmap >>= 1
    return fluents


if __name__ == '__main__':
    import doctest
    doctest.testmod()