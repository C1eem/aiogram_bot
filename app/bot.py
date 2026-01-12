import asyncio
from aiogram import types, F
from aiogram import Dispatcher, Bot
from aiogram.filters import Command
from dotenv import load_dotenv

from app.database.crud.history_crud import HistoryCRUD
from app.database.crud.user_crud import UserCRUD
from app.database.session import AsyncSessionLocal

from app.open_router_api import OpenRouterAPI
from app.payment import *
from app.database.session import engine, Base
import os

or_api = OpenRouterAPI()

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.message.register(send_invoice_handler, Command(commands="donate"))
dp.pre_checkout_query.register(pre_checkout_handler)
dp.message.register(success_payment_handler, F.successful_payment)
dp.message.register(pay_support_handler, Command(commands="paysupport"))

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply(f"Hello, {message.from_user.first_name}!")

@dp.message(Command("history"))
async def get_history(message: types.Message):
    async with AsyncSessionLocal() as db_session:
        user = await UserCRUD.get_by_tg_id(db_session, message.from_user.id)
        try:
            history = await HistoryCRUD.get_history(db_session, user.id)
            response_text = "📜 Ваша история:\n\n"
            for i, hist in enumerate(history[:5], 1):  # последние 5
                response_text += f"{i}. ❓ {hist.user_request[:50]}...\n"
                response_text += f"   💬 {hist.model_response[:50]}...\n"
                response_text += f"   Model: {hist.model[:50]}...\n\n"
            await message.reply(response_text)
        except Exception as e:
            print(f"Произошла ошибка при попытке получить историю: {e}")
            await message.reply(f"Что-то пошло не так, возможно ваша история пуста")

@dp.message(Command("del_history"))
async def del_history(message: types.Message):
    async with AsyncSessionLocal() as db_session:
        try:
            user = await UserCRUD.get_by_tg_id(db_session, message.from_user.id)
            await HistoryCRUD.delete(db_session, user.id)
            await message.reply("История успешно удалена")
        except Exception as e:
            print(f"Произошла ошибка при удалении истории: {e}")
            await message.reply("Что-то пошло не так")

@dp.message(Command("llama"))
async def llama(message: types.Message):
    async with AsyncSessionLocal() as db_session:
        user = await UserCRUD.update_model(
            db_session,
            tg_id=message.from_user.id,
            model="meta-llama/llama-3.3-70b-instruct:free"
        )
        await message.reply("Model selected: llama")

@dp.message(Command("gpt"))
async def llama(message: types.Message):
    async with AsyncSessionLocal() as db_session:
        user = await UserCRUD.update_model(
            db_session,
            tg_id=message.from_user.id,
            model="openai/gpt-oss-20b:free"
        )
        await message.reply("Model selected: gpt")

@dp.message()
async def response(message: types.Message):
    async with AsyncSessionLocal() as db_session:
        user = await UserCRUD.get_by_tg_id(db_session, message.from_user.id)
        user_tg_id = message.from_user.id
        user_name = message.from_user.first_name
        if not user:
            user = await UserCRUD.create(
                db_session,
                name=user_name,
                tg_id=user_tg_id,
                model="meta-llama/llama-3.3-70b-instruct:free"
            )

        data = await or_api.response(message.text, model=user.model)
        question = message.text
        answer = data
        history = await HistoryCRUD.create(
            db_session,
            user_id=user.id,
            user_request=question,
            model_response=answer,
            model=user.model
        )

        await message.reply(data)

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ БД готова")

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())