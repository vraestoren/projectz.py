from projectz import Client

projectz = Client()
projectz.login(email="example@gmail.com", password="password")

chat_id = projectz.get_joined_chats()["list"][0]["threadId"]
projectz.send_message(chat_id=chat_id, content="Welcome")

@projectz.on()
def event(data):
    projectz.send_message(
    	data["msg"]["threadId"], f"Hello {data['author']['nickname']}")
