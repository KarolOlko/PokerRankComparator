import unittest
from src.card import Card, CardError


class CardTest(unittest.TestCase):

    def test_CorrectCardSymbolProvided_CorrectValueAndColor(self):
        c = Card('2C')
        self.assertEquals('2', c.value)
        self.assertEquals('C', c.color)

    def test_NoneProvided_RaisesCardError(self):
        self.assertRaises(CardError, Card, None)

    def test_CardWithIncorrectColorProvided_RaisesCardError(self):
        self.assertRaises(CardError, Card, '2J')

    def test_WrongCardSymbolProvided_ThrowsCardError(self):
        self.assertRaises(CardError, Card, '1C')

    def test_TooLongStringProvided_ThrowsCardError(self):
        self.assertRaises(CardError, Card, '2CC')

    def test_AllValidCardsAreAccepted(self):
        values = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        colours = ['C', 'D', 'H', 'S']
        for v in values:
            for c in colours:
                Card(v + c)

    def test_CanBeSorted(self):
        cards = [Card('KH'), Card('2C'), Card('3H')]
        sorted_cards = sorted(cards)
        self.assertEquals([Card('2C'), Card('3H'), Card('KH')], sorted_cards)

    def test_CanBeHashed(self):
        s = set()
        s.add(Card('2D'))
        s.add(Card('2D'))
        self.assertEquals(1, len(s))

    def test_SameValueButDifferentColorYieldsUniqueElements(self):
        s = set()
        s.add(Card('2D'))
        s.add(Card('2C'))
        self.assertEquals(2, len(s))

    def test_StringOperatorYieldsCardSymbol(self):
        c = Card('3H')
        self.assertEquals('3H', str(c))

    def test_IsNextInSortedOrder(self):
        self.assertTrue(Card('3S').is_next_in_sorted_order(Card('2H')))
        self.assertFalse(Card('AH').is_next_in_sorted_order(Card('2C')))
