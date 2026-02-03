import telebot
from telebot import types
import os
import datetime
import json
import time

# ========== НАСТРОЙКИ ==========
TOKEN = os.environ.get('TOKEN')
ADMIN_ID = 1615054558  # Ваш Telegram ID
bot = telebot.TeleBot(TOKEN)

# ========== ХРАНЕНИЕ ДАННЫХ ПОЛЬЗОВАТЕЛЕЙ ==========
# Простое хранилище в памяти (для продакшена лучше использовать базу данных)
user_data_storage = {}

def save_user_data(user_id, user_info):
    """Сохраняет данные пользователя"""
    user_data_storage[user_id] = {
        'first_name': user_info.get('first_name', ''),
        'last_name': user_info.get('last_name', ''),
        'username': user_info.get('username', ''),
        'phone': user_info.get('phone', ''),
        'last_activity': datetime.datetime.now().isoformat()
    }
    # Для отладки: сохраняем в файл
    try:
        with open('users_data.json', 'w', encoding='utf-8') as f:
            json.dump(user_data_storage, f, ensure_ascii=False, indent=2)
    except:
        pass

def get_user_data(user_id):
    """Получает данные пользователя"""
    return user_data_storage.get(user_id, {})

# ========== БАЗА ДАННЫХ УСЛУГ ==========
services = {
    "registration": {
        "name": "📋 Регистрация бизнеса",
        "options": {
            "reg_llc": "• ООО: 15 000 ₽ (7 дней)",
            "reg_ao": "• АО: 25 000 ₽ (10 дней)",
            "reg_ip": "• ИП: 5 000 ₽ (3 дня)",
            "reg_nko": "• НКО: 20 000 ₽ (14 дней)"
        }
    },
    "addresses": {
        "name": "🏢 Юридические адреса",
        "options": {
            "addr_moscow": "• Москва: от 15 000 ₽/год",
            "addr_spb": "• Санкт-Петербург: от 10 000 ₽/год",
            "addr_russia": "• Другие регионы: от 7 000 ₽/год"
        }
    },
    "corporate": {
        "name": "🔄 Корпоративные изменения",
        "options": {
            "branch": "• Обособленные подразделения/филиалы",
            "migration": "• Миграция компаний в Москву",
            "liquidation": "• Ликвидация юридических лиц"
        }
    }
}

service_details = {
    "reg_llc": "<b>Регистрация ООО</b>\n\nВключено:\n✓ Проверка названия\n✓ Подготовка документов\n✓ Открытие расчетного счета\n✓ Государственная пошлина\n\nСрок: 7 рабочих дней\nЦена: 15 000 ₽",
    "reg_ao": "<b>Регистрация АО</b>\n\nВключено:\n✓ Полный юридический сопровождение\n✓ Подготовка устава\n✓ Регистрация в ЦБ РФ\n✓ Консультация по акциям\n\nСрок: 10 рабочих дней\nЦена: 25 000 ₽",
    "reg_ip": "<b>Регистрация ИП</b>\n\nВключено:\n✓ Проверка видов деятельности\n✓ Заполнение заявления\n✓ Оплата госпошлины\n✓ Подача документов\n\nСрок: 3 рабочих дня\nЦена: 5 000 ₽",
    "migration": "<b>Миграция компании в Москву</b>\n\nПроцесс:\n1. Внесение изменений в ЕГРЮЛ\n2. Смена юридического адреса\n3. Уведомление фондов\n4. Постановка на учет в ИФНС\n\nСрок: от 30 дней\nЦена: от 45 000 ₽",
    "liquidation": "<b>Ликвидация юридического лица</b>\n\nЭтапы:\n1. Принятие решения о ликвидации\n2. Уведомление ИФНС\n3. Публикация в Вестнике госрегистрации\n4. Расчет с кредиторами\n5. Закрытие счетов\n6. Снятие с учета\n\nСрок: от 4 месяцев\nЦена: от 60 000 ₽"
}

# ========== УЛУЧШЕННАЯ ФУНКЦИЯ УВЕДОМЛЕНИЙ ==========
def notify_admin(user_id, action="начал общение", service="", with_contact_button=True):
    """Отправляет уведомление администратору с кнопкой для связи"""
    try:
        # Получаем данные пользователя
        user_data = get_user_data(user_id)
        
        # Если данных нет, используем базовую информацию
        first_name = user_data.get('first_name', 'Неизвестно')
        last_name = user_data.get('last_name', '')
        username = user_data.get('username', '')
        
        time_now = datetime.datetime.now().strftime('%H:%M %d.%m.%Y')
        
        # Формируем сообщение
        message = (
            f"🔔 <b>НОВЫЙ КЛИЕНТ В БОТЕ</b>\n"
            f"▫️ <b>Действие:</b> {action}\n"
            f"▫️ <b>Имя:</b> {first_name}\n"
        )
        
        if last_name:
            message += f"▫️ <b>Фамилия:</b> {last_name}\n"
        if username:
            message += f"▫️ <b>Логин:</b> @{username}\n"
        
        message += f"▫️ <b>ID:</b> <code>{user_id}</code>\n"
        
        if service:
            message += f"▫️ <b>Услуга:</b> {service}\n"
        
        message += f"▫️ <b>Время:</b> {time_now}\n\n"
        
        # Добавляем подсказку для связи
        if username:
            message += f"<i>Чтобы ответить, нажмите на кнопку ниже или напишите @{username}</i>"
        else:
            message += f"<i>Чтобы ответить, используйте ID: {user_id}</i>"
        
        # Создаем клавиатуру с кнопкой для связи
        keyboard = types.InlineKeyboardMarkup()
        
        # Если у пользователя есть username, создаем кнопку с ссылкой
        if username and with_contact_button:
            keyboard.add(
                types.InlineKeyboardButton(
                    "💬 Написать пользователю",
                    url=f"https://t.me/{username}"
                )
            )
        
        keyboard.add(
            types.InlineKeyboardButton(
                "✅ Обработано",
                callback_data=f"processed_{user_id}"
            )
        )
        
        bot.send_message(
            ADMIN_ID,
            message,
            parse_mode='HTML',
            reply_markup=keyboard
        )
        
        print(f"✅ Уведомление отправлено администратору о пользователе {user_id}")
        
    except Exception as e:
        print(f"❌ Ошибка отправки уведомления: {e}")

# ========== ФУНКЦИИ КЛАВИАТУР ==========
def main_menu():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    buttons = []
    for key, service in services.items():
        buttons.append(types.InlineKeyboardButton(
            service["name"],
            callback_data=f"cat_{key}"
        ))
    
    for i in range(0, len(buttons), 2):
        if i+1 < len(buttons):
            keyboard.add(buttons[i], buttons[i+1])
        else:
            keyboard.add(buttons[i])
    
    keyboard.row(
        types.InlineKeyboardButton("🌐 Наш сайт", url="https://yandex-legal-pros.lovable.app/"),
        types.InlineKeyboardButton("📞 Связаться", callback_data="contact_manager")
    )
    
    return keyboard

def category_menu(category_key):
    keyboard = types.InlineKeyboardMarkup()
    service = services[category_key]
    
    for key, option in service["options"].items():
        keyboard.add(types.InlineKeyboardButton(
            option,
            callback_data=f"serv_{key}"
        ))
    
    keyboard.row(
        types.InlineKeyboardButton("◀️ Назад", callback_data="main_menu"),
        types.InlineKeyboardButton("💬 Консультация", callback_data=f"consult_{category_key}")
    )
    
    return keyboard

def service_menu(service_key):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        types.InlineKeyboardButton(
            "📄 Подробнее на сайте",
            url=f"https://yandex-legal-pros.lovable.app//service/{service_key}"
        ),
        types.InlineKeyboardButton(
            "💬 Обсудить с менеджером",
            callback_data=f"contact_{service_key}"
        )
    )
    
    keyboard.add(
        types.InlineKeyboardButton(
            "◀️ К категории",
            callback_data=f"cat_{service_key.split('_')[0]}"
        ),
        types.InlineKeyboardButton(
            "🏠 В главное меню",
            callback_data="main_menu"
        )
    )
    
    return keyboard

# ========== ОБРАБОТЧИКИ КОМАНД ==========
@bot.message_handler(commands=['start'])
def start_command(message):
    """Обработчик команды /start"""
    user = message.from_user
    
    # Сохраняем данные пользователя
    user_info = {
        'id': user.id,
        'first_name': user.first_name or '',
        'last_name': user.last_name or '',
        'username': user.username or ''
    }
    
    save_user_data(user.id, user_info)
    
    # Отправляем уведомление администратору
    notify_admin(user.id, "запустил бота командой /start")
    
    # Приветствуем пользователя
    welcome_text = (
        "<b>Добро пожаловать в юридическую консультацию!</b>\n\n"
        "Я помогу вам выбрать нужную услугу:\n"
        "• Регистрация ООО, АО, ИП, НКО\n"
        "• Юридические адреса по всей России\n"
        "• Миграция и ликвидация компаний\n\n"
        "<i>Выберите категорию:</i>"
    )
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode='HTML',
        reply_markup=main_menu()
    )

# ========== ОБРАБОТЧИК ЗАПРОСА КОНТАКТА ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith('contact_'))
def handle_contact_request(call):
    """Обработчик нажатия на кнопку 'Связаться с менеджером'"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user = call.from_user
    
    # Определяем услугу
    service_key = call.data[8:] if call.data != "contact_manager" else ""
    service_name = "общая консультация"
    
    if service_key:
        # Ищем название услуги
        for category in services.values():
            if service_key in category["options"]:
                service_name = category["options"][service_key]
                break
    
    # Сохраняем/обновляем данные пользователя
    user_info = {
        'id': user.id,
        'first_name': user.first_name or '',
        'last_name': user.last_name or '',
        'username': user.username or ''
    }
    
    save_user_data(user.id, user_info)
    
    # Отправляем уведомление администратору
    notify_admin(
        user.id,
        "запросил контакт с менеджером",
        service_name,
        with_contact_button=True
    )
    
    # Подтверждаем пользователю
    bot.answer_callback_query(
        call.id,
        "✅ Ваш запрос отправлен менеджеру! С вами свяжутся в ближайшее время.",
        show_alert=True
    )
    
    # Показываем контактную информацию пользователю
    contact_manager(chat_id, service_name)

# ========== ОБРАБОТЧИК ДРУГИХ CALLBACK ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_other_callbacks(call):
    """Обработчик остальных callback-запросов"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user = call.from_user
    
    bot.answer_callback_query(call.id)
    
    # Обработка кнопки "Обработано"
    if call.data.startswith('processed_'):
        user_id = call.data[10:]
        bot.answer_callback_query(
            call.id,
            f"✅ Заявка от пользователя {user_id} отмечена как обработанная",
            show_alert=False
        )
        return
    
    # Главное меню
    elif call.data == "main_menu":
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="<b>Выберите категорию услуги:</b>",
            parse_mode='HTML',
            reply_markup=main_menu()
        )
    
    # Категории
    elif call.data.startswith("cat_"):
        category_key = call.data[4:]
        
        if category_key in services:
            category = services[category_key]
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"<b>{category['name']}</b>\n\n<i>Выберите конкретную услугу:</i>",
                parse_mode='HTML',
                reply_markup=category_menu(category_key)
            )
    
    # Услуги
    elif call.data.startswith("serv_"):
        service_key = call.data[5:]
        
        if service_key in service_details:
            text = service_details[service_key]
        else:
            text = f"<b>Услуга выбрана</b>\n\n<i>Хотите узнать подробности на сайте или обсудить с менеджером?</i>"
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text + "\n\n👇 <b>Выберите действие:</b>",
            parse_mode='HTML',
            reply_markup=service_menu(service_key)
        )
    
    # Консультация по категории
    elif call.data.startswith("consult_"):
        category_key = call.data[8:]
        if category_key in services:
            service_name = f"консультация по категории: {services[category_key]['name']}"
            
            # Сохраняем данные пользователя
            user_info = {
                'id': user.id,
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'username': user.username or ''
            }
            save_user_data(user.id, user_info)
            
            # Уведомляем администратора
            notify_admin(user.id, "запросил консультацию", service_name)
            
            contact_manager(chat_id, service_name)

# ========== ФУНКЦИЯ СВЯЗИ С МЕНЕДЖЕРОМ ==========
def contact_manager(chat_id, service="общая консультация"):
    """Отправляет контакты менеджера пользователю"""
    manager_text = (
        f"<b>📞 Связь с менеджером</b>\n\n"
        f"<i>Услуга:</i> {service}\n\n"
        "✅ <b>Ваш запрос отправлен менеджеру!</b>\n\n"
        "С вами свяжутся в ближайшее время:\n\n"
        "1. <b>Telegram:</b> @DelovyeResheniya\n"
        "2. <b>Телефон:</b> +7 (985) 057-64-65\n"
        "3. <b>Email:</b> delovye-resheniya@mail.ru\n\n"
        "🕐 <i>Рабочее время: Пн-Пт с 9:00 до 18:00</i>\n\n"
        "<i>Укажите, что обратились через бота для получения приоритетного обслуживания.</i>"
    )
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu"))
    
    bot.send_message(
        chat_id,
        manager_text,
        parse_mode='HTML',
        reply_markup=keyboard
    )

# ========== ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ ==========
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    """Обработчик текстовых сообщений"""
    user = message.from_user
    
    # Сохраняем данные пользователя
    user_info = {
        'id': user.id,
        'first_name': user.first_name or '',
        'last_name': user.last_name or '',
        'username': user.username or ''
    }
    save_user_data(user.id, user_info)
    
    # Уведомляем администратора о сообщении
    notify_admin(
        user.id,
        f"написал сообщение: {message.text[:50]}...",
        with_contact_button=True
    )
    
    bot.send_message(
        message.chat.id,
        "Используйте кнопки меню для навигации ☝️\n"
        "Или нажмите /start для открытия главного меню.",
        reply_markup=types.ReplyKeyboardRemove()
    )

# ========== ЗАПУСК БОТА ==========
if __name__ == "__main__":
    print("=" * 50)
    print("🔄 Удаляем старые подключения...")
    
    # Удаляем вебхуки и ждем
    try:
        bot.remove_webhook()
        time.sleep(3)
    except:
        pass
    
    print("✅ Бот запущен и работает на Railway!")
    print(f"👨‍💼 Уведомления будут отправляться ID: {ADMIN_ID}")
    print("=" * 50)
    
    # Запускаем опрос
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("Перезапуск через 10 секунд...")
        time.sleep(10)
