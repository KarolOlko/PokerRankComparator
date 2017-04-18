
class CardError(Exception):
    pass


class Card(object):
    values = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    colours = ['C', 'D', 'H', 'S']

    def __init__(self, c):
        self._validate_input(c)
        self.value = c[0]
        self.color = c[1]

    def _validate_input(self, c):
        if not(c and len(c) == 2 and
                c[0] in Card.values and
               c[1] in Card.colours):
            raise CardError()

    def __lt__(self, other):
        lhs = Card.values.index(self.value)
        rhs = Card.values.index(other.value)
        return lhs < rhs

    def __eq__(self, other):
        lhs = Card.values.index(self.value)
        rhs = Card.values.index(other.value)
        return lhs == rhs

    def __str__(self):
        return '%s%s' % (self.value, self.color)

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash((self.value, self.color))

    def is_next_in_sorted_order(self, other):
        return self.values.index(self.value) - self.values.index(other.value) == 1
