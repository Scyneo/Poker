import random
# from functools import total_ordering
from dataclasses import dataclass
from types import SimpleNamespace
import json


@dataclass(frozen=True, order=True)
class Card:
	value: int
	color: str

	def __repr__(self):
		highs = ('J', 'Q', 'K', 'A')
		text_value = highs[self.value - 11] if self.value >= 11 else self.value

		return f'{text_value} {self.color}'


class Deck:
	def __init__(self):
		self.cards = []
		self.build()
		self.shuffle()

	def build(self):
		values = [i for i in range(2, 15)]
		colors = ['♥', '♦', '♣', '♠']
		self.cards = [Card(value, color) for value in values for color in colors]

	def shuffle(self):
		random.shuffle(self.cards)

	def draw(self, n) -> list:
		n_cards = len(self.cards)
		if n > n_cards:
			raise Exception("Za duzo kart chcesz wziac")

		cards_picked = []
		for _ in range(n):
			picked = random.choice(self.cards)
			cards_picked.append(picked)
			self.cards.remove(picked)
		return cards_picked


class Player:
	def __init__(self, deck, money: int = 1000):
		if isinstance(deck, Deck):
			self.cards = deck.draw(2)
		else:
			self.cards = deck
		self.money = money

	@classmethod
	def from_cards(cls, cards: list[Card, Card], money: int = 1000):
		return cls(cards, money)

	def bid(self, amount: int) -> int:
		if amount > self.money:
			raise Exception("Nie masz tyle pieniedzy")
		self.money -= amount
		return amount

	def check(self, current_bid) -> int:
		return self.bid(current_bid)

	def increase(self, current_bid: int, big_blind, amount: int) -> int:
		if amount >= current_bid + big_blind:
			return self.bid(amount)


if __name__ == '__main__':
	deck = Deck()
	# data = b'{"players": {"Agnieszka": [{"cards": [{"value": 10, "color": "\\u2665"}, {"value": 6, "color": "\\u2666"}], "money": 990}, [1050, 100]], ' \
	#        b'"Mateusz": [{"cards": [{"value": 7, "color": "\\u2666"}, {"value": 12, "color": "\\u2665"}], "money": 980}, [1000, 450]]}, ' \
	#        b'"bid": 20, "pot": 0, "table": [{"value": 4, "color": "\\u2660"}, {"value": 6, "color": "\\u2663"}, {"value": 6, "color": "\\u2665"}], "ready": []}'
	#
	# data = json.loads(data.decode('utf8'), object_hook=lambda d: SimpleNamespace(**d))
	#
	# print(vars(data.players))
	con = {"Mateusz": [Player(deck, 1000), 150], "Agnieszka": [Player(deck, 1000), 125]}
	for key in con:
		player = con[key][0]
		player.bid(100)
	print(con["Mateusz"][0].money, con["Agnieszka"][0].money)