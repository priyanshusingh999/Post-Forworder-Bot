import requests, json, time,threading
from flask import Flask
from pymongo import MongoClient
from collections import defaultdict
from config import TOKEN, MONGO_URI, DB_NAME, FORCE_SUB_CHANNEL, OWNER_ID

app = Flask(__name__)

@app.route('/')
def home():
    return '🤖 Bot is Running! Created by @priyanshusingh999'

def run_flask():
    app.run(host='0.0.0.0', port=8001)

threading.Thread(target=run_flask).start()

API = f"https://api.telegram.org/bot{TOKEN}"

mongo = MongoClient(MONGO_URI)
db = mongo[DB_NAME]
users_col = db['users']
toggles_col = db['toggles']

media_groups = defaultdict(list)
media_timestamps = {}

def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(f"{API}/sendMessage", json=payload)
    except Exception as e:
        print(f"❌ Error sending message: {e}")

def pin_message(chat_id, message_id):
    try:
        requests.post(f"{API}/pinChatMessage", json={"chat_id": chat_id, "message_id": message_id})
    except Exception as e:
        print(f"❌ Pin failed: {e}")

def get_updates(offset=None):
    try:
        params = {"timeout": 30, "offset": offset}
        r = requests.get(f"{API}/getUpdates", params=params, timeout=40)
        return r.json().get("result", [])
    except Exception as e:
        print(f"❌ Error in get_updates: {e}")
        return []

def get_member_status(user_id, channel_id):
    try:
        r = requests.get(f"{API}/getChatMember", params={"chat_id": channel_id, "user_id": user_id}).json()
        return r.get("result", {}).get("status", "left")
    except:
        return "left"

def force_subscribe_message(chat_id):
    btn = {"inline_keyboard": [[{"text": "🔗 Join Channel", "url": f"https://t.me/{FORCE_SUB_CHANNEL.strip('@')}"}]]}
    send_message(chat_id, "🔒 Pehle channel join karo tabhi aap bot ka use kar sakte ho.", reply_markup=json.dumps(btn))

def get_chat_username(channel_id):
    try:
        r = requests.get(f"{API}/getChat", params={"chat_id": channel_id}).json()
        return r.get("result", {}).get("username")
    except:
        return None

def copy_message(to_chat_id, message):
    try:
        res = requests.post(f"{API}/copyMessage", json={"chat_id": to_chat_id, "from_chat_id": message["chat"]["id"], "message_id": message["message_id"]}).json()
        mid = res.get("result", {}).get("message_id")
        if mid:
            pin_message(to_chat_id, mid)
        return mid
    except Exception as e:
        print(f"❌ Error forwarding message: {e}")
        return None

def get_user(user_id):
    user = users_col.find_one({"_id": user_id})
    if not user:
        user = {"_id": user_id, "channels": []}
        users_col.insert_one(user)
    return user

def get_toggle(user_id):
    toggle = toggles_col.find_one({"_id": user_id})
    if not toggle:
        toggle = {"_id": user_id, "show_links": True, "respond_getchat": True}
        toggles_col.insert_one(toggle)
    return toggle

def toggle_posturl_inline(chat_id, user_id):
    toggle = get_toggle(user_id)
    new_val = not toggle.get("respond_getchat", True)
    toggles_col.update_one({"_id": user_id}, {"$set": {"respond_getchat": new_val}})
    status = "ON ✅" if new_val else "OFF ❌"
    send_message(chat_id, f"🛠️ Post URL fetch is now {status}")

def main():
    print("✅ Bot is running with MongoDB...")
    offset = None
    while True:
        updates = get_updates(offset)
        for update in updates:
            offset = update["update_id"] + 1
            message = update.get("message")
            if not message:
                continue

            user_id = message["from"]["id"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")

            if FORCE_SUB_CHANNEL:
                status = get_member_status(user_id, FORCE_SUB_CHANNEL)
                if status in ["left", "kicked"]:
                    force_subscribe_message(chat_id)
                    continue

            user = get_user(user_id)
            toggle = get_toggle(user_id)

            if message.get("media_group_id"):
                mgid = message["media_group_id"]
                media_groups[mgid].append(message)
                media_timestamps[mgid] = time.time()
                continue

            if text.startswith("/start"):
                send_message(chat_id, "👋 Welcome! Send any post and I’ll share it to your channels.")

            elif text.startswith("/addchannel"):
                try:
                    ids = text.split(" ", 1)[1].split()
                    users_col.update_one({"_id": user_id}, {"$addToSet": {"channels": {"$each": ids}}})
                    send_message(chat_id, f"✅ Added: {', '.join(ids)}")
                except:
                    send_message(chat_id, "❌ Usage: /addchannel <channel_ids>")

            elif text.startswith("/removechannel"):
                try:
                    ids = text.split(" ", 1)[1].split()
                    users_col.update_one({"_id": user_id}, {"$pull": {"channels": {"$in": ids}}})
                    send_message(chat_id, f"🗑️ Removed: {', '.join(ids)}")
                except:
                    send_message(chat_id, "❌ Usage: /removechannel <channel_ids>")

            elif text.startswith("/mychannels"):
                chans = user.get("channels", [])
                if not chans:
                    send_message(chat_id, "ℹ️ Aapne abhi koi channel add nahi kiya.")
                else:
                    send_message(chat_id, "📋 Aapke channels:\n" + "\n".join(chans))

            elif text.startswith("/users") and user_id == OWNER_ID:
                send_message(chat_id, f"👥 Total users: {users_col.count_documents({})}")

            elif text.startswith("/broadcast") and user_id == OWNER_ID:
                try:
                    msg = text.split(" ", 1)[1]
                    sent = 0
                    for usr in users_col.find():
                        try:
                            send_message(usr['_id'], f"📢 Broadcast:\n\n{msg}")
                            sent += 1
                        except:
                            pass
                    send_message(chat_id, f"✅ Broadcast sent to {sent} users")
                except:
                    send_message(chat_id, "❌ Usage: /broadcast <message>")

            elif text == "/toggleurls":
                new_val = not toggle.get("show_links", True)
                toggles_col.update_one({"_id": user_id}, {"$set": {"show_links": new_val}})
                status = "ON ✅" if new_val else "OFF ❌"
                send_message(chat_id, f"🔁 Post URL toggle is now {status}")

            elif text == "/togglegetchat":
                toggle_posturl_inline(chat_id, user_id)

            elif text.startswith("/getChat") and toggle.get("respond_getchat", True):
                send_message(chat_id, json.dumps(update, indent=2))

            else:
                if not user.get("channels"):
                    send_message(chat_id, "⚠️ Pehle /addchannel se channel add karo.")
                    continue
                links = []
                for cid in user["channels"]:
                    mid = copy_message(cid, message)
                    uname = get_chat_username(cid)
                    if uname and mid and toggle.get("show_links", True):
                        links.append(f"https://t.me/{uname}/{mid}")
                if links:
                    send_message(chat_id, "🔗 Post URLs:\n" + "\n".join(links))

        for gid in list(media_groups.keys()):
            if time.time() - media_timestamps[gid] > 1.5:
                group = media_groups.pop(gid)
                media_timestamps.pop(gid, None)
                user_id = group[0]["from"]["id"]
                chat_id = group[0]["chat"]["id"]
                user = get_user(user_id)
                toggle = get_toggle(user_id)
                if not user.get("channels"):
                    send_message(chat_id, "⚠️ Pehle /addchannel se channel add karo.")
                    continue
                links = []
                for cid in user["channels"]:
                    media = []
                    for idx, msg in enumerate(group):
                        item = {}
                        if "photo" in msg:
                            item = {"type": "photo", "media": msg["photo"][-1]["file_id"]}
                        elif "video" in msg:
                            item = {"type": "video", "media": msg["video"]["file_id"]}
                        else:
                            continue
                        if idx == 0 and msg.get("caption"):
                            item["caption"] = f"<b>{msg['caption']}</b>"
                            item["parse_mode"] = "HTML"
                        media.append(item)
                    if media:
                        try:
                            res = requests.post(f"{API}/sendMediaGroup", json={"chat_id": cid, "media": media}).json()
                            first_id = res["result"][0]["message_id"]
                            pin_message(cid, first_id)
                            uname = get_chat_username(cid)
                            if uname and toggle.get("show_links", True):
                                links.append(f"https://t.me/{uname}/{first_id}")
                        except Exception as e:
                            print(f"❌ sendMediaGroup failed: {e}")
                if links:
                    send_message(chat_id, "📸 Media Group Posted:\n" + "\n".join(links))

        time.sleep(1)

if __name__ == "__main__":
    main()
