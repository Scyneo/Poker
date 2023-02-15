from Deck_Player import Deck, Player, Card
from Settings import *
import time
import json
import random


def receive_msg(connection):
	data = connection.recv(1024)
	data = json.loads(data.decode(FORMAT))
	return data


def json_send(message):
	return json.dumps(message, default=encode_players).encode(FORMAT)


def encode_players(some_object):
	if isinstance(some_object, Player):
		return some_object.__dict__
	elif isinstance(some_object, Card):
		return some_object.__dict__
	else:
		type_name = some_object.__class__.__name__
		raise TypeError(f"Object of type '{type_name}' is not JSON serializable")


class Poker:
	def __init__(self, small_blind: int, clients: dict, connected: dict):
		self.deck = Deck()
		self.small_blind = small_blind
		self.bid = 2 * small_blind
		self.pot = 0
		self.state = "preflop"

		self.connected = connected
		self.clients = clients
		self.initialize_players()
		self.table = self.deck.draw(5)
		self.player_turn = ""

		self.data_bundle = {}
		self.run()

	def players_decide(self, ready):
		for key, conn in zip(self.connected, self.clients):

			if not self.connected[key][2]:
				continue

			player = self.connected[key][0]
			self.player_turn = key

			self.send_data_bundle()

			if len(self.connected) == 1:
				player.money += self.pot  # IT'S A WIN
				self.bid = 0
				return True
			if len(ready) == len(self.connected):
				self.bid = 0
				return True

			decision = receive_msg(conn)
			try:
				int(decision)
			except ValueError:
				pass

			if decision == 'check':
				self.pot += player.check(self.bid)
				ready.append(player)
			elif isinstance(decision, int):
				amount = decision
				if self.state in ["preflop", "flop"]:
					new_amount = player.increase(self.bid, self.small_blind, amount)
				else:
					new_amount = player.increase(self.bid, self.small_blind * 2, amount)
				self.pot += new_amount
				self.bid = new_amount
				ready.clear()
				ready.append(player)
			else:
				self.connected[key][2] = False
			# self.clients.pop(conn)
			self.send_data_bundle()

	def send_data_bundle(self):
		self.data_bundle = {"players": self.connected, "bid": self.bid, "pot": self.pot, "table": self.table,
							"state": self.state, "turn": self.player_turn}

		for conn in self.clients:
			conn.sendall(json_send(self.data_bundle))

		print("Send data")
		print(self.data_bundle)

	def bidding(self):
		ready = []
		while True:
			if self.players_decide(ready):
				time.sleep(2.0)
				return

	def run(self):
		self.blinds()
		# Actual game
		self.send_data_bundle()
		self.flop()
		self.turn()
		self.river()

	def blinds(self):
		# Wpłacanie ciemnych
		for n, key in enumerate(self.connected):
			player = self.connected[key][0]
			if n == 0:
				self.pot += player.bid(self.small_blind)
			else:
				self.pot += player.bid(self.bid)
				break

	def flop(self):
		# Flop
		self.bidding()
		self.state = "flop"
		self.bidding()

	def turn(self):
		# Turn
		self.state = "turn"
		self.bidding()

	def river(self):
		# River
		self.state = "river"
		self.bidding()

	def initialize_players(self):
		player_places = [[(1050, 100), 1], [(1000, 450), 2], [(565, 510), 3], [(170, 450), 4], [(120, 100), 5]]

		for player in self.connected.values():
			random_place = random.choice(player_places)
			player_places.remove(random_place)

			player.append(Player(self.deck))
			player.append(random_place)
			player.append(True)

	def broadcast(self, message):
		for conn in self.clients:
			conn.sendall(json_send(message))
