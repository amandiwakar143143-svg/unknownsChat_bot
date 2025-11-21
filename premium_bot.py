PREMIUM 24/7 OPTIMIZED ANONYMOUS CHAT BOT

Zero errors – Redis based – Anti-spam – Anti-ads – Media block – Stable

Bot Username: unknownsChat_bot

import time import re import redis from telegram import * from telegram.ext import *

TOKEN = "YOUR_BOT_TOKEN" BOT_USERNAME = "unknownsChat_bot"

Redis for 24/7 reliability

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

Constants

SPAM_DELAY = 0.6 MEDIA_BLOCK_TIME = 30

WELCOME_TEXT = """ 👋 Welcome to Anonymous Chat! Tap a button to begin 👇 """

start_keyboard = InlineKeyboardMarkup([ [InlineKeyboardButton("Start Chat 🔎", callback_data="start_chat")], [InlineKeyboardButton("Online Users 👥", callback_data="online")] ])

def set_state(key, value): r.set(key, value)

def get_state(key): v = r.get(key) return v

def send_welcome(update): update.message.reply_text(WELCOME_TEXT, reply_markup=start_keyboard)

Waiting list stored in redis list

def add_waiting(user): if not r.sismember("waiting", user): r.sadd("waiting", user)

def pop_waiting(): users = list(r.smembers("waiting")) if len(users) >= 2: u1, u2 = users[0], users[1] r.srem("waiting", u1) r.srem("waiting", u2) return u1, u2 return None

Anti-spam

def check_spam(uid): now = time.time() last = get_state(f"spam:{uid}") if last: last = float(last) if now - last < SPAM_DELAY: return False set_state(f"spam:{uid}", now) return True

Anti-Ads (no t.me links, no URLs)

def is_advertisement(text): pattern = r"(t.me|http|www.)" return re.search(pattern, text.lower()) is not None

Media-block checker

def can_send_media(uid): start = get_state(f"media:{uid}") if not start: return True diff = time.time() - float(start) return diff >= MEDIA_BLOCK_TIME

Match users

def start_chat(uid, context): partner_key = f"chat:{uid}" if get_state(partner_key): context.bot.send_message(uid, "❗ You're already in chat.") return

add_waiting(uid)
context.bot.send_message(uid, "🔎 Searching for partner…")

pair = pop_waiting()
if pair:
    u1, u2 = int(pair[0]), int(pair[1])
    set_state(f"chat:{u1}", u2)
    set_state(f"chat:{u2}", u1)
    now = time.time()
    set_state(f"media:{u1}", now)
    set_state(f"media:{u2}", now)

    context.bot.send_message(u1, "🎉 Partner found! Say hi!")
    context.bot.send_message(u2, "🎉 Partner found! Say hi!")

Stop chat

def stop_chat(uid, context): partner = get_state(f"chat:{uid}") if not partner: context.bot.send_message(uid, "❗ You aren't in a chat.") return

partner = int(partner)
context.bot.send_message(uid, "❌ Chat ended.")
context.bot.send_message(partner, "❌ Partner left.")

r.delete(f"chat:{uid}")
r.delete(f"chat:{partner}")
r.delete(f"media:{uid}")
r.delete(f"media:{partner}")

Buttons

def handle_buttons(update, context): q = update.callback_query uid = q.message.chat_id

if q.data == "start_chat":
    start_chat(uid, context)
elif q.data == "online":
    online = len(r.smembers("waiting")) + len(r.keys("chat:*"))
    q.message.reply_text(f"👥 Online: {online}")

q.answer()

Message handler

def relay(update, context): msg = update.message uid = msg.chat_id partner = get_state(f"chat:{uid}")

if not partner:
    msg.reply_text("❗ Not chatting. Press Start.")
    return

# Anti-spam
if not check_spam(uid):
    msg.reply_text("⚠ Slow down!")
    return

# Anti-advertisement
if msg.text and is_advertisement(msg.text):
    msg.reply_text("🚫 Ads not allowed.")
    return

# Media blocking
if msg.photo or msg.video or msg.document or msg.animation or msg.sticker:
    if not can_send_media(uid):
        msg.reply_text("⛔ You can send media after 30 seconds.")
        return

context.bot.copy_message(int(partner), uid, msg.message_id)

Commands

def start(update, context): send_welcome(update)

def stop_cmd(update, context): stop_chat(update.message.chat_id, context)

def next_cmd(update, context): stop_chat(update.message.chat_id, context) start_chat(update.message.chat_id, context)

Main runner

def main(): updater = Updater(TOKEN, use_context=True) dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("stop", stop_cmd))
dp.add_handler(CommandHandler("next", next_cmd))
dp.add_handler(CallbackQueryHandler(handle_buttons))

dp.add_handler(MessageHandler(Filters.all, relay))

updater.start_polling()
updater.idle()

if name == "main": main()