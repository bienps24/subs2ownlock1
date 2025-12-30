import os
import time
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# ======================
# ENV
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID not set")

ADMIN_ID = int(ADMIN_ID)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# ======================
# TELEGRAM CHANNELS (MUST ADD BOT AS ADMIN)
# ======================
REQUIRED_CHANNELS = [
    "@channel_one",
    "@channel_two",
    "@channel_three"
]

CHANNEL_LINKS = [
    "https://t.me/channel_one",
    "https://t.me/channel_two",
    "https://t.me/channel_three"
]

UNLOCK_LINK = "https://t.me/+21PYHt4_VQU4Njc1"
PAYMENT_LINK = "https://connecttelegram.blogspot.com/?m=1"

UNLOCK_DELAY = 10  # seconds

# ======================
# USER DATA (TEMP)
# ======================
users = {}
# users[user_id] = {"start_time": None, "paid": False}

# ======================
# HELPERS
# ======================
async def has_joined_all(user_id: int) -> bool:
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ("member", "administrator", "creator"):
                return False
        except:
            return False
    return True

def is_unlocked(user_id: int) -> bool:
    start = users[user_id]["start_time"]
    if not start:
        return False
    return (time.time() - start) >= UNLOCK_DELAY

def main_keyboard(user_id: int):
    kb = InlineKeyboardMarkup(row_width=1)

    kb.add(
        InlineKeyboardButton("🔴 Join Channel 1", url=CHANNEL_LINKS[0]),
        InlineKeyboardButton("🔴 Join Channel 2", url=CHANNEL_LINKS[1]),
        InlineKeyboardButton("🔔 Join Channel 3", url=CHANNEL_LINKS[2]),
    )

    kb.add(
        InlineKeyboardButton("▶️ Start Unlock", callback_data="start_unlock")
    )

    kb.add(
        InlineKeyboardButton("⚡️ Instant Unlock (Paid)", url=PAYMENT_LINK)
    )

    if users[user_id]["paid"] or is_unlocked(user_id):
        kb.add(InlineKeyboardButton("🔓 Unlock Link", url=UNLOCK_LINK))
    else:
        kb.add(InlineKeyboardButton("🔒 Unlock Link", callback_data="locked"))

    return kb

def status_text(user_id: int):
    if users[user_id]["paid"]:
        return "✅ *Instant Unlock Enabled*"

    if not users[user_id]["start_time"]:
        return "🔓 *Unlock Link*\nJoin all channels then tap **Start Unlock**"

    remaining = int(UNLOCK_DELAY - (time.time() - users[user_id]["start_time"]))
    if remaining > 0:
        return f"⏳ Unlocking… please wait **{remaining}s**"
    return "✅ *Unlock Ready!*"

# ======================
# HANDLERS
# ======================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    if message.chat.type != "private":
        return

    user_id = message.from_user.id
    users.setdefault(user_id, {"start_time": None, "paid": False})

    await message.answer(
        status_text(user_id),
        reply_markup=main_keyboard(user_id),
        parse_mode="Markdown"
    )

@dp.callback_query_handler(lambda c: c.data == "start_unlock")
async def start_unlock(call: types.CallbackQuery):
    user_id = call.from_user.id
    users.setdefault(user_id, {"start_time": None, "paid": False})

    if not await has_joined_all(user_id):
        await call.answer(
            "❌ Please join all required channels first",
            show_alert=True
        )
        return

    if not users[user_id]["start_time"]:
        users[user_id]["start_time"] = time.time()
        await call.answer("⏳ Unlocking… wait 10 seconds", show_alert=True)
    else:
        if is_unlocked(user_id):
            await call.answer("✅ Unlock ready!", show_alert=True)
        else:
            remaining = int(UNLOCK_DELAY - (time.time() - users[user_id]["start_time"]))
            await call.answer(f"⏱️ Please wait {remaining}s", show_alert=True)

    await call.message.edit_text(
        status_text(user_id),
        reply_markup=main_keyboard(user_id),
        parse_mode="Markdown"
    )

@dp.callback_query_handler(lambda c: c.data == "locked")
async def locked(call: types.CallbackQuery):
    await call.answer("🔒 Complete unlock steps or use Instant Unlock", show_alert=True)

# ======================
# ADMIN APPROVE
# ======================
@dp.message_handler(commands=["approve"])
async def approve(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(message.get_args())
        users.setdefault(user_id, {"start_time": None, "paid": False})
        users[user_id]["paid"] = True

        await bot.send_message(
            user_id,
            f"✅ Payment Approved!\n🔓 Unlock Link:\n{UNLOCK_LINK}"
        )
        await message.reply("✅ Approved")
    except:
        await message.reply("Usage: /approve USER_ID")

# ======================
# START
# ======================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
