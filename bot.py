from aiogram import Bot, Dispatcher, types
import asyncio
import time
import pickle
import os
import datetime

class ProcessData:
    def __init__(self):
        self.process_name = ""
        self.start_time = time.time()
        self.process_date = ""

TOKEN = "7430942828:AAFX_RRZlXp7KsuTsyvCtS3V2n0HMVhf-_c"
bot = Bot(token=TOKEN)
dp = Dispatcher()

def read_save(user_id):
    if not os.path.exists('save.pickle') or os.path.getsize('save.pickle') == 0:
        return {}, ProcessData(), {}

    with open('save.pickle', 'rb') as f:
        data = pickle.load(f)

    return data.get(user_id, ({}, ProcessData(), {}))

def edit_save(user_id, arr, current, history):
    if os.path.exists('save.pickle') and os.path.getsize('save.pickle') > 0:
        with open('save.pickle', 'rb') as f:
            data = pickle.load(f)
    else:
        data = {}

    data[user_id] = (arr, current, history)
    with open('save.pickle', 'wb') as f:
        pickle.dump(data, f)

def load_data():
    if not os.path.exists('save.pickle') or os.path.getsize('save.pickle') == 0:
        return {} 

    with open('save.pickle', 'rb') as f:
        return pickle.load(f) 

async def print_stat(arr):
    res = ""
    if not arr: 
        return "Нет данных для отображения."

    arr = {key: value if value is not None else 0 for key, value in arr.items()}

    arr = sorted(arr.items(), key=lambda item: item[1], reverse=True)

    for process_name, process_time in arr[:-1]:
        res += f"{process_name} : {process_time / 60:.2f} минут\n"
    if res == "":
        return"Нет данных для отображения."
    return res
    

async def time_edit(arr, current):
    if current.process_name:
        if current.process_name in arr:
            return arr[current.process_name] + time.time() - current.start_time
        else:
            return time.time() - current.start_time

async def daily_task():
    while True:
        now = datetime.datetime.now()
        midnight = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)
        sleep_time = (midnight - now).total_seconds()

        await asyncio.sleep(sleep_time)

        data = load_data()
        if not data:
            continue  

        for user_id, (arr, current, history) in data.items():
            arr[current.process_name] = await time_edit(arr, current)  
            date_key = now.strftime("%d:%m:%Y")
            history[date_key] = arr.copy()

            data[user_id] = ({}, ProcessData(), history)
            
            progress_text = f"📅 Итог за {date_key}:\n\n" + await print_stat(arr)
            try:
                await bot.send_message(user_id, progress_text)
            except Exception as e:
                print(f"Ошибка отправки сообщения пользователю {user_id}: {e}")

        with open('save.pickle', 'wb') as f:
            pickle.dump(data, f)

@dp.message(lambda message: message.text.lower().startswith("/history"))
async def history_command(message: types.Message):
    user_id = message.from_user.id
    _, _, history = read_save(user_id)

    splited_message = message.text.split()
    if len(splited_message) == 2:
        date_key = splited_message[1]
        if date_key in history:
            await message.answer(await print_stat(history[date_key]))
        else:
            await message.answer(f"Нет данных за {date_key}")
    else:
        await message.answer("Используйте команду: /history <дд:мм:гггг>")

@dp.message(lambda message: message.text.lower() == "/help" or message.text.lower() == "/start")
async def answer(message: types.Message):
    help_text = (
        "Просто отправьте название процесса, и бот начнёт его отслеживать\n\n"
        "*Доступные команды:*\n\n"
        "– */help*: показать этот список команд\n"
        "– */stop*: остановить текущий процесс и сохранить его\n"
        "– */status*: показать сохранённые данные"
        "– */edit  \\<имя процесса\\> \\<время\\>*: изменить время процесса\n"
        "– */delete\\_process \\<имя процесса\\>*: удалить данные о процессе\n"
        "– */clear\\_save* : удалить все сохранённые данные\n"  
    )

    await message.answer(help_text, parse_mode="MarkdownV2")

@dp.message(lambda message: message.text.lower() == "/clear_save")
async def answer(message: types.Message): 
    user_id = message.from_user.id
    edit_save(user_id, {} , ProcessData(), {})
    await message.answer("Сохранение очищено")

@dp.message(lambda message: message.text.lower().startswith("/delete_process"))
async def answer(message: types.Message):
    user_id = message.from_user.id
    arr, current, history = read_save(user_id)

    arr[current.process_name] = await time_edit(arr, current)
    splited_message = message.text.lower().split()
    if len(splited_message) == 2:
        arr.pop(splited_message[1], None)
        if current.process_name == splited_message[0]:
            current = ProcessData()
        edit_save(user_id, arr, current, history)
        await message.answer("Удалены данные о процессе: " + splited_message[1])
        return

    await message.answer("Неверный формат команды. Используйте: /delete_process + <имя процесса>")
    return

@dp.message(lambda message: message.text.lower().startswith("/edit"))
async def answer(message: types.Message): 
    user_id = message.from_user.id
    arr, current, history = read_save(user_id)
    splited_message = message.text.split()
    if len(splited_message) != 3 or not splited_message[2].isdigit() or not splited_message[1]:
        await message.answer("Неверный формат команды. Используйте: edit <имя процесса> <знак> <значение в минутах>")
        return

    process_name = splited_message[1].lower()
    value = splited_message[2]
    arr[process_name] = arr.get(process_name, 0) + int(value) * 60
    edit_save(user_id, arr, current, history)
    await message.answer(f"{process_name} : {arr[process_name] / 60:.2f} минут\n")


@dp.message(lambda message: message.text.lower() == "/stop" )
async def answer(message: types.Message):
    user_id = message.from_user.id
    arr, current, history = read_save(user_id)

    arr[current.process_name] = await time_edit(arr, current)
    
    current = ProcessData()
    edit_save(user_id, arr, current, history)
    await message.answer(await print_stat(arr)) 


@dp.message(lambda message: message.text.lower().startswith("/status"))
async def answer(message: types.Message):
    user_id = message.from_user.id
    arr, current, _ = read_save(user_id)

    arr[current.process_name] = await time_edit(arr, current)
    splited_message = message.text.lower().split()
    if len(splited_message) == 2:
        await message.answer(arr[splited_message[1]])
        return
    if len(splited_message) == 1:
        await message.answer(await print_stat(arr))
        return 

    await message.answer("Неверный формат команды. Используйте: /status или /status + <имя процесса>")
    return
    
@dp.message()
async def answer(message: types.Message):
    user_id = message.from_user.id
    arr, current, history = read_save(user_id)

    arr[current.process_name] = await time_edit(arr, current)
    current.process_name = message.text.lower()
    current.start_time = time.time()

    edit_save(user_id, arr, current, history)

async def main():
    asyncio.create_task(daily_task())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())