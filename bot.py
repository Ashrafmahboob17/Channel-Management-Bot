from telegram import Update, ChatPermissions
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import json
import time

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

TOKEN = config["token"]
OWNER_ID = config["owner_id"]
WARN_LIMIT = 3
RESTRICT_TIME = 24 * 60 * 60  # 24 hours

user_warnings = {}

def start(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 بوت الطلاب جاهز ويستمع إليك 🎓")

def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id == OWNER_ID or update.message.chat.type == "private":
        return

    if "http://" in update.message.text or "https://" in update.message.text:
        count = user_warnings.get(user_id, 0) + 1
        user_warnings[user_id] = count

        if count < WARN_LIMIT:
            update.message.reply_text(f"⚠️ تحذير {count}/{WARN_LIMIT}: يمنع إرسال الروابط.")
        elif count == WARN_LIMIT:
            update.message.reply_text("⛔ تم تقييدك 24 ساعة بسبب تكرار إرسال الروابط.")
            until = int(time.time()) + RESTRICT_TIME
            context.bot.restrict_chat_member(update.message.chat_id, user_id, ChatPermissions(can_send_messages=False), until_date=until)
        else:
            update.message.reply_text("🚫 تم طردك من القناة لتكرار المخالفة.")
            context.bot.kick_chat_member(update.message.chat_id, user_id)
        context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
