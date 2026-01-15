import asyncio
import config
import psycopg2
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
import datetime

DATABASE_URL = config.URL

dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(msg: types.Message) -> None:
    await msg.answer(
        text="Привет! Я бот для заметок.\n"
        "С моей помощью ты можешь:\n"
        "- вставить заметку с помощью команды /add <заметка>\n"
        "- отредактировать заметку с помощью команды /edit <номер_заметки> <отредактированная_заметка>\n"
        "- удалить заметку с помощью команды /delete <номер_заметки>\n"
        "- просмотреть свои заметки с помощью команды /notes"
    )


@dp.message(Command("notes"))
async def cmd_select(msg: types.Message) -> None:
    user_id = msg.from_user.id
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()    
    cursor.execute(
        "SELECT * FROM notes WHERE user_id = %s ORDER BY id",
        (user_id,)
    )
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if not result:
        await msg.answer("У вас пока нет заметок.")
        return
    
    notes_text = ""
    for row in result:
        note_id, note_user_id, note_content, note_date = row
        note_text = str(note_content)
        formatted_date = f"{note_date.day}.{note_date.month}.{note_date.year}"
        notes_text += f"{note_id}: {note_text} ({formatted_date})\n"
    
    await msg.answer(text=f"Ваши заметки: \n{notes_text}")


@dp.message(Command("add"))
async def cmd_insert(msg: types.Message) -> None:
    user_id = msg.from_user.id
    
    try:
        note_text = msg.text[len('/add '):].strip()
        if not note_text:
            raise ValueError("Пустая заметка.")
        
        date = datetime.datetime.now().date()
    except (ValueError, IndexError):
        await msg.answer("Некорректный ввод. Попробуйте команду /add <заметка>.")
        return

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO notes (user_id, note, creation_date)
        VALUES (%s, %s, %s)
        """,
        (user_id, note_text, date)
    )

    conn.commit()
    cursor.close()
    conn.close()

    await msg.answer(text="Заметка сохранена!")


@dp.message(Command("edit"))
async def cmd_edit(msg: types.Message) -> None:
    user_id = msg.from_user.id
    
    try:
        splitted_msg = msg.text.split(" ", 2)
        note_id = int(splitted_msg[1])
        new_note = splitted_msg[2].strip()
        
        if not new_note:
            raise ValueError("Пустая заметка.")
        
        new_date = datetime.datetime.now().date()

    except (ValueError, IndexError):
        await msg.answer("Некорректный ввод. Попробуйте команду /edit <номер_заметки> <отредактированная_заметка>.")
        return

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM notes WHERE id = %s AND user_id = %s",
        (note_id, user_id)
    )
    note_exists = cursor.fetchone()
    
    if not note_exists:
        await msg.answer("Заметка не найдена.")
        cursor.close()
        conn.close()
        return

    cursor.execute(
        """
        UPDATE notes
        SET note = %s, creation_date = %s
        WHERE id = %s AND user_id = %s
        """,
        (new_note, new_date, note_id, user_id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    await msg.answer(text="Заметка обновлена! Используйте /notes, чтобы увидеть изменения.")


@dp.message(Command("delete"))
async def cmd_delete(msg: types.Message) -> None:
    user_id = msg.from_user.id
    
    try:
        note_id = int(msg.text.split(" ")[1])
    except (ValueError, IndexError):
        await msg.answer("Некорректный ввод. Попробуйте команду /delete <номер_заметки>.")
        return

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id FROM notes WHERE id = %s AND user_id = %s",
        (note_id, user_id)
    )
    note_exists = cursor.fetchone()
    
    if not note_exists:
        await msg.answer("Заметка не найдена.")
        cursor.close()
        conn.close()
        return
    
    cursor.execute(
        "DELETE FROM notes WHERE id = %s AND user_id = %s",
        (note_id, user_id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    await msg.answer(text="Заметка удалена!")


async def main() -> None:
    bot = Bot(config.BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == '__main__':
    print("Бот работает...")
    asyncio.run(main())
