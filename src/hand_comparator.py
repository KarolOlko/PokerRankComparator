import enum
from src.card import Card
from src import card
from enum import unique


class HandError(Exception):
    pass


@unique
class HandRank(enum.IntEnum):
    HIGH_CARD = 0
    PAIR = 1
    TWO_PAIRS = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8


class Hand(object):
    def __init__(self, rank, value=''):
        self.rank = rank
        self.value = value


class CompareError(Exception):
    pass


class Winner(enum.Enum):
    DRAW = "DRAW"
    WHITE = "WHITE"
    BLACK = "BLACK"


class ComparisonResult(object):
    def __init__(self, winner, hand):
        self.winner = winner
        self.hand = hand


class HandVerifier(object):
    def verify_hands(self, black, white):
        for hand in [black, white]:
            if not (self._is_valid_hand_size(hand) and
                    self._are_card_instances(hand)):
                raise HandError()

        self._verify_all_cards_unique(black + white)

    def _is_valid_hand_size(self, hand):
        if len(hand) != 5:
            return False
        return True

    def _are_card_instances(self, hand):
        for card in hand:
            if not isinstance(card, Card):
                return False
        return True

    def _verify_all_cards_unique(self, cards):
        s = set()
        for c in cards:
            s.add(c)

        if len(s) != len(cards):
            raise HandError()


class HandComparator(object):
    def __init__(self):
        self.verifier = HandVerifier()
        self._comparator_for = {HandRank.STRAIGHT_FLUSH: self._compare_straight_flushes,
                                HandRank.FOUR_OF_A_KIND: self._compare_four_of_a_kinds,
                                HandRank.FULL_HOUSE: self._compare_full_houses,
                                HandRank.FLUSH: self._compare_flushes,
                                HandRank.STRAIGHT: self._compare_straights,
                                HandRank.THREE_OF_A_KIND: self._compare_three_of_a_kinds,
                                HandRank.TWO_PAIRS: self._compare_two_pairs,
                                HandRank.PAIR: self._compare_pairs,
                                HandRank.HIGH_CARD: self._compare_high_card_hands}

    def compare_hands(self, black, white):
        hands = self._verify_and_order_descending(black, white)

        ranks = self._compute_ranks(hands)

        if self._ranks_differ(ranks):
            return self._get_higher_of_two(ranks)

        common_rank = self._get_common_rank(ranks)
        comparator = self._comparator_for[common_rank]
        return comparator(hands)

    def _black(self, hands):
        return hands[0]

    def _white(self, hands):
        return hands[1]

    def _verify_and_order_descending(self, black, white):
        self.verifier.verify_hands(black, white)
        return self._order_both_descending(black, white)

    def _order_both_descending(self, black, white):
        return self._order_descending(black), self._order_descending(white)

    def _order_descending(self, hand):
        return sorted(hand, reverse=True)

    def _compute_ranks(self, hands):
        black_rank = self._compute_rank(self._black(hands))
        white_rank = self._compute_rank(self._white(hands))
        return black_rank, white_rank

    def _compute_rank(self, hand):
        if self._is_straight_flush(hand):
            return HandRank.STRAIGHT_FLUSH
        if self._is_four_of_a_kind(hand):
            return HandRank.FOUR_OF_A_KIND
        if self._is_full_house(hand):
            return HandRank.FULL_HOUSE
        if self._is_flush(hand):
            return HandRank.FLUSH
        if self._is_straight(hand):
            return HandRank.STRAIGHT
        if self._is_three_of_a_kind(hand):
            return HandRank.THREE_OF_A_KIND
        if self._is_two_pairs(hand):
            return HandRank.TWO_PAIRS
        if self._is_pair(hand):
            return HandRank.PAIR
        return HandRank.HIGH_CARD

    def _is_straight_flush(self, hand):
        return self._is_straight(hand) and self._is_flush(hand)

    def _is_four_of_a_kind(self, hand):
        value_counts = self._get_value_counts(hand)
        return max(value_counts.values()) == 4

    def _is_full_house(self, hand):
        if self._is_three_of_a_kind(hand):
            card = self._get_three_of_a_kind_card(hand)
            remaining_two = filter(lambda c: c.value != card.value, hand)
            if self._is_pair(remaining_two):
                return True
        return False

    def _is_flush(self, hand):
        hand_color = hand[0].color
        for card in hand:
            if card.color != hand_color:
                return False
        return True

    def _is_straight(self, hand):
        for card_index in range(len(hand) - 1):
            current_card = hand[card_index]
            next_card = hand[card_index + 1]
            if not current_card.is_next_in_sorted_order(next_card):
                return False
        return True

    def _is_three_of_a_kind(self, hand):
        value_counts = self._get_value_counts(hand)
        return max(value_counts.values()) == 3

    def _is_two_pairs(self, hand):
        if self._is_pair(hand):
            pair_value = self._get_pair_value(hand)
            remaining_cards = self._get_ordered_cards_other_than_pair(hand, pair_value)
            if self._is_pair(remaining_cards):
                return True
        return False

    def _is_pair(self, hand):
        value_counts = self._get_value_counts(hand)
        return max(value_counts.values()) == 2

    def _get_value_counts(self, hand):
        value_count = {}
        for card in hand:
            if card.value in value_count:
                value_count[card.value] += 1
            else:
                value_count[card.value] = 1
        return value_count

    def _ranks_differ(self, ranks):
        return self._black(ranks) != self._white(ranks)

    def _get_higher_of_two(self, ranks):
        if self._black(ranks) > self._white(ranks):
            return self._black_wins(ranks)
        return self._white_wins(ranks)

    def _black_wins(self, hands):
        return ComparisonResult(Winner.BLACK, Hand(self._black(hands)))

    def _white_wins(self, hands):
        return ComparisonResult(Winner.WHITE, Hand(self._white(hands)))

    def _get_common_rank(self, ranks):
        return ranks[0]

    def _compare_straight_flushes(self, hands):
        high_card_comparison = self._compare_high_card_hands(hands)
        high_card_comparison.hand.rank = HandRank.STRAIGHT_FLUSH
        return high_card_comparison

    def _compare_four_of_a_kinds(self, hands):
        winning_hand = Hand(HandRank.FOUR_OF_A_KIND)
        values = self._get_four_of_a_kind_cards(hands)
        winner = self._get_winner(values)
        winning_hand.value = self._get_winning_hand_value(winner, values)

        return ComparisonResult(winner, winning_hand)

    def _get_four_of_a_kind_cards(self, hands):
        return [self._get_four_of_a_kind_card(h) for h in hands]

    def _get_four_of_a_kind_card(self, hand):
        for value, count in self._get_value_counts(hand).items():
            if count == 4:
                return self._card_for_value(value)

    def _compare_full_houses(self, hands):
        result = self._compare_three_of_a_kinds(hands)
        result.hand.rank = HandRank.FULL_HOUSE
        return result

    def _compare_flushes(self, hands):
        high_card_comparison = self._compare_high_card_hands(hands)
        high_card_comparison.hand.rank = HandRank.FLUSH
        return high_card_comparison

    def _compare_straights(self, hands):
        winner = self._get_winner(hands)
        winning_hand = self._get_straight_winning_hand(winner, hands)
        return ComparisonResult(winner, winning_hand)

    def _get_straight_winning_hand(self, winner, hands):
        winning_hand = Hand(HandRank.STRAIGHT)
        value = ''
        if winner == Winner.BLACK:
            value = self._black(hands)[0].value
        elif winner == Winner.WHITE:
            value = self._white(hands)[0].value
        winning_hand.value = value

        return winning_hand

    def _compare_three_of_a_kinds(self, hands):
        winning_hand = Hand(HandRank.THREE_OF_A_KIND)
        black_value, white_value = self._get_three_of_a_kind_values(hands)
        winner = self._get_winner([black_value, white_value])
        winning_hand.value = self._get_winning_hand_value(winner, [black_value, white_value])

        return ComparisonResult(winner, winning_hand)

    def _get_three_of_a_kind_values(self, hands):
        cards = []
        for hand in hands:
            card = self._get_three_of_a_kind_card(hand)
            cards.append(card)
        return cards

    def _get_three_of_a_kind_card(self, hand):
        value_counts = self._get_value_counts(hand)
        for value, count in value_counts.items():
            if count == 3:
                return self._card_for_value(value)

    def _get_winning_hand_value(self, winner, cards):
        if winner == Winner.WHITE:
            return self._white(cards).value
        return self._black(cards).value

    def _compare_two_pairs(self, hands):
        winning_hand = Hand(HandRank.TWO_PAIRS)
        black_pairs, white_pairs = self._get_two_pairs_each(hands)
        if self._pair_values_differ([black_pairs, white_pairs]):
            if self._black_pairs_win(black_pairs, white_pairs):
                return ComparisonResult(Winner.BLACK, winning_hand)
            return ComparisonResult(Winner.WHITE, winning_hand)

        return self._compare_last_cards_in_hands(hands)

    def _get_two_pairs_each(self, hands):
        result = []
        for hand in hands:
            first_pair = self._get_pair_value(hand)
            remaining_cards = self._get_ordered_cards_other_than_pair(hand, first_pair)
            second_pair = self._get_pair_value(remaining_cards)
            result.append(self._order_descending([first_pair, second_pair]))
        return result

    def _black_pairs_win(self, black_pairs, white_pairs):
        black_cards = self._cards_for_values(black_pairs)
        white_cards = self._cards_for_values(white_pairs)
        return black_cards > white_cards

    def _cards_for_values(self, values):
        return [self._card_for_value(v) for v in values]

    def _card_for_value(self, value):
        return Card(value + 'C')

    def _compare_last_cards_in_hands(self, hands):
        cards = self._last_cards(hands)
        return self._compare_cards(cards, HandRank.TWO_PAIRS)

    def _last_cards(self, hands):
        last_black = self._get_non_pair_card(self._black(hands))
        last_white = self._get_non_pair_card(self._white(hands))
        return [last_black, last_white]

    def _get_non_pair_card(self, hand):
        for value, count in self._get_value_counts(hand).items():
            if count == 1:
                return list(filter(lambda c: c.value == value, hand))[0]

    def _compare_pairs(self, hands):

        pair_values = self._get_pair_values(hands)
        if self._pair_values_differ(pair_values):
            return self._get_pair_winner(pair_values)

        return self._get_winner_from_remaining_cards(hands, pair_values)

    def _get_pair_values(self, pairs):
        black = self._get_pair_value(self._black(pairs))
        white = self._get_pair_value(self._white(pairs))
        return [black, white]

    def _get_pair_value(self, cards):
        value_counts = self._get_value_counts(cards)
        for value, count in value_counts.items():
            if count == 2:
                return value

    def _pair_values_differ(self, pair_values):
        return pair_values[0] != pair_values[1]

    def _get_pair_winner(self, pair_values):
        if self._black_card_wins(pair_values):
            return ComparisonResult(Winner.BLACK, Hand(HandRank.PAIR, self._black(pair_values)))
        return ComparisonResult(Winner.WHITE, Hand(HandRank.PAIR, self._white(pair_values)))

    def _black_card_wins(self, pair_values):
        return self._card_for_value(self._black(pair_values)) > self._card_for_value(self._white(pair_values))

    def _get_winner_from_remaining_cards(self, hands, pair_values):
        remaining_black = self._get_ordered_cards_other_than_pair(
            self._black(hands), self._black(pair_values))
        remaining_white = self._get_ordered_cards_other_than_pair(
            self._white(hands), self._white(pair_values))
        return self._compare_hands([remaining_black, remaining_white], HandRank.PAIR)

    def _get_ordered_cards_other_than_pair(self, hand, pair_value):
        remaining = filter(lambda c: c.value != pair_value, hand)
        return self._order_descending(remaining)

    def _compare_high_card_hands(self, high_cards):
        return self._compare_hands(high_cards, HandRank.HIGH_CARD)

    def _compare_hands(self, cards, rank):
        winner = self._get_winner(cards)
        winning_hand = self._get_winning_hand(winner, cards, rank)
        return ComparisonResult(winner, winning_hand)

    def _compare_cards(self, cards, rank):
        winner = self._get_winner(cards)
        hand = self._get_winning_card(winner, cards, rank)
        return ComparisonResult(winner, hand)

    def _get_winning_card(self, winner, cards, rank):
        if winner == Winner.BLACK:
            value = self._black(cards).value
            return Hand(rank, value)
        elif winner == Winner.WHITE:
            value = self._white(cards).value
            return Hand(rank, value)
        return Hand(rank)

    def _get_winner(self, hands):
        if self._black(hands) > self._white(hands):
            return Winner.BLACK
        elif self._white(hands) > self._black(hands):
            return Winner.WHITE
        return Winner.DRAW

    def _get_winning_hand(self, winner, hands, rank):
        if winner == Winner.DRAW:
            return Hand(rank)

        for black_card, white_card in zip(hands[0], hands[1]):
            if black_card > white_card:
                return Hand(rank, black_card.value)
            elif white_card > black_card:
                return Hand(rank, white_card.value)
