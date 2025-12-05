import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import google.generativeai as genai
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

TOKEN = os.getenv("BOT_TOKEN")  #
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# Gemini Configuration
genai.configure(api_key=GEMINI_KEY)

MY_CHAT_ID = os.getenv("MY_ADMIN_ID")
CITY = "Kaiserslautern"

model = genai.GenerativeModel("gemini-2.5-flash")

bot = Bot(token=TOKEN)
dp = Dispatcher()

scheduler = AsyncIOScheduler()


logging.basicConfig(level=logging.INFO)

varwords = ['Help', 'help', 'HELP', 'Support', 'Info', 'Commands', 'assist']


ai_mode_users = set()


# buttons
def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🤖 Turn AI On")
    builder.button(text="🛑 Turn AI Off")
    builder.button(text="📜 Commands")
    builder.button(text="🌤 Weather")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


# weather for all users (odessa or kaiserslautern)
async def get_weather_forecast(city_name):
    try:
        url = f"https://wttr.in/{city_name}?format=%C+%t+%w"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    raw_weather = await response.text()
                else:
                    return "Failed to fetch weather data."

        prompt = (
            f"Briefly and cheerfully describe the weather in {city_name}. "
            f"Data: {raw_weather}. "
            f"Give outfit advice. Style: friendly bro. Language: English. (Send for Telegram, use appropriate formatting)."
        )
        gemini_response = await model.generate_content_async(prompt)

        return gemini_response.text

    except Exception as e:
        return f"Weather Error: {e}"


def get_city_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🇩🇪 Kaiserslautern", callback_data="city_Kaiserslautern")
    builder.button(text="🇺🇦 Odessa", callback_data="city_Odessa")
    builder.adjust(1)
    return builder.as_markup()


#personal weather notification
async def send_morning_weather():
    try:
        # 1. raw weather
        url = f"https://wttr.in/{CITY}?format=%C+%t+%w"  # Format: Condition, Temp, Wind
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    raw_weather = await response.text()
                else:
                    raw_weather = "no data"

        # 2. Gemini weather prompt
        prompt = (
            f"Write a very short, funny, and friendly good morning wish for Sergey. "
            f"Current weather in {CITY}: {raw_weather}. "
            f"Give advice on what to wear or take with you based on the weather. No fluff. Language: English. (Send for Telegram, use appropriate formatting)."
        )

        gemini_response = await model.generate_content_async(prompt)
        text_to_send = gemini_response.text

        # 3. personal weather notification
        clean_text = text_to_send.replace("**", "*")
        try:
            await bot.send_message(chat_id=MY_CHAT_ID, text=clean_text, parse_mode="Markdown")
        except Exception:
            # If formatting fails, send as is
            await bot.send_message(chat_id=MY_CHAT_ID, text=clean_text)

    except Exception as e:
        print(f"Error sending weather: {e}")


# --- HANDLERS ---

# 1. /start
@dp.message(Command("start"))
async def start(message: types.Message):
    # Print ID and keyboard on start
    await message.answer(
        f"Greetings! \nYour personal robot is at your service.",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )


# 2. words check
@dp.message(F.text.in_(varwords))
@dp.message(F.text == "📜 Commands")
async def help_handler(message: types.Message):
    await message.answer("Here is the list of commands:\n/ai - Turn AI On\n/quit - Turn AI Off")


# 3. Button Ai on
@dp.message(Command("ai"))
@dp.message(F.text == "🤖 Turn AI On")
async def enable_ai_mode(message: types.Message):
    ai_mode_users.add(message.from_user.id)
    await message.answer("✅ **AI Mode Enabled.**",
                         parse_mode="Markdown")


@dp.message(Command("quit"))
@dp.message(F.text == "🛑 Turn AI Off")
async def disable_ai_mode(message: types.Message):
    user_id = message.from_user.id
    if user_id in ai_mode_users:
        ai_mode_users.discard(user_id)
    await message.answer("❌ **AI Mode Disabled.**", parse_mode="Markdown")


@dp.message(F.text == "🌤 Weather")
async def weather_button_handler(message: types.Message):
    await message.answer("Choose a city:", reply_markup=get_city_keyboard())


@dp.callback_query(F.data.startswith("city_"))
async def city_callback_handler(callback: types.CallbackQuery):

    city_chosen = callback.data.split("_")[1]

    await callback.answer("Checking weather...")

    weather_text = await get_weather_forecast(city_chosen)

    await callback.message.answer(
        weather_text.replace("**", "*"),
        parse_mode="Markdown"
    )


# main message process
@dp.message()
async def main_handler(message: types.Message):
    user_id = message.from_user.id

    # Ai on
    if user_id in ai_mode_users:
        try:
            await bot.send_chat_action(chat_id=message.chat.id, action="typing")
            # prompt
            response = await model.generate_content_async(message.text)

            if response.text:
                # markdown edit
                await message.answer(
                    response.text.replace("**", "*"),
                    parse_mode="Markdown"
                )
            else:
                await message.answer("Gemini remained silent (empty response).")

        except Exception as e:
            await message.answer(f"Gemini Error: {e}")

    # Ai off
    else:
        await message.answer("Error(x) - unknown message")


# --- Strart ---
async def main():
    print("Bot started")

    #time change hour=x, minute=y
    scheduler.add_job(send_morning_weather, 'cron', hour=8, minute=0)
    scheduler.start()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")