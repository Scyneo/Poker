import threading
from types import SimpleNamespace
import pygame, sys
from Settings import *
from Deck_Player import Player, Card, Deck
import json

pygame.font.init()
pygame.init()

pot_font = pygame.font.SysFont("monospace", 60)
balance_font = pygame.font.SysFont("monospace", 40)


def load_cards():
	deck = Deck()
	cards = {}
	for card in deck.cards:
		value = card.value
		color = card.color

		if value == 11:
			card_type = "jack"
		elif value == 12:
			card_type = "queen"
		elif value == 13:
			card_type = "king"
		elif value == 14:
			card_type = "ace"
		else:
			card_type = str(value)

		if color == '♥':
			card_color = "hearts"
		elif color == '♦':
			card_color = "diamonds"
		elif color == '♣':
			card_color = "clubs"
		elif color == '♠':
			card_color = "spades"

		card_name = card_type + "_of_" + card_color

		card_image = pygame.transform.scale(pygame.image.load(f"cards\{card_name}.png"), (80, 128))
		cards[card] = card_image
	return cards


def json_send(message):
	return json.dumps(message).encode(FORMAT)


class Game:
	def __init__(self, nickname, client):
		self.screen = pygame.display.set_mode((1280, 720))
		self.cards = load_cards()
		self.render_slider = False

		self.nickname = nickname
		self.client = client
		self.data_bundle = SimpleNamespace

		self.players = {}
		self.player = []

		self.table = []
		self.bid = 0
		self.pot = 0
		self.state = ""
		self.player_turn = ""

		self.handle_data_bundle(True)

		pygame.display.set_caption(nickname)
		self.clock = pygame.time.Clock()

	def run(self):
		background1 = pygame.transform.scale(pygame.image.load('canvas.png'), (1280, 720))
		background2 = pygame.transform.scale(pygame.image.load('stol.png'), (1600, 900))
		dealer_img = pygame.transform.scale_by(pygame.image.load("dealer.png"), 0.5)
		check_button = Button(pygame.image.load("check_button.png"), (700, 60), self.screen)
		fold_button = Button(pygame.image.load("fold_button.png"), (700, 120), self.screen)
		raise_button = Button(pygame.image.load("raise_button.png"), (700, 180), self.screen)
		ok_button = Button(pygame.transform.scale(pygame.image.load("ok_button.png"), (45, 45)), (810, 400), self.screen)
		dealer_coin = pygame.transform.scale_by(pygame.image.load("dealer_coin.png"), 0.15)
		neon = pygame.transform.scale(pygame.image.load("neon.png"), (190, 190))

		slider = Slider(self.screen, 400, 400, 400, 45)

		data_handler = threading.Thread(target=self.handle_data_bundle)
		data_handler.start()

		while True:
			self.clock.tick(60)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()

			# Displaying background and dealer
			self.screen.blit(background1, (0, 0))
			self.screen.blit(background2, ((1280 - 1600) / 2, (720 - 900) / 2))
			self.screen.blit(dealer_img, (520, -35))

			# Displaying table and player cards and money
			self.display_table()
			self.draw_players()
			pot_text = pot_font.render(str(self.pot), True, (255, 255, 255))
			self.screen.blit(pot_text, (380, 150))

			state = pot_font.render(self.state, True, (255, 255, 255))
			self.screen.blit(state, (1100, 650))

			# Place dealer coin
			# min(list(self.players.values())[1][1][1])

			# Glow rectangle around player turn
			neon_pos = self.players[self.player_turn][1][0]
			self.screen.blit(neon, (neon_pos[0]-35, neon_pos[1] - 37))

			if self.player[2]:
				if check_button.draw():
					self.client.sendall(json_send("check"))
				if raise_button.draw():
					self.render_slider = True
				if fold_button.draw():
					self.client.sendall(json_send("fold"))

			if self.render_slider:
				if self.state in ["preflop", "flop"]:
					slider.draw(self.bid + 10, self.player[0].money)
				else:
					slider.draw(self.bid + 20, self.player[0].money)
				if ok_button.draw():
					raise_money = slider.get_money()
					self.client.sendall(json_send(raise_money))
					self.render_slider = False

			pygame.display.update()

	def handle_data_bundle(self, first_run=None):
		while True:
			self.data_bundle = self.json_receive()

			print("Received data")

			self.players = {}
			self.player = []
			self.process_players()
			self.player = self.players[self.nickname]
			self.player_turn = self.data_bundle.turn

			self.table = [Card(**vars(card)) for card in self.data_bundle.table]
			self.bid = self.data_bundle.bid
			self.pot = self.data_bundle.pot
			self.state = self.data_bundle.state
			if first_run:
				break

	def display_table(self):
		k = 0
		if self.state == "flop":
			k = 3
		elif self.state == "turn":
			k = 4
		elif self.state == "river":
			k = 5

		for i in range(5):
			self.display_card(self.table[i], (380 + i * 110, 270), i <= k - 1)

	def draw_players(self):
		fold_image = pygame.transform.scale(pygame.image.load("fold.png"), (120, 128))

		for player_data in self.players.values():
			player = player_data[0]
			position = player_data[1][0]
			visible = False

			if player == self.player[0]:
				visible = True

			# Displaying cards
			if not player_data[2]:
				self.screen.blit(fold_image, position)
			else:
				self.display_card(player.cards[0], position, visible)
				self.display_card(player.cards[1], (position[0] + 40, position[1]), visible)

			# Displaying balance
			balance_text = balance_font.render(str(player.money), True, (255, 255, 255))
			self.screen.blit(balance_text, (position[0], position[1] + 130))

	def display_card(self, card: Card, pos: tuple, visible: bool):
		if visible:
			self.screen.blit(self.cards[card], pos)
		else:
			# Display back of the card
			self.screen.blit(pygame.transform.scale(pygame.image.load("back.png"), (80, 128)), pos)

	def process_players(self):
		# Creates dictionary from SimpleNamespace
		data = vars(self.data_bundle.players)

		for nickname, player_data in data.items():
			player_cards = []
			cards = player_data[0].cards
			money = player_data[0].money
			pos = player_data[1]
			turn = player_data[2]

			card1 = Card(**vars(cards[0]))
			card2 = Card(**vars(cards[1]))
			player_cards.append(card1)
			player_cards.append(card2)

			player_object = Player.from_cards(player_cards, money)

			self.players[nickname] = [player_object, pos, turn]

	def json_receive(self):
		data = self.client.recv(1024)
		return json.loads(data.decode(FORMAT), object_hook=lambda d: SimpleNamespace(**d))


class Button:
	def __init__(self, image, pos: tuple, screen):
		self.screen = screen
		self._image = image
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = pos
		self.clicked = False
		self.hover = False

	def draw(self):
		action = False
		pos = pygame.mouse.get_pos()

		if self.hover:
			self.image = self._image
			self.hover = False

		if self.rect.collidepoint(pos):
			if not self.hover:
				self.image = pygame.transform.scale_by(self.image, 1.05)
				self.hover = True

			if pygame.mouse.get_pressed()[0] and not self.clicked:
				self.clicked = True
				action = True

		if not pygame.mouse.get_pressed()[0]:
			self.clicked = False

		self.screen.blit(self.image, (self.rect.x, self.rect.y))

		return action


class Slider:
	def __init__(self, screen, x_coord, y_coord, width, height):
		# x, y, width, height
		self.screen = screen
		self.money = 0
		self.sliderRect = pygame.Rect(x_coord, y_coord, width, height)
		self.smallSliderRect = pygame.Rect(x_coord, y_coord, 20, height)
		self.clicked = False

	def draw(self, min_money: int, max_money: int):
		self.clicked = False
		pygame.draw.rect(self.screen, (255, 255, 255), self.sliderRect)

		pos = pygame.mouse.get_pos()

		if self.smallSliderRect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0]:
				self.smallSliderRect.centerx = pos[0]
				self.clicked = True
		elif self.sliderRect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0]:
				self.smallSliderRect.centerx = pos[0]
				self.clicked = True

		if self.clicked:
			self.update_money(pos[0], min_money, max_money)

		pygame.draw.rect(self.screen, (255, 0, 0), self.smallSliderRect)

		money = balance_font.render(str(self.money), True, (0, 0, 0))
		self.screen.blit(money, (self.sliderRect.centerx, self.sliderRect.y))

	def update_money(self, x: int, min_money: int, max_money: int):
		if x < self.sliderRect.x:
			self.smallSliderRect.x = self.sliderRect.x
			self.money = min_money
		elif x > self.sliderRect.x + self.sliderRect.w:
			self.money = max_money
			self.smallSliderRect.x = self.sliderRect.x + self.sliderRect.w - self.smallSliderRect.w
		else:
			self.money = int(min_money + (max_money - min_money) * \
							float((x - self.sliderRect.x) / float(self.sliderRect.w)))

	def get_money(self):
		return self.money
