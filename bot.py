import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# LINKS
YT1 = "https://youtube.com/@setzis-magicworld?si=tBXL1YWZl-ndhvhm"
YT2 = "https://youtube.com/@hotmovies-q6n?si=-a58DZP_kjkXbTfN"
YT3 = "https://youtube.com/@xuezhongwen-y7b?si=ikM1rLMOmdzKc1WT"
UNLOCK_LINK = "https://t.me/+21PYHt4_VQU4Njc1"
PAYMENT_LINK = "https://connecttelegram.blogspot.com/?m=1"

# USER DATA (simple in-memory)
users = {}

def progress_bar(done):
    bars = ["🟩" if i < done else "⬜️" for i in range(3)]
    return "".join(bars)

def main_keyboard(user_id):
    done = users[user_id]["done"]

    kb = InlineKeyboardMarkup(row_width=1)

    if 1 not in done:
        kb.add(
            InlineKeyboardButton("🔴 Subscribe Channel 1", url=YT1),
            InlineKeyboardButton("✅ Done Channel 1", callback_data="done_1")
        )

    if 2 not in done:
        kb.add(
            InlineKeyboardButton("🔴 Subscribe Channel 2", url=YT2),
            InlineKeyboardButton("✅ Done Channel 2", callback_data="done_2")
        )

    if 3 not in done:
        kb.add(
            InlineKeyboardButton("🔔 Subscribe & Hit Bell", url=YT3),
            InlineKeyboardButton("✅ Done Channel 3", callback_data="done_3")
        )

    kb.add(
        InlineKeyboardButton("⚡️ Instant Unlock (Paid)", url=PAYMENT_LINK)
    )

    if len(done) >= 3 or users[user_id]["paid"]:
        kb.add(
            InlineKeyboardButton("🔓 Unlock Link", url=UNLOCK_LINK)
        )
    else:
        kb.add(
            InlineKeyboardButton("🔒 Unlock Link", callback_data="locked")
        )

    return kb

def text_status(user_id):
    done = len(users[user_id]["done"])
    return (
        "🔓 *Unlock Link*\n"
        "Complete the actions and unlock the link\n\n"
        f"📊 Progress: {done} / 3\n"
        f"{progress_bar(done)}"
    )

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    if message.chat.type != "private":
        return

    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = {"done": set(), "paid": False}

    await message.answer(
        text_status(user_id),
        reply_markup=main_keyboard(user_id),
        parse_mode="Markdown"
    )

@dp.callback_query_handler(lambda c: c.data.startswith("done_"))
async def done_task(call: types.CallbackQuery):
    user_id = call.from_user.id
    task = int(call.data.split("_")[1])

    users[user_id]["done"].add(task)

    await call.message.edit_text(
        text_status(user_id),
        reply_markup=main_keyboard(user_id),
        parse_mode="Markdown"
    )
    await call.answer("✅ Task marked as done")

@dp.callback_query_handler(lambda c: c.data == "locked")
async def locked(call: types.CallbackQuery):
    await call.answer("❌ Complete all tasks or use Instant Unlock", show_alert=True)

# ADMIN COMMAND
@dp.message_handler(commands=["approve"])
async def approve(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(message.get_args())
        users[user_id]["paid"] = True
        await bot.send_message(
            user_id,
            "✅ Payment Approved!\n🔓 Here is your unlock link:\n" + UNLOCK_LINK
        )
        await message.reply("Approved successfully")
    except:
        await message.reply("Usage: /approve USER_ID")

if name == "main":
    executor.start_polling(dp, skip_updates=True)
