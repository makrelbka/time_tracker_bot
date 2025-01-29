import asyncio
from aiogram import Bot, Dispatcher, types
import datetime
import pickle
import os

class ProcessData:
    def __init__(self):
        self.process_name = ""
        self.start_time = 0
        self.process_date = ""
        self.arr = {}

    def clear(self):
        self.arr = {}
        self.process_name = ""
        self.start_time = 0
        self.process_date = ""


TOKEN = "7430942828:AAFX_RRZlXp7KsuTsyvCtS3V2n0HMVhf-_c"
bot = Bot(token=TOKEN)
dp = Dispatcher()

def read_save(user_id):
    if not os.path.exists('save.pickle') or os.path.getsize('save.pickle') == 0:
        return ProcessData()
    
    with open('save.pickle', 'rb') as f:
        data = pickle.load(f)

    return data.get(user_id, ProcessData())

def edit_save(user_id, current):
    if os.path.exists('save.pickle') and os.path.getsize('save.pickle') > 0:
        with open('save.pickle', 'rb') as f:
            data = pickle.load(f)
    else:
        data = {}

    data[user_id] = current
    print("|", current.arr)
    with open('save.pickle', 'wb') as f:
        pickle.dump(data, f)

async def print_stat(arr):
    res = ""
    if not arr: 
        return "Нет данных для отображения."
    
    arr = sorted(arr.items(), key=lambda item: item[1], reverse=True)
    for i in arr:
        res += f"{i[0]} : {i[1] / 60:.2f} минут\n"
    return res

@dp.message()
async def answer(message: types.Message):
    user_id = message.from_user.id
    current = read_save(user_id)

    if current.process_name:
        if current.process_name in current.arr:
            current.arr[current.process_name] += (datetime.datetime.now() - current.start_time).total_seconds()
        else:
            current.arr[current.process_name] = (datetime.datetime.now() - current.start_time).total_seconds()
    print(current.arr)
    current.process_date = message.text
    current.start_time = datetime.time()
    if message.text == "stop":
        current.clear()
        edit_save(user_id, current)
        await message.answer(await print_stat(current.arr))  
    elif message.text == "status":
        await message.answer(await print_stat(current.arr))

    edit_save(user_id, current)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())