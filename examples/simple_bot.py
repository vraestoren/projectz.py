from projectz import Client

projz = Client()
projz.login(email="example@gmail.com", password="password")

chat_id = projz.get_joined_chats()["list"][0]["threadId"]
projz.send_message(chat_id=chat_id, content="Welcome")

@projectz.on()
def event(data):
    projz.send_message(
    	data["msg"]["threadId"], f"Hello {data['author']['nickname']}")
