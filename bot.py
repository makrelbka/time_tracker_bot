import asyncio
import time
from aiogram import Bot, Dispatcher, types

TOKEN = "7430942828:AAFX_RRZlXp7KsuTsyvCtS3V2n0HMVhf-_c"
bot = Bot(token=TOKEN)
dp = Dispatcher()
arr = {}
current = []

def print_stat(arr):
    res = ""
    arr = sorted(arr.items(), key=lambda item: item[1], reverse=True)
    for i in arr:
        res += f"{i[0]} : {i[1] / 60:.2f} минут\n"
    return res

@dp.message(lambda message: message.text and message.text.lower() == 'status')
async def print_status(message: types.Message):
    await message.answer(print_stat(arr))

@dp.message(lambda message: message.text and message.text.lower() == 'stop')
async def print_status(message: types.Message):
    global current 
    current = []
    await message.answer(print_stat(arr))

@dp.message()
async def answer(message: types.Message):
    global current 
    if current:
        if current[0] in arr:
            arr[current[0]] += time.time() - current[1]
        else:
            arr[current[0]] = time.time() - current[1]
    current = [message.text, time.time()]

    # if message.text == "stop":
    #     current = []
    #     await message.answer(print_stat(arr))
    # if message.text == "status":
    #     await message.answer(print_stat(arr))

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())