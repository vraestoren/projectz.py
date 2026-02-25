from time import sleep
from threading import Thread
from websocket import WebSocket
from orjson import dumps, loads

class WebSocket:
	def __init__(self, client) -> None:
		self.ws = WebSocket()
		self._ping_message = dumps({"t": 0})

	def connect(self) -> None:
		self._sign(path="/v1/chat/ws", body=b"")
		self.ws.connect(
			"wss://ws.projz.com/v1/chat/ws",
			header=client.session.headers)
		self._start_ping_thread()

	def _start_ping_thread(self) -> None:
		def ping_loop():
			import time
			while True:
				try:
					self.ping_cycle()
					sleep(10) 
				except:
					break
		thread = Thread(target=ping_loop, daemon=True)
		thread.start()

	def send(self, data: bytes) -> None:
		self.ws.send_binary(data)

	def ping_cycle(self) -> None:
		if self._ping_message:
			self.send(self._ping_message)

	def listen(self) -> dict:
		raw = self.ws.recv()
		if not raw:
			return {}
		try:
			return loads(raw)
		except:
			return {"raw": raw}

	def send_json(self, entity: dict) -> None:
		self.send(dumps(entity))
