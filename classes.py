from datetime import datetime, timedelta
import os

class Task():
    def __init__(self, name, priority, status, deadline, description, category):
        self.__name = name
        self.__priority = priority
        self.__status = status
        self.__deadline = deadline
        self.__description = description
        self.__category = category

    def get(self, key):
        if key == "name":
            value = self.__name
        elif key == "priority":
            value = self.__priority
        elif key == "status":
            value = self.__status
        elif key == "deadline":
            value = self.__deadline
        elif key == "description":
            value = self.__description
        elif key == "category":
            value = self.__category
        else:
            value = None
            print("Задано не існуюче поле")
        return value

    def edit(self, key, value):
        if key == "name":
            self.__name = value
        elif key == "priority":
            self.__priority = value
        elif key == "status":
            self.__status = value
        elif key == "deadline":
            self.__deadline = value
        elif key == "description":
            self.__description = value
        elif key == "category":
            self.__category = value

    def print(self):
        print("{0:30} | {1:10} | {2:12} | {3:15} | {4:20} | {5}".format(
                self.__name,
                self.__priority,
                self.__status,
                self.__deadline,
                self.__category,
                self.__description
            )
        )

    def join(self):
        return f"{self.__name} | {self.__priority} | {self.__status} | {self.__deadline} | {self.__description} | {self.__category}"

    def set(self, text_row):
        try:
            data = text_row.strip().split(" | ")
            self.__name = data[0]
            self.__priority = data[1]
            self.__status = data[2]
            self.__deadline = data[3]
            self.__description = data[4]
            self.__category = data[5]
            return self
        except Exception as e:
            print(f"Конвертація не відбулась: {e}")
            return None

class TaskManager():
    def __init__(self):
        self.__tasks = []

    def add(self, task):
        self.__tasks.append(task)
        print(f"Завдання '{task.get('name')}' додано успішно!")

    def get(self, name):
        for task in self.__tasks:
            if task.get("name") == name:
                return task
        return None

    def delete(self, name):
        success = False
        for i in range(len(self.__tasks)):
            if (self.__tasks[i].get("name") == name):
                self.__tasks.remove(self.__tasks[i])
                success = True
                print(f"Завдання '{name}' видалено успішно!")
                break
        if not success:
            print(f"Завдання '{name}' не знайдено!")
        return success

    def change_status(self, name, new_status):
        task = self.get(name)
        if task:
            task.edit("status", new_status)
            print(f"Статус завдання '{name}' змінено на '{new_status}'")
        else:
            print(f"Завдання '{name}' не знайдено!")

    def __print_head(self):
        print("=" * 160)
        print("{0:30} | {1:10} | {2:12} | {3:15} | {4:20} | {5}".format(
                "Назва",
                "Пріоритет",
                "Статус",
                "Дедлайн",
                "Категорія",
                "Опис"
            )
        )
        print("=" * 160)

    def print(self, filter="all", sort=None):
        self.__print_head()

        filtered_tasks = []

        if filter == "all":
            filtered_tasks = self.__tasks

        elif filter == "active":
            filtered_tasks = [t for t in self.__tasks if t.get('status') in ['нове', 'в роботі']]

        elif filter == "completed":
            filtered_tasks = [t for t in self.__tasks if t.get('status') == 'виконане']
        
        elif filter == "overdue":
            filtered_tasks = self.get_overdue_tasks()
        
        elif filter == "urgent":
            filtered_tasks = [t for t in self.__tasks  if t.get('priority') == 'високий' and t.get('status') != 'виконане']

        if sort == "priority":
            priority_order = {'високий': 1, 'середній': 2, 'низький': 3}
            filtered_tasks = sorted(filtered_tasks, key=lambda t: priority_order.get(t.get('priority'), 4))
        
        elif sort == "deadline":
            filtered_tasks = sorted(filtered_tasks, key=lambda t: t.get('deadline'))

        for task in filtered_tasks:
            task.print()
        
        print("=" * 160)

    def find(self, key, value):
        self.__print_head()
        found = False
        for task in self.__tasks:
            if key == "name":
                if value.lower() in task.get(key).lower():
                    task.print()
                    found = True
            else:
                if task.get(key) == value:
                    task.print()
                    found = True
        
        if not found:
            print(f"Завдання з {key} = '{value}' не знайдено")
        print("=" * 160)

    def get_statistics(self):
        total = len(self.__tasks)
        completed = len([t for t in self.__tasks if t.get('status') == 'виконане'])
        active = len([t for t in self.__tasks if t.get('status') in ['нове', 'в роботі']])
        
        print(f"Всього завдань: {total}")
        print(f"Виконано: {completed}")
        print(f"Активних: {active}")
        print(f"Процент виконання: {completed/total*100:.1f}%" if total > 0 else "0%")

    def get_overdue_tasks(self):
        today = datetime.now().strftime("%Y-%m-%d")
        
        overdue = [t for t in self.__tasks 
                if t.get('deadline') < today and t.get('status') != 'виконане']
        return overdue
    
    def get_categories_statistics(self):
        categories = {}
        for task in self.__tasks:
            cat = task.get('category')
            if cat not in categories:
                categories[cat] = {'total': 0, 'completed': 0}
            categories[cat]['total'] += 1
            if task.get('status') == 'виконане':
                categories[cat]['completed'] += 1
        
        print("="*50)
        print("СТАТИСТИКА ПО КАТЕГОРІЯХ".center(50))
        print("="*50 + "\n")
        
        for cat, stats in categories.items():
            percent = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"{cat}: {stats['completed']}/{stats['total']} ({percent:.1f}%)")
    
    def get_all_categories(self):
        return list(set(t.get('category') for t in self.__tasks))

    def read_from_file(self, fileName):
        if not os.path.exists(fileName):
            print(f"Файл {fileName} не знайдено")
            return
        print("Зчитування файлу розпочато")
        if (len(self.__tasks) > 0):
            print("Менеджер завдань уже заповнений")
            return
        file_reader = open(fileName, mode = 'r', encoding='utf-8')
        data_list = file_reader.read().strip().split('\n')

        for row in data_list:
            if row.strip():
                task = Task("", "", "", "", "", "")
                task_obj = task.set(row)
                if task_obj is not None:
                    self.__tasks.append(task_obj)
                else:
                    print(f"Пропущено некоректний рядок: {row}")
        file_reader.close()
        print(f"Завантажено {len(self.__tasks)} завдань")

    def save_to_file(self, fileName):
        file_writer = open(fileName, mode = 'w', encoding='utf-8')
        for task in self.__tasks:
            file_writer.write(task.join() + '\n')
        file_writer.close()

class Reminder():
    def __init__(self, number, task_name, reminder_datetime, type, message, is_sent, chat_id=None):
        self.__number = number
        self.__task_name = task_name
        self.__reminder_datetime = reminder_datetime
        self.__type = type
        self.__message = message
        self.__is_sent = is_sent
        self.__chat_id = chat_id

    def get(self, key):
        if key == "number":
            value = self.__number
        elif key == "task_name":
            value = self.__task_name
        elif key == "reminder_datetime":
            value = self.__reminder_datetime
        elif key == "type":
            value = self.__type
        elif key == "message":
            value = self.__message
        elif key == "is_sent":
            value = self.__is_sent
        elif key == 'chat_id':
            value = self.__chat_id
        else:
            value = None
            print("Задано не існуюче поле")
        return value

    def edit(self, key, value):
        if key == "number":
            self.__number = value
        elif key == "task_name":
            self.__task_name = value
        elif key == "reminder_datetime":
            self.__reminder_datetime = value
        elif key == "type":
            self.__type = value
        elif key == "message":
            self.__message = value
        elif key == "is_sent":
            self.__is_sent = value
        elif key == "chat_id":
            self.__chat_id = value

    def mark_as_sent(self):
        self.__is_sent = True

    def check_time(self):
        try:
            reminder_time = datetime.strptime(self.__reminder_datetime, "%Y-%m-%d %H:%M")
            current_time = datetime.now()
            if current_time >= reminder_time and not self.__is_sent:
                return True
            return False
        except:
            print("Помилка перевірки часу нагадування")
            return False

    def print(self):
        print("{0:10} | {1:30} | {2:20} | {3:15} | {4:11} | {5}".format(
                str(self.__number),
                self.__task_name,
                self.__reminder_datetime,
                self.__type,
                "Так" if self.__is_sent else "Ні",
                self.__message
            )
        )

    def join(self):
        return f"{self.__number} | {self.__task_name} | {self.__reminder_datetime} | {self.__type} | {self.__message} | {self.__is_sent} | {self.__chat_id}"

    def set(self, text_row):
        try:
            data = text_row.strip().split(" | ")
            self.__number = int(data[0])
            self.__task_name = data[1]
            self.__reminder_datetime = data[2]
            self.__type = data[3]
            self.__message = data[4]
            self.__is_sent = data[5] == "True"
            if len(data) > 6:
                chat_id_str = data[6].strip()
                if chat_id_str == 'None' or chat_id_str == '':
                    self.__chat_id = None
                else:
                    self.__chat_id = int(data[6])
            else:
                self.__chat_id = None
            return self
        except Exception as e:
            print(f"Конвертація не відбулась: {e}")
            return None
        
    def postpone(self, minutes):
        try:
            current_time = datetime.strptime(self.__reminder_datetime, "%Y-%m-%d %H:%M")
            new_time = current_time + timedelta(minutes=minutes)
            self.__reminder_datetime = new_time.strftime("%Y-%m-%d %H:%M")
            self.__is_sent = False
            return True
        except Exception as e:
            print(f"Помилка відкладання: {e}")
            return False

class Reminders():
    def __init__(self):
        self.__reminders = []
        self.__next_number = 1

    def create(self, task_name, reminder_datetime, type, message):
        reminder = Reminder(self.__next_number, task_name, reminder_datetime, type, message, False)
        self.__reminders.append(reminder)
        print(f"Нагадування №{self.__next_number} для завдання '{task_name}' створено!")
        self.__next_number += 1

    def delete(self, reminder_number):
        success = False
        for i in range(len(self.__reminders)):
            if (self.__reminders[i].get("number") == reminder_number):
                self.__reminders.remove(self.__reminders[i])
                success = True
                print(f"Нагадування №{reminder_number} видалено успішно!")
                break
        if not success:
            print(f"Нагадування №{reminder_number} не знайдено!")
        return success

    def get_pending(self):
        return [reminder for reminder in self.__reminders if not reminder.get("is_sent")]

    def print(self, filter="all", sort=None):
        self.__print_head()
        
        filtered_reminders = []

        if filter == "all":
            filtered_reminders = self.__reminders
        
        elif filter == "pending":
            filtered_reminders = [r for r in self.__reminders if not r.get('is_sent')]
        
        elif filter == "sent":
            filtered_reminders = [r for r in self.__reminders if r.get('is_sent')]
        
        elif filter == "active":
            filtered_reminders = [r for r in self.__reminders if r.check_time()]
        
        if sort == "datetime":
            filtered_reminders = sorted(filtered_reminders, key=lambda r: r.get('reminder_datetime'))
        
        elif sort == "type":
            filtered_reminders = sorted(filtered_reminders, key=lambda r: r.get('type'))
        
        for reminder in filtered_reminders:
            reminder.print()
        
        print("=" * 160)

    def __print_head(self):
        print("=" * 160)
        print("{0:10} | {1:30} | {2:20} | {3:15} | {4:11} | {5}".format(
                "Номер",
                "Завдання",
                "Дата і час",
                "Тип",
                "Відправлено",
                "Повідомлення"
            )
        )
        print("=" * 160)

    def find(self, key, value):
        self.__print_head()
        found = False
        for reminder in self.__reminders:
            if key == "task_name":
                if value.lower() in reminder.get(key).lower():
                    reminder.print()
                    found = True
            else:
                if reminder.get(key) == value:
                    reminder.print()
                    found = True

        if not found:
            print(f"Нагадування з {key} = '{value}' не знайдено")
        print("=" * 160)

    def get_by_number(self, number):
        for reminder in self.__reminders:
            if reminder.get('number') == number:
                return reminder
        return None
    
    def mark_range_as_sent(self, start_num, end_num):
        count = 0
        for r in self.__reminders:
            num = r.get('number')
            if start_num <= num <= end_num and not r.get('is_sent'):
                r.mark_as_sent()
                count += 1
        return count

    def read_from_file(self, fileName):
        if not os.path.exists(fileName):
            print(f"Файл {fileName} не знайдено")
            return
        print("Зчитування файлу розпочато")
        if (len(self.__reminders) > 0):
            print("Список нагадувань уже заповнений")
            return
        file_reader = open(fileName, mode = 'r', encoding='utf-8')
        data_list = file_reader.read().strip().split('\n')
        max_number = 0

        for row in data_list:
            if row.strip():
                reminder = Reminder(0, "", "", "", "", False)
                reminder_obj = reminder.set(row)
                
                if reminder_obj is not None: 
                    self.__reminders.append(reminder_obj)
                    if reminder_obj.get("number") > max_number:
                        max_number = reminder_obj.get("number")
                else:
                    print(f"Пропущено некоректний рядок: {row}")

        self.__next_number = max_number + 1
        file_reader.close()
        print(f"Завантажено {len(self.__reminders)} нагадувань")

    def save_to_file(self, fileName):
        file_writer = open(fileName, mode = 'w', encoding='utf-8')
        for reminder in self.__reminders:
            file_writer.write(reminder.join() + '\n')
        file_writer.close()