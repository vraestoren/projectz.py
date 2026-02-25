from hmac import new
from time import time
from uuid import uuid4
from orjson import dumps
from ws import WebSocket
from base64 import b64encode
from requests import Session
from hashlib import sha1, sha256

class Client(WebSocket):
	def __init__(self, device_id: str = None) -> None:
		self.api = "https://api.projz.com"
		self.sid = None
		self.user_id = None
		self.device_id = self._device_id() if not device_id else device_id
		self.session = Session()
		self.session.headers = {
			"rawDeviceId": self.device_id,
			"appType": "MainApp",
			"appVersion": "1.23.4",
			"osType": "2",
			"deviceType": "1",
			"nonce": str(uuid4()),
			"reqTime": str(int(time() * 1000)),
			"Accept-Language": "en-US",
			"countryCode": "EN",
			"User-Agent": "com.projz.z.android/1.23.4-12525 (Linux; U; Android 7.1.2; SM-N975F; Build/samsung-user 7.1.2 2)",
			"timeZone": "480",
			"carrierCountryCodes": "en",
			"Content-Type": "application/json; charset=UTF-8",
			"Host": "api.projz.com",
			"Connection": "Keep-Alive"
		}

	def login(self, email: str, password: str) -> dict:
		data = dumps({
			"authType": 1,
			"email": email,
			"password": password
		})
		path = "/v1/auth/login"
		self._sign(path=path, body=data)
		response = self.session.post(
			f"{self.api}{path}", data=data).json()
		if "sId" in response:
			self.sid = response["sId"]
			self.session.headers["sId"] = self.sid
			self.user_id = response["account"]["uid"]
			self.connect()
		return response

	def register(
			self,
			email: str,
			password: str,
			security_code: str,
			nickname: str,
			tag_line: str,
			gender: int = 1,
			birthday: str = "1900-01-01",
			set_credentials: bool = False) -> dict:
		self.check_security_validation(email, security_code)
		data = dumps({
			"authType": 1,
			"purpose": 1,
			"email": email,
			"password": password,
			"phoneNumber": "+7 ",
			"securityCode": security_code,
			"invitationCode": "",
			"secret": "",
			"nickname": nickname,
			"tagLine": tag_line,
			"icon": "",
			"nameCardBackground": "",
			"gender": gender,
			"birthday": birthday,
			"requestToBeReactivated": False,
			"countryCode": "en",
			"suggestedCountryCode": "EN"
		})
		path = "/v1/auth/register"
		self._sign(path=path, body=data)
		return self.session.post(f"{self.api}{path}", data=data).json()

	def send_message(
			self,
			chat_id: int,
			content: str,
			message_type: int = 1,
			reply_message_id: int = None) -> dict:
		data = {
			"t": 1,
			"threadId": chat_id,
			"msg": {
				"type": message_type,
				"status": 1,
				"threadId": chat_id,
				"createdTime": int(time()),
				"uid": self.user_id,
				"seqId": int(time()),
				"content": content,
				"messageId": message_type,
				"extensions": {
					"replyMessageId": reply_message_id
				}
			}
		}

		return self.send_json(data)

	def change_password(self, old_password: str, new_password: str) -> dict:
		data = dumps({
			"newPassword": new_password,
			"oldPassword": old_password
		})
		path = "/v1/auth/change-password"
		self._sign(path=path, body=data)
		return self.session.post(
			f"{self.api}{path}", data=data).json()

	def get_recommended_circles(
			self,
			size: int = 10,
			page_token: str = None) -> dict:
		path = f"/v1/circles?type=recommend&size={size}"
		if page_token:
			path = f"{path}&pageToken={page_token}"
		self._sign(path=path, body=b"")
		return self.session.get(f"{self.api}{path}").json()

	def get_my_circles(self, size: int = 10, page_token: str = None) -> dict:
		path = f"/v1/circles?type=joined&categoryId=0&size={size}"
		if page_token:
			path = f"{path}&pageToken={page_token}"
		self._sign(path=path, body=b"")
		return self.session.get(f"{self.api}{path}").json()

	def get_circle_chats(
			self,
			circle_id: int,
			social_id: str = None,
			circle_link: str = None,
			size: int = 10,
			page_token: str = None) -> dict:
		path = f"/v1/chat/threads?type=circle&objectId={circle_id}&size={size}",
		if page_token:
			path = f"{path}&pageToken={page_token}"
		self._sign(path=path, body=b"")
		return self.session.get(f"{self.api}{path}").json()

	def get_circle_info(self, circle_id: int) -> dict:
		path = f"/v1/circles/{circle_id}"
		self._sign(path=path, body=b"")
		return self.session.get(f"{self.api}{path}").json()

	def get_link_info(self, link: str) -> dict:
		data = dumps({"link": link})
		path = "/v1/links/path"
		self._sign(path=path, body=data)
		return self.session.post(
			f"{self.api}{path}", data=data).json()

	def join_circle(self, circle_id: int) -> dict:
		path = f"/v1/circles/{circle_id}/members"
		self._sign(path=path, body=b"")
		return self.session.post(f"{self.api}{path}").json()

	def leave_circle(self, circle_id: int) -> dict:
		path = f"/v1/circles/{circle_id}/members"
		self._sign(path=path, body=b"")
		return self.session.delete(f"{self.api}{path}").json()

	def join_chat(self, chat_id: int) -> dict:
		path = f"/v1/chat/threads/{chat_id}/members"
		self._sign(path=path, body=b"")
		return self.session.post(f"{self.api}{path}").json()

	def leave_chat(self, chat_id: int) -> dict:
		path = f"/v1/chat/threads/{chat_id}/members"
		self._sign(path=path, body=b"")
		return self.session.delete(f"{self.api}{path}").json()

	def request_security_validation(self, email: str) -> dict:
		data = dumps({
			"authType": 1,
			"purpose": 1,
			"email": email,
			"countryCode": "en"
		})
		path = "/v1/auth/request-security-validation"
		self._sign(path=path, body=data)
		return self.session.post(
			f"{self.api}{path}", data=data).json()

	def get_chat_messages(
			self,
			chat_id: int,
			size: int = 10,
			page_token: str = None) -> dict:
		path = f"/v1/chat/threads/{chat_id}/messages?size={size}"
		if page_token:
			path = f"{path}&pageToken={page_token}"
		self._sign(path=path, body=b"")
		return self.session.get(f"{self.api}{path}").json()

	def get_joined_chats(
			self,
			start: int = 0,
			size: int = 10,
			chats_type: str = "all") -> dict:
		path = f"/v1/chat/joined-threads?start={start}&size={size}&type={chats_type}"
		self._sign(path=path, body=b"")
		return self.session.get(f"{self.api}{path}").json()

	def check_security_validation(self, email: str, code: str) -> dict:
		data = dumps({
			"authType": 1,
			"email": email,
			"securityCode": code
		})
		path = "/v1/auth/check-security-validation"
		self._sign(path=path, body=data)
		return self.session.get(f"{self.api}{path}", data=data).json()

	def get_circle_users(
			self,
			circle_id: int,
			size: int = 10,
			page_token: str = None,
			type: str = "normal") -> dict:
		path = f"/v1/circles/{circle_id}/members?type={type}&size={size}"
		if page_token:
			path = f"{path}&pageToken={page_token}"
		self._sign(path=path, body=b"")
		return self.session.get(f"{self.api}{path}").json()

	def get_circle_admins(self, circle_id: int) -> dict:
		path = f"/v1/circles/{circle_id}/management-team"
		self._sign(path=path, body=b"")
		return self.session.get(f"{self.api}{path}").json()

	def get_recommended_users(self) -> dict:
		path = "/v1/onboarding/recommend-users"
		self._sign(path=path, body=b"")
		return self.session.get(f"{self.api}{path}").json()

	def get_circle_active_users(
			self,
			circle_id: int,
			size: int = 10,
			page_token: str = None) -> dict:
		path = f"/v1/circles/{circle_id}/active-members?size={size}"
		if page_token:
			path = f"{path}&pageToken={page_token}"
		self._sign(path=path, body=b"")
		return self.session.get(f"{self.api}{path}").json()

	def visit_profile(self, user_id: int) -> dict:
		path = f"/v1/user/profile/{user_id}/visit"
		self._sign(path=path, body=b"")
		return self.session.post(f"{self.api}{path}").json()

	def start_chat(
			self,
			user_ids: list,
			message: str,
			message_type: int = 1) -> dict:
		data = dumps({
			"type": message_type,
			"status": 1,
			"background": self.get_default_chat_background().raw_json,
			"inviteMessageContent": message,
			"invitedUids": user_ids
		})
		path = "/v1/chat/threads"
		self._sign(path=path, body=data)
		return self.session.post(
			f"{self.api}{path}", data=data).json()

	def verify_captcha(self, captcha_value: str) -> dict:
		data = dumps({"captchaValue": captcha_value})
		path = "/api/f/v1/risk/verify-captcha"
		self._sign(path=path, body=data)
		return self.session.post(
			f"{self.api}{path}", data=data).json()

	def _sign(self, path: str, body: bytes) -> None:
		self.session.headers["nonce"] = str(uuid4())
		self.session.headers["reqTime"] = str(int(time() * 1000))

		signature_data = path.encode("utf-8")
		for signable in [
			"rawDeviceId", "rawDeviceIdTwo",
			"appType", "appVersion",
			"osType", "deviceType",
			"sId", "countryCode",
			"reqTime", "User-Agent",
			"contentRegion", "nonce",
			"carrierCountryCodes"
		]:
			if header := self.session.headers.get(signable):
				signature_data += header.encode("utf-8")

		if body:
			signature_data += body

		mac = new(
			bytes.fromhex(
				"0705dd04686ef13c9228549386eb9164467fe99b284078b89ab96cb4ba6cc748"), signature_data, sha256)
		self.session.headers["HJTRFS"] = b64encode(bytes.fromhex("02") + mac.digest()).decode("utf-8")

	def _device_id(self):
		prefix = bytes.fromhex("02") + sha1(str(uuid4()).encode("utf-8")).digest()
		return (prefix + sha1(
			prefix + sha1(bytes.fromhex("c48833a8487cc749e66eb934d0ba7f2d608a")).digest()).digest()
		).hex()

	def on(self, event_type: str = None):
		def decorator(function):
			def wrapper():
				while True:
					function(self.listen())
			return wrapper
		return decorator
