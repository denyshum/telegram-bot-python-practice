import telebot
import threading
import time
from telebot import types
from datetime import datetime
from classes import Task, TaskManager, Reminder, Reminders

token = "8208626469:AAGVVpXpmi6sU4nFfbev7xhlbESVFQRPba0"
bot = telebot.TeleBot(token)

task_manager = TaskManager()
reminders = Reminders()

user_states = {}
user_data = {}

def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('📋 Завдання', '🔔 Нагадування')
    keyboard.row('📊 Статистика', '💾 Зберегти')
    keyboard.row('❓ Допомога')
    return keyboard

def tasks_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('➕ Додати', '✅ Статус', '✏️ Редагувати')
    keyboard.row('🔍 Пошук', '📝 Список')
    keyboard.row('🗑 Видалити', '↩️ Назад')
    return keyboard

def reminders_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('➕ Створити', '✏️ Редагувати', '📝 Список')
    keyboard.row('🔍 Пошук', '📤 Надіслати', '⏰ Відкласти')
    keyboard.row('🗑 Видалити', '↩️ Назад')
    return keyboard

def priority_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.row('високий', 'середній', 'низький')
    return keyboard

def status_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.row('нове', 'в роботі', 'виконане')
    return keyboard

def type_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.row('telegram', 'push', 'sms')
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_states[user_id] = None
    user_data[user_id] = {}
    
    bot.send_message(message.chat.id, f"Вітаю, {message.from_user.first_name}! 👋\n\nЯ бот-менеджер завдань та нагадувань.\nОберіть дію з меню:",
        reply_markup=main_keyboard())

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
📚 <b>ДОВІДКА</b>

<b>📋 ЗАВДАННЯ:</b>
➕ Додати — створити нове завдання
✅ Статус — швидка зміна статусу (нове/в роботі/виконане)
✏️ Редагувати — змінити будь-яке поле завдання
🔍 Пошук — знайти за назвою, пріоритетом, категорією
📝 Список — перегляд завдань (із <b>фільтрами та сортуванням</b>)
🗑 Видалити — видалити завдання назавжди

<b>🔔 НАГАДУВАННЯ:</b>
➕ Створити — додати нагадування
✏️ Редагувати — змінити час, текст або тип
🔍 Пошук — знайти нагадування за текстом або датою
📝 Список — перегляд (із <b>фільтрами та сортуванням</b>)
📤 Надіслати — надіслати повідомлення вручну
⏰ Відкласти — перенести час нагадування
🗑 Видалити — видалити нагадування

<b>КОМАНДИ:</b>
/start — перезапустити бота
/help — показати це повідомлення
/cancel — скасувати поточну дію (введення)
"""
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')

@bot.message_handler(commands=['cancel'])
def cancel(message):
    user_id = message.from_user.id
    user_states[user_id] = None
    user_data[user_id] = {}
    bot.send_message(message.chat.id, "❌ Операцію скасовано", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text in ['📋 Завдання', '🔔 Нагадування', '📊 Статистика', '💾 Зберегти', '❓ Допомога', '↩️ Назад'])
def main_menu_handler(message):
    text = message.text
    user_id = message.from_user.id
    
    if text == '📋 Завдання':
        user_states[user_id] = 'tasks_menu'
        bot.send_message(message.chat.id, "Меню завдань:", reply_markup=tasks_keyboard())
    
    elif text == '🔔 Нагадування':
        user_states[user_id] = 'reminders_menu'
        bot.send_message(message.chat.id, "Меню нагадувань:", reply_markup=reminders_keyboard())
    
    elif text == '📊 Статистика':
        show_statistics(message)
    
    elif text == '💾 Зберегти':
        task_manager.save_to_file("dataTasks.txt")
        reminders.save_to_file("dataReminders.txt")
        bot.send_message(message.chat.id, "✅ Дані збережено!")
    
    elif text == '❓ Допомога':
        help_command(message)
    
    elif text == '↩️ Назад':
        user_states[user_id] = None
        bot.send_message(message.chat.id, "Головне меню:", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == '📝 Список' and user_states.get(message.from_user.id) != 'reminders_menu')
def show_tasks_list(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Всі", callback_data="tasks_all"))
    markup.add(types.InlineKeyboardButton("Активні", callback_data="tasks_active"))
    markup.add(types.InlineKeyboardButton("Виконані", callback_data="tasks_completed"))
    markup.add(types.InlineKeyboardButton("Прострочені", callback_data="tasks_overdue"))
    markup.add(types.InlineKeyboardButton("Термінові", callback_data="tasks_urgent"))
    
    bot.send_message(message.chat.id, "Оберіть фільтр:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '✏️ Редагувати' and user_states.get(message.from_user.id) == 'tasks_menu')
def edit_task_start(message):
    user_id = message.from_user.id
    user_states[user_id] = 'edit_task_name'
    user_data[user_id] = {}
    bot.send_message(message.chat.id, "Введіть назву завдання, яке хочете змінити:", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: message.text == '✏️ Редагувати' and user_states.get(message.from_user.id) == 'reminders_menu')
def edit_reminder_start(message):
    user_id = message.from_user.id
    user_states[user_id] = 'edit_reminder_number'
    user_data[user_id] = {}
    bot.send_message(message.chat.id, "Введіть номер нагадування для редагування:", reply_markup=types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda call: call.data.startswith('tasks_'))
def tasks_filter_step(call):
    filter_type = call.data.split('_')[1]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📅 За дедлайном", callback_data=f"sort_tasks_{filter_type}_deadline"))
    markup.add(types.InlineKeyboardButton("🔥 За пріоритетом", callback_data=f"sort_tasks_{filter_type}_priority"))
    markup.add(types.InlineKeyboardButton("📋 Без сортування", callback_data=f"sort_tasks_{filter_type}_none"))
    
    bot.edit_message_text("Тепер оберіть сортування:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('sort_tasks_'))
def show_tasks_final(call):
    parts = call.data.split('_')
    filter_type = parts[2]
    sort_type = parts[3]
    
    tasks = task_manager._TaskManager__tasks[:]
    title_suffix = ""

    if filter_type == "active":
        tasks = [t for t in tasks if t.get('status') in ['нове', 'в роботі']]
        title_suffix = "(Активні)"
    elif filter_type == "completed":
        tasks = [t for t in tasks if t.get('status') == 'виконане']
        title_suffix = "(Виконані)"
    elif filter_type == "overdue":
        today = datetime.now().strftime("%Y-%m-%d")
        tasks = [t for t in tasks if t.get('deadline') < today and t.get('status') != 'виконане']
        title_suffix = "(Прострочені)"
    elif filter_type == "urgent":
        tasks = [t for t in tasks if t.get('priority') == 'високий' and t.get('status') != 'виконане']
        title_suffix = "(Термінові)"
    
    if sort_type == "deadline":
        tasks.sort(key=lambda x: x.get('deadline'))
    elif sort_type == "priority":
        prio_map = {'високий': 1, 'середній': 2, 'низький': 3}
        tasks.sort(key=lambda x: prio_map.get(x.get('priority'), 4))
    
    if not tasks:
        bot.edit_message_text("❌ Завдань за цими критеріями не знайдено", call.message.chat.id, call.message.message_id)
        return

    message_text = f"<b>СПИСОК ЗАВДАНЬ {title_suffix}</b>\n\n"
    for i, task in enumerate(tasks, 1):
        status_emoji = "✅" if task.get('status') == 'виконане' else "⏳"
        prio = task.get('priority')
        p_emoji = "🔴" if prio == 'високий' else "🟡" if prio == 'середній' else "🟢"
        
        message_text += f"{i}. {status_emoji} <b>{task.get('name')}</b>\n"
        message_text += f"   {p_emoji} {prio} | {task.get('status')}\n"
        message_text += f"   📅 {task.get('deadline')} | 📂 {task.get('category')}\n"
        message_text += f"   📝 {task.get('description')}\n\n"
    
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id, parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == '➕ Додати')
def add_task_start(message):
    user_id = message.from_user.id
    user_states[user_id] = 'add_task_name'
    user_data[user_id] = {}
    
    bot.send_message(
        message.chat.id,
        "📝 Створення нового завдання\n\nВведіть назву завдання:",
        reply_markup=types.ReplyKeyboardRemove()
    )

@bot.message_handler(func=lambda message: message.text == '🔍 Пошук' and user_states.get(message.from_user.id) == 'tasks_menu')
def search_task_start(message):
    user_id = message.from_user.id
    user_states[user_id] = 'search_task_field'
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.row('назва', 'пріоритет')
    keyboard.row('статус', 'категорія')
    keyboard.row('дедлайн', '↩️ Скасувати')
    
    bot.send_message(
        message.chat.id,
        "🔍 Пошук завдань\n\nОберіть критерій пошуку:",
        reply_markup=keyboard
    )

@bot.message_handler(func=lambda message: message.text == '🔍 Пошук' and user_states.get(message.from_user.id) == 'reminders_menu')
def search_reminder_start(message):
    user_id = message.from_user.id
    user_states[user_id] = 'search_reminder_field'
    user_data[user_id] = {}
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.row('номер', 'завдання', 'дата')
    keyboard.row('тип', 'повідомлення')
    keyboard.row('↩️ Скасувати')
    
    bot.send_message(
        message.chat.id,
        "🔍 Пошук нагадувань\n\nОберіть критерій пошуку:",
        reply_markup=keyboard
    )

@bot.message_handler(func=lambda message: message.text == '🗑 Видалити' and user_states.get(message.from_user.id) == 'tasks_menu')
def delete_task_start(message):
    user_id = message.from_user.id
    user_states[user_id] = 'delete_task'
    user_data[user_id] = {}
    
    bot.send_message(
        message.chat.id,
        "🗑 Видалення завдання\n\nВведіть назву завдання для видалення:",
        reply_markup=types.ReplyKeyboardRemove()
    )

@bot.message_handler(func=lambda message: message.text == '📝 Список' and user_states.get(message.from_user.id) == 'reminders_menu')
def show_reminders_list(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Всі", callback_data="reminders_all"))
    markup.add(types.InlineKeyboardButton("Невідправлені", callback_data="reminders_pending"))
    markup.add(types.InlineKeyboardButton("Відправлені", callback_data="reminders_sent"))
    markup.add(types.InlineKeyboardButton("Активні", callback_data="reminders_active"))
    
    bot.send_message(message.chat.id, "Оберіть фільтр:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('reminders_'))
def reminders_filter_step(call):
    filter_type = call.data.split('_')[1]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🕒 За часом", callback_data=f"sort_remind_{filter_type}_time"))
    markup.add(types.InlineKeyboardButton("📱 За типом", callback_data=f"sort_remind_{filter_type}_type"))
    markup.add(types.InlineKeyboardButton("📋 Без сортування", callback_data=f"sort_remind_{filter_type}_none"))
    
    bot.edit_message_text("Тепер оберіть сортування:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('sort_remind_'))
def show_reminders_final(call):
    parts = call.data.split('_')
    filter_type = parts[2]
    sort_type = parts[3]
    
    reminders_data = reminders._Reminders__reminders[:]
    title_suffix = ""

    if filter_type == "pending":
        reminders_data = [r for r in reminders_data if not r.get('is_sent')]
        title_suffix = "(Невідправлені)"
    elif filter_type == "sent":
        reminders_data = [r for r in reminders_data if r.get('is_sent')]
        title_suffix = "(Відправлені)"
    elif filter_type == "active":
        reminders_data = [r for r in reminders_data if r.check_time()]
        title_suffix = "(Активні)"

    if sort_type == "time":
        reminders_data.sort(key=lambda x: x.get('reminder_datetime'))
    elif sort_type == "type":
        reminders_data.sort(key=lambda x: x.get('type'))

    if not reminders_data:
        bot.edit_message_text("❌ Нагадувань не знайдено", call.message.chat.id, call.message.message_id)
        return

    message_text = f"<b>СПИСОК НАГАДУВАНЬ {title_suffix}</b>\n\n"
    for r in reminders_data:
        sent_emoji = "✅" if r.get('is_sent') else "⏳"
        type_emoji = "📲" if r.get('type') == 'telegram' else "📧" if r.get('type') == 'email' else "📱"
        
        message_text += f"{sent_emoji} <b>№{r.get('number')}</b>\n"
        message_text += f"📋 {r.get('task_name')}\n"
        message_text += f"📅 {r.get('reminder_datetime')}\n"
        message_text += f"{type_emoji} {r.get('type')}\n"
        message_text += f"💬 {r.get('message')}\n\n"
    
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id, parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == '➕ Створити')
def add_reminder_start(message):
    user_id = message.from_user.id
    user_states[user_id] = 'add_reminder_task'
    user_data[user_id] = {}
    
    bot.send_message(
        message.chat.id,
        "🔔 Створення нагадування\n\nВведіть назву завдання:",
        reply_markup=types.ReplyKeyboardRemove()
    )

@bot.message_handler(func=lambda message: message.text == '📤 Надіслати')
def send_reminder_start(message):
    user_id = message.from_user.id
    
    pending = reminders.get_pending()
    
    if not pending:
        bot.send_message(message.chat.id, "❌ Немає невідправлених нагадувань", reply_markup=reminders_keyboard())
        return
    
    message_text = "📤 <b>Невідправлені нагадування:</b>\n\n"
    for reminder in pending:
        message_text += f"№{reminder.get('number')} - {reminder.get('task_name')}\n"
    
    message_text += "\nВведіть номер нагадування для відправки:"
    
    user_states[user_id] = 'send_reminder'
    bot.send_message(message.chat.id, message_text, parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: message.text == '⏰ Відкласти')
def postpone_reminder_start(message):
    user_id = message.from_user.id

    user_data[user_id] = {}
    
    pending = reminders.get_pending()
    
    if not pending:
        bot.send_message(message.chat.id, "❌ Немає нагадувань для відкладання", reply_markup=reminders_keyboard())
        return
    
    message_text = "⏰ <b>Невідправлені нагадування:</b>\n\n"
    for reminder in pending:
        message_text += f"№{reminder.get('number')} - {reminder.get('task_name')}\n"
    
    message_text += "\nВведіть номер нагадування:"
    
    user_states[user_id] = 'postpone_reminder_number'
    bot.send_message(message.chat.id, message_text, parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: message.text == '🗑 Видалити' and user_states.get(message.from_user.id) == 'reminders_menu')
def delete_reminder_start(message):
    user_id = message.from_user.id
    user_states[user_id] = 'delete_reminder'
    user_data[user_id] = {}
    
    bot.send_message(
        message.chat.id,
        "🗑 Видалення нагадування\n\nВведіть номер нагадування для видалення:",
        reply_markup=types.ReplyKeyboardRemove()
    )

def show_statistics(message):
    tasks = task_manager._TaskManager__tasks
    total = len(tasks)
    completed = len([t for t in tasks if t.get('status') == 'виконане'])
    active = len([t for t in tasks if t.get('status') in ['нове', 'в роботі']])
    percent = (completed / total * 100) if total > 0 else 0
    
    message_text = "📊 <b>ЗАГАЛЬНА СТАТИСТИКА</b>\n\n"
    message_text += f"📝 Всього завдань: <b>{total}</b>\n"
    message_text += f"✅ Виконано: <b>{completed}</b>\n"
    message_text += f"⏳ Активних: <b>{active}</b>\n"
    message_text += f"📈 Процент виконання: <b>{percent:.1f}%</b>\n\n"
    
    categories = {}
    for task in tasks:
        cat = task.get('category')
        if cat not in categories:
            categories[cat] = {'total': 0, 'completed': 0}
        categories[cat]['total'] += 1
        if task.get('status') == 'виконане':
            categories[cat]['completed'] += 1
    
    if categories:
        message_text += "<b>📂 ПО КАТЕГОРІЯХ:</b>\n\n"
        for cat, stats in categories.items():
            cat_percent = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            message_text += f"• {cat}: {stats['completed']}/{stats['total']} ({cat_percent:.1f}%)\n"
    
    bot.send_message(message.chat.id, message_text, parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == '✅ Статус' and user_states.get(message.from_user.id) == 'tasks_menu')
def quick_status_start(message):
    user_id = message.from_user.id
    user_states[user_id] = 'quick_status_name'
    user_data[user_id] = {}
    
    bot.send_message(message.chat.id, "Введіть назву завдання для зміни статусу:", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: True)
def handle_states(message):
    user_id = message.from_user.id
    state = user_states.get(user_id)
    
    if not state:
        bot.send_message(message.chat.id, "Оберіть дію з меню", reply_markup=main_keyboard())
        return

    if state == 'add_task_name':
        user_data[user_id]['name'] = message.text
        user_states[user_id] = 'add_task_priority'
        bot.send_message(message.chat.id, "Оберіть пріоритет:", reply_markup=priority_keyboard())
    
    elif state == 'add_task_priority':
        user_data[user_id]['priority'] = message.text
        user_states[user_id] = 'add_task_status'
        bot.send_message(message.chat.id, "Оберіть статус:", reply_markup=status_keyboard())
    
    elif state == 'add_task_status':
        user_data[user_id]['status'] = message.text
        user_states[user_id] = 'add_task_deadline'
        bot.send_message(message.chat.id, "Введіть дедлайн (РРРР-ММ-ДД):", reply_markup=types.ReplyKeyboardRemove())
    
    elif state == 'add_task_deadline':
        user_data[user_id]['deadline'] = message.text
        user_states[user_id] = 'add_task_description'
        bot.send_message(message.chat.id, "Введіть опис:")
    
    elif state == 'add_task_description':
        user_data[user_id]['description'] = message.text
        user_states[user_id] = 'add_task_category'
        bot.send_message(message.chat.id, "Введіть категорію:")
    
    elif state == 'add_task_category':
        user_data[user_id]['category'] = message.text
        
        task = Task(
            user_data[user_id]['name'],
            user_data[user_id]['priority'],
            user_data[user_id]['status'],
            user_data[user_id]['deadline'],
            user_data[user_id]['description'],
            user_data[user_id]['category']
        )
        
        task_manager.add(task)
        task_manager.save_to_file("dataTasks.txt")
        
        bot.send_message(message.chat.id, "✅ Завдання успішно створено!", reply_markup=tasks_keyboard())
        user_states[user_id] = None
        user_data[user_id] = {}
    
    elif state == 'search_task_field':
        if message.text == '↩️ Скасувати':
            bot.send_message(message.chat.id, "Пошук скасовано", reply_markup=tasks_keyboard())
            user_states[user_id] = None
            return
        
        field_map = {
            'назва': 'name',
            'пріоритет': 'priority',
            'статус': 'status',
            'категорія': 'category',
            'дедлайн': 'deadline'
        }
        
        user_data[user_id]['search_field'] = field_map.get(message.text)
        user_states[user_id] = 'search_task_value'
        
        if message.text == 'пріоритет':
            bot.send_message(message.chat.id, "Оберіть значення:", reply_markup=priority_keyboard())
        elif message.text == 'статус':
            bot.send_message(message.chat.id, "Оберіть значення:", reply_markup=status_keyboard())
        else:
            bot.send_message(message.chat.id, "Введіть значення для пошуку:", reply_markup=types.ReplyKeyboardRemove())
    
    elif state == 'search_task_value':
        value = message.text
        field = user_data[user_id]['search_field']
        
        tasks = task_manager._TaskManager__tasks
        found = [t for t in tasks if value.lower() in str(t.get(field)).lower()]
        
        if not found:
            bot.send_message(message.chat.id, "❌ Нічого не знайдено", reply_markup=tasks_keyboard())
        else:
            message_text = f"🔍 <b>Результати пошуку ({len(found)}):</b>\n\n"
            for i, task in enumerate(found, 1):
                status_emoji = "✅" if task.get('status') == 'виконане' else "⏳"
                
                prio = task.get('priority')
                p_emoji = "🔴" if prio == 'високий' else "🟡" if prio == 'середній' else "🟢"
                
                message_text += f"{i}. {status_emoji} <b>{task.get('name')}</b>\n"
                message_text += f"   {p_emoji} {prio} | {task.get('status')}\n"
                message_text += f"   📅 {task.get('deadline')} | 📂 {task.get('category')}\n"
                message_text += f"   📝 {task.get('description')}\n\n"
            
            bot.send_message(message.chat.id, message_text, parse_mode='HTML', reply_markup=tasks_keyboard())
        
        user_states[user_id] = None
        user_data[user_id] = {}
    
    elif state == 'delete_task':
        name = message.text
        task = task_manager.get(name)
        
        if task:
            task_manager.delete(name)
            task_manager.save_to_file("dataTasks.txt")
            bot.send_message(message.chat.id, f"✅ Завдання '{name}' видалено!", reply_markup=tasks_keyboard())
        else:
            bot.send_message(message.chat.id, f"❌ Завдання '{name}' не знайдено", reply_markup=tasks_keyboard())
        
        user_states[user_id] = None
    
    elif state == 'add_reminder_task':
        user_data[user_id]['reminder_task'] = message.text
        user_states[user_id] = 'add_reminder_datetime'
        bot.send_message(message.chat.id, "Введіть дату і час (РРРР-ММ-ДД ГГ:ХХ):")
    
    elif state == 'add_reminder_datetime':
        try:
            datetime.strptime(message.text, "%Y-%m-%d %H:%M")
            user_data[user_id]['reminder_datetime'] = message.text
            user_states[user_id] = 'add_reminder_type'
            bot.send_message(message.chat.id, "Оберіть тип:", reply_markup=type_keyboard())
        except ValueError:
            bot.send_message(message.chat.id, "❌ Невірний формат! Спробуйте ще раз (РРРР-ММ-ДД ГГ:ХХ):")
    
    elif state == 'add_reminder_type':
        user_data[user_id]['reminder_type'] = message.text
        user_states[user_id] = 'add_reminder_message'
        bot.send_message(message.chat.id, "Введіть повідомлення:", reply_markup=types.ReplyKeyboardRemove())
    
    elif state == 'add_reminder_message':
        user_data[user_id]['reminder_message'] = message.text
        
        reminder = reminders.create(
            user_data[user_id]['reminder_task'],
            user_data[user_id]['reminder_datetime'],
            user_data[user_id]['reminder_type'],
            user_data[user_id]['reminder_message']
        )

        if reminder is None:
            reminder = reminders._Reminders__reminders[-1]

        if user_data[user_id]['reminder_type'] == 'telegram':
            reminder.edit('chat_id', message.chat.id)

        reminders.save_to_file("dataReminders.txt")
        
        bot.send_message(message.chat.id, "✅ Нагадування успішно створено!", reply_markup=reminders_keyboard())
        user_states[user_id] = None
        user_data[user_id] = {}
    
    elif state == 'send_reminder':
        try:
            number = int(message.text)
            reminder = reminders.get_by_number(number)
            
            if reminder:
                if reminder.get('is_sent'):
                    bot.send_message(message.chat.id, "❌ Це нагадування вже надіслано!", reply_markup=reminders_keyboard())
                else:
                    if reminder.get('type') == 'telegram':
                        target_chat_id = reminder.get('chat_id')
                        if not target_chat_id:
                            target_chat_id = message.chat.id
                        
                        msg_text = f"🔔 <b>НАГАДУВАННЯ (Надіслано вручну)</b>\n\n"
                        msg_text += f"📋 Завдання: <b>{reminder.get('task_name')}</b>\n"
                        msg_text += f"📅 Час: {reminder.get('reminder_datetime')}\n"
                        msg_text += f"💬 Повідомлення: {reminder.get('message')}"
                        
                        try:
                            bot.send_message(target_chat_id, msg_text, parse_mode='HTML')
                        except Exception as e:
                            bot.send_message(message.chat.id, f"⚠️ Помилка відправки: {e}")

                    reminder.mark_as_sent()
                    reminders.save_to_file("dataReminders.txt")
                    bot.send_message(message.chat.id, f"✅ Нагадування №{number} позначено як відправлене!", reply_markup=reminders_keyboard())
            else:
                bot.send_message(message.chat.id, f"❌ Нагадування №{number} не знайдено", reply_markup=reminders_keyboard())
        except ValueError:
            bot.send_message(message.chat.id, "❌ Введіть коректний номер (цифру)", reply_markup=reminders_keyboard())
        
        user_states[user_id] = None
    
    elif state == 'postpone_reminder_number':
        try:
            number = int(message.text)
            reminder = reminders.get_by_number(number)
            
            if reminder and not reminder.get('is_sent'):
                user_data[user_id]['postpone_number'] = number
                user_states[user_id] = 'postpone_reminder_minutes'
                bot.send_message(message.chat.id, "На скільки хвилин відкласти?")
            else:
                bot.send_message(message.chat.id, "❌ Нагадування не знайдено або вже відправлено", reply_markup=reminders_keyboard())
                user_states[user_id] = None
        except:
            bot.send_message(message.chat.id, "❌ Введіть коректний номер", reply_markup=reminders_keyboard())
            user_states[user_id] = None
    
    elif state == 'postpone_reminder_minutes':
        try:
            minutes = int(message.text)
            number = user_data[user_id]['postpone_number']
            
            reminder = reminders.get_by_number(number)
            if reminder.postpone(minutes):
                reminders.save_to_file("dataReminders.txt")
                bot.send_message(message.chat.id, f"✅ Нагадування відкладено на {minutes} хв", reply_markup=reminders_keyboard())
            else:
                bot.send_message(message.chat.id, "❌ Помилка відкладання", reply_markup=reminders_keyboard())
        except:
            bot.send_message(message.chat.id, "❌ Введіть коректну кількість хвилин", reply_markup=reminders_keyboard())
        
        user_states[user_id] = None
        user_data[user_id] = {}
    
    elif state == 'delete_reminder':
        try:
            number = int(message.text)
            reminders.delete(number)
            reminders.save_to_file("dataReminders.txt")
            bot.send_message(message.chat.id, f"✅ Нагадування №{number} видалено!", reply_markup=reminders_keyboard())
        except:
            bot.send_message(message.chat.id, "❌ Помилка видалення", reply_markup=reminders_keyboard())
            user_states[user_id] = None

    elif state == 'edit_task_name':
        name = message.text
        task = task_manager.get(name)
        if task:
            user_data[user_id]['edit_task_name'] = name
            user_states[user_id] = 'edit_task_field'
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.row('назва', 'пріоритет', 'статус')
            markup.row('дедлайн', 'опис', 'категорія')
            markup.row('↩️ Скасувати')
            
            bot.send_message(message.chat.id, f"Що змінити в завданні '{name}'?", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "❌ Завдання не знайдено", reply_markup=tasks_keyboard())
            user_states[user_id] = 'tasks_menu'

    elif state == 'edit_task_field':
        if message.text == '↩️ Скасувати':
            user_states[user_id] = 'tasks_menu'
            bot.send_message(message.chat.id, "Редагування скасовано", reply_markup=tasks_keyboard())
            return

        field_map = {
            'назва': 'name', 'пріоритет': 'priority', 'статус': 'status',
            'дедлайн': 'deadline', 'опис': 'description', 'категорія': 'category'
        }
        
        field = field_map.get(message.text)
        if field:
            user_data[user_id]['edit_field'] = field
            user_states[user_id] = 'edit_task_value'
            
            if field == 'priority':
                bot.send_message(message.chat.id, "Оберіть новий пріоритет:", reply_markup=priority_keyboard())
            elif field == 'status':
                bot.send_message(message.chat.id, "Оберіть новий статус:", reply_markup=status_keyboard())
            else:
                bot.send_message(message.chat.id, f"Введіть нове значення для '{message.text}':", reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.send_message(message.chat.id, "❌ Невірне поле. Оберіть з клавіатури.")

    elif state == 'edit_task_value':
        new_value = message.text
        task_name = user_data[user_id]['edit_task_name']
        field = user_data[user_id]['edit_field']
        
        task = task_manager.get(task_name)
        if task:
            task.edit(field, new_value)
            task_manager.save_to_file("dataTasks.txt")
            bot.send_message(message.chat.id, "✅ Завдання оновлено!", reply_markup=tasks_keyboard())
        else:
            bot.send_message(message.chat.id, "❌ Помилка при збереженні", reply_markup=tasks_keyboard())
        
        user_states[user_id] = 'tasks_menu'

    elif state == 'edit_reminder_number':
        try:
            number = int(message.text)
            reminder = reminders.get_by_number(number)
            if reminder:
                user_data[user_id]['edit_reminder_num'] = number
                user_states[user_id] = 'edit_reminder_field'
                
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                markup.row('дата', 'повідомлення', 'тип')
                markup.row('↩️ Скасувати')
                
                bot.send_message(message.chat.id, f"Що змінити в нагадуванні №{number}?", reply_markup=markup)
            else:
                bot.send_message(message.chat.id, "❌ Нагадування не знайдено", reply_markup=reminders_keyboard())
                user_states[user_id] = 'reminders_menu'
        except ValueError:
            bot.send_message(message.chat.id, "❌ Введіть число!")

    elif state == 'edit_reminder_field':
        if message.text == '↩️ Скасувати':
            user_states[user_id] = 'reminders_menu'
            bot.send_message(message.chat.id, "Редагування скасовано", reply_markup=reminders_keyboard())
            return

        field_map = {
            'дата': 'reminder_datetime', 
            'повідомлення': 'message', 
            'тип': 'type'
        }
        
        field = field_map.get(message.text)
        if field:
            user_data[user_id]['edit_field'] = field
            user_states[user_id] = 'edit_reminder_value'
            
            if field == 'type':
                bot.send_message(message.chat.id, "Оберіть новий тип:", reply_markup=type_keyboard())
            elif field == 'reminder_datetime':
                bot.send_message(message.chat.id, "Введіть нову дату (РРРР-ММ-ДД ГГ:ХХ):")
            else:
                bot.send_message(message.chat.id, "Введіть нове повідомлення:")
        else:
             bot.send_message(message.chat.id, "❌ Невірне поле.")

    elif state == 'edit_reminder_value':
        new_value = message.text
        number = user_data[user_id]['edit_reminder_num']
        field = user_data[user_id]['edit_field']

        if field == 'reminder_datetime':
            try:
                datetime.strptime(new_value, "%Y-%m-%d %H:%M")
            except ValueError:
                bot.send_message(message.chat.id, "❌ Невірний формат дати! Спробуйте ще раз:")
                return

        reminder = reminders.get_by_number(number)
        if reminder:
            reminder.edit(field, new_value)
            
            if field == 'reminder_datetime':
                reminder.edit('is_sent', False)
                
            if field == 'type' and new_value == 'telegram':
                reminder.edit('chat_id', message.chat.id)

            reminders.save_to_file("dataReminders.txt")
            bot.send_message(message.chat.id, "✅ Нагадування оновлено!", reply_markup=reminders_keyboard())

            user_states[user_id] = 'reminders_menu'
    
    elif state == 'quick_status_name':
        name = message.text
        task = task_manager.get(name)
        
        if task:
            user_data[user_id]['status_task_name'] = name
            user_states[user_id] = 'quick_status_select'
            
            bot.send_message(message.chat.id, f"Оберіть новий статус для '{name}':", reply_markup=status_keyboard())
        else:
            bot.send_message(message.chat.id, "❌ Завдання не знайдено", reply_markup=tasks_keyboard())
            user_states[user_id] = 'tasks_menu'

    elif state == 'quick_status_select':
        new_status = message.text
        name = user_data[user_id]['status_task_name']
        
        task = task_manager.get(name)
        if task:
            task.edit('status', new_status)
            task_manager.save_to_file("dataTasks.txt")
            bot.send_message(message.chat.id, f"✅ Статус завдання '{name}' змінено на '{new_status}'!", reply_markup=tasks_keyboard())
        else:
            bot.send_message(message.chat.id, "❌ Помилка: завдання не знайдено", reply_markup=tasks_keyboard())
            
        user_states[user_id] = 'tasks_menu'

    elif state == 'search_reminder_field':
        if message.text == '↩️ Скасувати':
            bot.send_message(message.chat.id, "Пошук скасовано", reply_markup=reminders_keyboard())
            user_states[user_id] = 'reminders_menu'
            return
        
        field_map = {
            'номер' : 'number',
            'завдання': 'task_name',
            'дата': 'reminder_datetime',
            'тип': 'type',
            'повідомлення': 'message'
        }
        
        field = field_map.get(message.text)
        if field:
            user_data[user_id]['search_field'] = field
            user_states[user_id] = 'search_reminder_value'
            
            if message.text == 'тип':
                bot.send_message(message.chat.id, "Оберіть тип:", reply_markup=type_keyboard())
            else:
                bot.send_message(message.chat.id, f"Введіть значення для пошуку по полю '{message.text}':", reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.send_message(message.chat.id, "❌ Невірний критерій. Оберіть з меню.")

    elif state == 'search_reminder_value':
        value = message.text
        field = user_data[user_id]['search_field']

        all_reminders = reminders._Reminders__reminders

        if field == 'number':
            found = [r for r in all_reminders if str(r.get(field)) == value]
        else:
            found = [r for r in all_reminders if value.lower() in str(r.get(field)).lower()]
        
        if not found:
            bot.send_message(message.chat.id, "❌ Нічого не знайдено", reply_markup=reminders_keyboard())
        else:
            message_text = f"🔍 <b>Результати пошуку ({len(found)}):</b>\n\n"
            for r in found:
                sent_emoji = "✅" if r.get('is_sent') else "⏳"
                type_emoji = "📲" if r.get('type') == 'telegram' else "📧" if r.get('type') == 'email' else "📱"
                
                message_text += f"{sent_emoji} <b>№{r.get('number')}</b>\n"
                message_text += f"📋 {r.get('task_name')}\n"
                message_text += f"📅 {r.get('reminder_datetime')}\n"
                message_text += f"{type_emoji} {r.get('type')}\n"
                message_text += f"💬 {r.get('message')}\n\n"
            
            bot.send_message(message.chat.id, message_text, parse_mode='HTML', reply_markup=reminders_keyboard())
        
        user_states[user_id] = 'reminders_menu'
        user_data[user_id] = {}

def check_reminders_background():
    while True:
        try:
            current_time = datetime.now()
            reminders_data = reminders._Reminders__reminders
            
            for reminder in reminders_data[:]:
                if (reminder.check_time() and not reminder.get('is_sent') and reminder.get('type') == 'telegram'):
                    chat_id = reminder.get('chat_id')
                    
                    if chat_id:
                        message_text = f"🔔 <b>НАГАДУВАННЯ!</b>\n\n"
                        message_text += f"📋 Завдання: <b>{reminder.get('task_name')}</b>\n"
                        message_text += f"💬 {reminder.get('message')}\n"
                        message_text += f"📅 {reminder.get('reminder_datetime')}"
                        
                        bot.send_message(chat_id, message_text, parse_mode='HTML')
                        reminder.mark_as_sent()
                        reminders.save_to_file("dataReminders.txt")
            
            time.sleep(60)
        except Exception as e:
            print(f"Помилка в фоновій перевірці: {e}")
            time.sleep(60)

task_manager.read_from_file("dataTasks.txt")
reminders.read_from_file("dataReminders.txt")
reminder_thread = threading.Thread(target=check_reminders_background, daemon=True)
reminder_thread.start()
print("Бот запущено!")
bot.polling(non_stop=True)