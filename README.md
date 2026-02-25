# projectz.py

Mobile-API for the [ProjectZ](https://play.google.com/store/apps/details?id=com.projz.z.android) social network.

> Developed by [vraestoren](https://github.com/vraestoren) & [Zakovskiy](https://github.com/Zakovskiy)

---

## Quick Start

```python
from projectz import Client

projz = Client()
projz.login(email="example@gmail.com", password="password")
```

---

## Authentication

```python
# Login
projz.login(email="example@gmail.com", password="password")

# Request a security verification code
projz.request_security_validation(email="your@email.com")

# Register a new account
projz.register(
    email="example@gmail.com",
    password="password",
    security_code="123456",
    nickname="YourName",
    tag_line="Hello world!",
    gender=1,
    birthday="2000-01-01"
)

# Change password
projz.change_password(old_password="old", new_password="new")
```

---

## Circles (Communities)

```python
# Get recommended circles
projz.get_recommended_circles(size=10)

# Get circles you've joined
projz.get_my_circles(size=10)

# Get info about a specific circle
projz.get_circle_info(circle_id=123456)

# Join / leave a circle
projz.join_circle(circle_id=123456)
projz.leave_circle(circle_id=123456)

# Get circle members
projz.get_circle_users(circle_id=123456, size=20, member_type="normal")

# Get circle admins
projz.get_circle_admins(circle_id=123456)

# Get active members
projz.get_circle_active_users(circle_id=123456, size=10)

# Get chats inside a circle
projz.get_circle_chats(circle_id=123456, size=10)
```

---

## Chats

```python
# Get chats you've joined
projz.get_joined_chats(start=0, size=10)

# Join / leave a chat
projz.join_chat(chat_id=789)
projz.leave_chat(chat_id=789)

# Send a message
projz.send_message(chat_id=789, content="Hello!")

# Reply to a message
projz.send_message(chat_id=789, content="Nice!", reply_message_id=42)

# Get messages in a chat
projz.get_chat_messages(chat_id=789, size=20)

# Start a new DM
projz.start_chat(user_ids=[111, 222], message="Hey!")
```

---

## Users

```python
# Get recommended users
projz.get_recommended_users()

# Visit a user's profile
projz.visit_profile(user_id=111)
```

---

## Links & Misc

```python
# Resolve a share link
projz.get_link_info(link="https://projz.com/...")

# Verify a captcha
projz.verify_captcha(captcha_value="abc123")
```

---

## Listening for Real-Time Events

The client connects via WebSocket automatically after login. Use the `@on()` decorator to handle incoming messages:

```python
projz.login(email="example@gmail.com", password="password")

@projz.on()
def handle_message(event):
    print(event)

# Start listening
handle_message()
```

---

## Custom Device ID

You can supply your own device ID to persist sessions:

```python
projz = Client(device_id="your_device_id_here")
```

Or generate a fresh one:

```python
device_id = client._device_id()
print(device_id)
```
