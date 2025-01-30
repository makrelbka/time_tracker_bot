import asyncio
from aiogram import Bot, Dispatcher, types
import time
import pickle
import os

class ProcessData:
    def __init__(self, process_name=""):
        self.process_name = process_name
        self.start_time = time.time()
        self.process_date = ""

TOKEN = "7430942828:AAFX_RRZlXp7KsuTsyvCtS3V2n0HMVhf-_c"
bot = Bot(token=TOKEN)
dp = Dispatcher()

def read_save(user_id):
    if not os.path.exists('save.pickle') or os.path.getsize('save.pickle') == 0:
        return {}, None 
    
    with open('save.pickle', 'rb') as f:
        data = pickle.load(f)

    return data.get(user_id, ({}, None))  

def edit_save(user_id, arr, current):
    if os.path.exists('save.pickle') and os.path.getsize('save.pickle') > 0:
        with open('save.pickle', 'rb') as f:
            data = pickle.load(f)
    else:
        data = {}

    data[user_id] = (arr, current)
    
    with open('save.pickle', 'wb') as f:
        pickle.dump(data, f)

async def print_stat(arr):
    if not arr:
        return "Нет данных для отображения."

    sorted_items = sorted(arr.items(), key=lambda x: time.time() - x[1].start_time, reverse=True)
    res = "\n".join([f"{name} : {(time.time() - data.start_time) / 60:.2f} минут" for name, data in sorted_items])
    return res

@dp.message(lambda message: message.text.lower() == "stop")
async def stop_process(message: types.Message):
    user_id = message.from_user.id
    arr, _ = read_save(user_id)
    edit_save(user_id, arr, None)
    await message.answer(await print_stat(arr))

@dp.message(lambda message: message.text.lower() == "status")
async def status_process(message: types.Message):
    user_id = message.from_user.id
    arr, _ = read_save(user_id)
    await message.answer(await print_stat(arr))

@dp.message(lambda message: message.text.lower() == "/clear_save")
async def clear_save(message: types.Message):
    if os.path.exists('save.pickle'):
        os.remove('save.pickle')
    await message.answer("Сохраненные данные удалены!")

@dp.message()
async def process_message(message: types.Message):
    user_id = message.from_user.id
    arr, current = read_save(user_id)

    if current:
        current.start_time += time.time() - current.start_time

    text = message.text.lower()

    if text not in arr:
        arr[text] = ProcessData(text)

    current = arr[text]
    current.start_time = time.time()

    edit_save(user_id, arr, current)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())