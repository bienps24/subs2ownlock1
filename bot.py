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
YT1 = "https://youtube.com/@setzis-magicworld?si=tBXL1YWZl-ndhvhm"
YT2 = "https://gperya.com/?outValue=llIdkrI&appId=com.waiudieay.sxkzriagxs&install_referrer=h5&aid=39&share_referrer=101"
YT3 = "https://youtube.com/@xuezhongwen-y7b?si=ikM1rLMOmdzKc1WT"
UNLOCK_LINK = "https://t.me/+21PYHt4_VQU4Njc1"
PAYMENT_LINK = "https://connecttelegram.blogspot.com/?m=1"

# USER DATA (in-memory)
users = {}

def progress_bar(done):
    bars = ["🟩" if i < done else "⬜️" for i in range(3)]
    return "".join(bars)

def main_keyboard(user_id):
    kb = InlineKeyboardMarkup(row_width=1)
    # Show channels only
    kb.add(
        InlineKeyboardButton("🔴 Subscribe Channel 1", url=YT1),
        InlineKeyboardButton("🔴 Subscribe Channel 2", url=YT2),
        InlineKeyboardButton("🔔 Subscribe Channel 3", url=YT3),
    )

    # Payment option
    kb.add(InlineKeyboardButton("⚡️ Instant Unlock (Paid)", url=PAYMENT_LINK))

    # Unlock link logic
    if users[user_id]["unlocked"]:
        kb.add(InlineKeyboardButton("🔓 Unlock Link", url=UNLOCK_LINK))
    else:
        kb.add(InlineKeyboardButton("🔒 Unlock Link", callback_data="locked"))

    return kb

def text_status(user_id):
    return (
        "🔓 *Unlock Link*\n"
        "Please subscribe to the channels above.\n"
        "⏳ Unlock available after 999 seconds..."
    )

async def unlock_after_delay(user_id):
    await asyncio.sleep(999)  # 999 seconds delay
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
    await call.answer("❌ Please wait 999 seconds or pay for instant unlock.", show_alert=True)

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
