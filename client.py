import socket
from Settings import *
import json
from graphics import Game

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
nickname = str(input("Set your nickname: "))


def receive_msg():
	while True:
		msg_data = client.recv(1024)
		msg_data = json.loads(msg_data.decode(FORMAT))
		print(msg_data)
		if msg_data == "Zaczynamy":
			break


def send_msg():
	client.sendall(json.dumps(nickname).encode(FORMAT))


send_msg()
receive_msg()

# receive_thread = threading.Thread(target=receive_msg)
# receive_thread.start()
#
# send_thread = threading.Thread(target=send_msg)
# send_thread.start()
#
# if not receive_thread.is_alive():
# 	g = Game(nickname, client)
# 	g.run()

g = Game(nickname, client)
g.run()
