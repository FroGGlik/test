import asyncio
import logging
import os
import datetime
import re


async def updating(filename: str, tasks: list) -> None:
    last_mtime = os.path.getmtime(filename)
    while True:
        current_mtime = os.path.getmtime(filename)

        if current_mtime > last_mtime:
            logging.info(f'Файл {filename} был изменен')
            tasks.clear()
            tasks.extend(load_tasks(filename))
            print(f'Задачи обновлены: {tasks}')
            logging.info('Задачи обновлены')

        await asyncio.sleep(10)


async def notify(tasks: list) -> None:
    to_remove = []
    while True:
        now = datetime.datetime.now().time().strftime('%H:%M')
        for task in tasks:
            if task[0] == now:
                print(f'Напоминание: {task[1]}')
                logging.info(f'Отправлено напоминание: {task[1]}')
                to_remove.append(task)

        for task in to_remove:
            tasks.remove(task)

        await asyncio.sleep(1)


def load_tasks(filename: str) -> list:
    tasks = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                times = re.findall(r'\d\d:\d\d', line)
                if not times:
                    continue

                time = times[0]
                text = re.sub(r'\d\d:\d\d', '', line).strip()
                tasks.append((time, text))

        logging.info('Все задачи считаны из файла')
        return tasks
    except Exception as ex:
        logging.error(f'Ошибка чтения файла: {ex}')
        print(f'Ошибка чтения файла: {ex}')
        return tasks

def exists(filename: str) -> bool:
    if not os.path.exists(filename):
        logging.error(f'Файл {filename} не найден')
        print(f'Файл {filename} не найден')
        return False
    return True


def empty(filename: str) -> bool:
    if os.path.getsize(filename) == 0:
        logging.error(f'Файл {filename} пуст')
        print(f'Файл {filename} пуст')
        return True
    return False


async def main():
    logging.info('Приложение запущено')

    file = 'tasks.txt'

    if not exists(file) or empty(file):
        logging.info('Не удалось начать обработку задач. Приложение остановлено.')
        print('Не удалось начать обработку задач. Приложение остановлено.')
        return
    
    tasks = load_tasks(file)

    if not tasks:
        logging.info('Нет задач для обработки. Приложение остановлено.')
        print('Нет задач для обработки. Приложение остановлено.')
        return
    
    print('Задачи загружены: ')
    for task in tasks:
        print(task)

    await asyncio.gather(
        notify(tasks),
        updating(file, tasks)
    )


if __name__ == '__main__':
    logging.basicConfig(
        filename='logs.txt',
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(messsage)s',
        encoding='utf-8'
    )
    asyncio.run(main())