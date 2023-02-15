import socket
import threading
from Settings import *
from game import Poker
import json
import time


# def handle_client(self, conn):
# 	connected = True
# 	while connected:
# 		message = receive_msg(conn)
# 		if message == DISCONNECT_MESSAGE:
# 			connected = False
#
#
# # conn.close()
#
# def client_threads(self):
# 	for client in self.clients:
# 		threading.Thread(target=self.handle_client, args=(client,))


def json_send(message):
	return json.dumps(message).encode(FORMAT)


def broadcast(message):
	global CLIENTS
	for client in CLIENTS:
		client.sendall(json_send(message))


def receive_msg(connection):
	data = connection.recv(1024)
	data = json.loads(data.decode(FORMAT))
	return data


def poker_handle():
	global THREADS, CLIENTS
	while True:
		if len(CLIENTS) == 2:
			broadcast("Zaczynamy")
			break
	time.sleep(1.0)
	Poker(10, CLIENTS, CONNECTED)


def start():
	global CLIENTS, THREADS, CONNECTED
	server.listen()
	print(f"[LISTENING] Server is running and listening on {SERVER}")

	poker_thread = threading.Thread(target=poker_handle)
	poker_thread.start()

	while True:
		conn, addr = server.accept()
		nickname = receive_msg(conn)
		conn.sendall(json_send(f"Connected successfully, welcome {nickname}"))
		CLIENTS[conn] = [addr]
		CONNECTED[nickname] = []
		# thread = threading.Thread(target=handle_client, args=(conn, ))
		# THREADS.append(thread)
		# thread.start()
		# print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")
		print(f"[ACTIVE CONNECTIONS] {len(CONNECTED)}")


if __name__ == '__main__':
	CONNECTED = {}
	CLIENTS = {}
	THREADS = []
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server.bind(ADDR)
	server.listen()

	print("[STARTING] server is starting...")
	start()
