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

    def _post(self, path: str, data: bytes = b"") -> dict:
        self._sign(path=path, body=data)
        return self.session.post(f"{self.api}{path}", data=data).json()

    def _get(self, path: str) -> dict:
        self._sign(path=path, body=b"")
        return self.session.get(f"{self.api}{path}").json()

    def _delete(self, path: str) -> dict:
        self._sign(path=path, body=b"")
        return self.session.delete(f"{self.api}{path}").json()

    def login(self, email: str, password: str) -> dict:
        data = dumps({
            "authType": 1,
            "email": email,
            "password": password
        })
        response = self._post("/v1/auth/login", data)
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
            birthday: str = "1900-01-01") -> dict:
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
        return self._post("/v1/auth/register", data)

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
        return self._post("/v1/auth/change-password", data)

    def get_recommended_circles(
            self,
            size: int = 10,
            page_token: str = None) -> dict:
        path = f"/v1/circles?type=recommend&size={size}"
        if page_token:
            path += f"&pageToken={page_token}"
        return self._get(path)

    def get_my_circles(
            self,
            size: int = 10,
            page_token: str = None) -> dict:
        path = f"/v1/circles?type=joined&categoryId=0&size={size}"
        if page_token:
            path += f"&pageToken={page_token}"
        return self._get(path)

    def get_circle_chats(
            self,
            circle_id: int,
            size: int = 10,
            page_token: str = None) -> dict:
        path = f"/v1/chat/threads?type=circle&objectId={circle_id}&size={size}"
        if page_token:
            path += f"&pageToken={page_token}"
        return self._get(path)

    def get_circle_info(self, circle_id: int) -> dict:
        return self._get(f"/v1/circles/{circle_id}")

    def get_link_info(self, link: str) -> dict:
        return self._post("/v1/links/path", dumps({"link": link}))

    def join_circle(self, circle_id: int) -> dict:
        return self._post(f"/v1/circles/{circle_id}/members")

    def leave_circle(self, circle_id: int) -> dict:
        return self._delete(f"/v1/circles/{circle_id}/members")

    def join_chat(self, chat_id: int) -> dict:
        return self._post(f"/v1/chat/threads/{chat_id}/members")

    def leave_chat(self, chat_id: int) -> dict:
        return self._delete(f"/v1/chat/threads/{chat_id}/members")

    def request_security_validation(self, email: str) -> dict:
        data = dumps({
            "authType": 1,
            "purpose": 1,
            "email": email,
            "countryCode": "en"
        })
        return self._post("/v1/auth/request-security-validation", data)

    def check_security_validation(self, email: str, code: str) -> dict:
        data = dumps({
            "authType": 1,
            "email": email,
            "securityCode": code
        })
        return self._post("/v1/auth/check-security-validation", data)

    def get_chat_messages(
            self,
            chat_id: int,
            size: int = 10,
            page_token: str = None) -> dict:
        path = f"/v1/chat/threads/{chat_id}/messages?size={size}"
        if page_token:
            path += f"&pageToken={page_token}"
        return self._get(path)

    def get_joined_chats(
            self,
            start: int = 0,
            size: int = 10,
            chats_type: str = "all") -> dict:
        return self._get(
            f"/v1/chat/joined-threads?start={start}&size={size}&type={chats_type}")

    def get_circle_users(
            self,
            circle_id: int,
            size: int = 10,
            page_token: str = None,
            user_type: str = "normal") -> dict:
        path = f"/v1/circles/{circle_id}/members?type={user_type}&size={size}"
        if page_token:
            path += f"&pageToken={page_token}"
        return self._get(path)

    def get_circle_admins(self, circle_id: int) -> dict:
        return self._get(f"/v1/circles/{circle_id}/management-team")

    def get_recommended_users(self) -> dict:
        return self._get("/v1/onboarding/recommend-users")

    def get_circle_active_users(
            self,
            circle_id: int,
            size: int = 10,
            page_token: str = None) -> dict:
        path = f"/v1/circles/{circle_id}/active-members?size={size}"
        if page_token:
            path += f"&pageToken={page_token}"
        return self._get(path)

    def visit_profile(self, user_id: int) -> dict:
        return self._post(f"/v1/user/profile/{user_id}/visit")

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
        return self._post("/v1/chat/threads", data)

    def verify_captcha(self, captcha_value: str) -> dict:
        return self._post(
            "/api/f/v1/risk/verify-captcha",
            dumps({"captchaValue": captcha_value}))

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
                "0705dd04686ef13c9228549386eb9164467fe99b284078b89ab96cb4ba6cc748"),
            signature_data, sha256)
        self.session.headers["HJTRFS"] = b64encode(
            bytes.fromhex("02") + mac.digest()).decode("utf-8")

    def _device_id(self) -> str:
        prefix = bytes.fromhex("02") + sha1(
            str(uuid4()).encode("utf-8")).digest()
        return (prefix + sha1(
            prefix + sha1(
                bytes.fromhex("c48833a8487cc749e66eb934d0ba7f2d608a")).digest()
        ).digest()).hex()

    def on(self, event_type: str = None):
        def decorator(function):
            def wrapper():
                while True:
                    function(self.listen())
            return wrapper
        return decorator
