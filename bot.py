import os
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not BOT_TOKEN or not ADMIN_ID:
    raise ValueError("Missing BOT_TOKEN or ADMIN_ID in environment variables")

ADMIN_ID = int(ADMIN_ID)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# LINKS
YT1 = "https://www.youtube.com/@HOTMOVIES-q6n"
UNLOCK_LINK = "https://t.me/+21PYHt4_VQU4Njc1"
PAYMENT_LINK = "https://t.me/reaks_14bot/pay"

# USER DATA (in-memory)
users = {}

def progress_bar(done):
    bars = ["🟩" if i < done else "⬜️" for i in range(3)]
    return "".join(bars)

def main_keyboard(user_id):
    kb = InlineKeyboardMarkup(row_width=1)
    # Show channels only
    kb.add(
        InlineKeyboardButton("🔴 Subscribe Now", url=YT1),
    )

    # Payment option
    kb.add(InlineKeyboardButton("⚡️ Instant Unlock (55.00php)", url=PAYMENT_LINK))

    # Unlock link logic
    if users[user_id]["unlocked"]:
        kb.add(InlineKeyboardButton("🔓 Unlock 2 VIP CHANNELS", url=UNLOCK_LINK))
    else:
        kb.add(InlineKeyboardButton("🔒 Unlock Now", callback_data="locked"))

    return kb

def text_status(user_id):
    return (
        "🔓 *ᴜɴʟᴏᴄᴋ ʟɪᴠᴇꜱʜᴏᴡ*\n"
        "Tap 𝐒𝐔𝐁𝐒𝐂𝐑𝐈𝐁𝐄 and Unlock 2 VIP Channels.\n"
        "⏳ Or wait to Unlock after 24hours..."
    )

async def unlock_after_delay(user_id):
    await asyncio.sleep(86400)  # 999 seconds delay
    users[user_id]["unlocked"] = True
    try:
        await bot.send_message(
            user_id,
            f"✅ Your link is now unlocked!\n🔓 {UNLOCK_LINK}"
        )
    except:
        pass  # user may block bot

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    if message.chat.type != "private":
        return

    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = {"unlocked": False, "paid": False}
        # Start 10-second unlock timer
        asyncio.create_task(unlock_after_delay(user_id))

    await message.answer(
        text_status(user_id),
        reply_markup=main_keyboard(user_id),
        parse_mode="Markdown"
    )

@dp.callback_query_handler(lambda c: c.data == "locked")
async def locked(call: types.CallbackQuery):
    await call.answer("❌ Please wait 24Hours or pay for instant unlock or Subscribe to auto join.", show_alert=True)

# ADMIN COMMAND
@dp.message_handler(commands=["approve"])
async def approve(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(message.get_args())
        users[user_id]["paid"] = True
        users[user_id]["unlocked"] = True
        await bot.send_message(
            user_id,
            "✅ Payment Approved!\n🔓 Here is your unlock link:\n" + UNLOCK_LINK
        )
        await message.reply("Approved successfully")
    except:
        await message.reply("Usage: /approve USER_ID")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
