import telebot
from telebot import types
import os
import datetime

# ========== НАСТРОЙКИ ==========
TOKEN = os.environ.get('TOKEN')  # Токен берется из Railway
ADMIN_ID = 1615054558  # Ваш Telegram ID (уведомления будут приходить сюда)
bot = telebot.TeleBot(TOKEN)

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

# Описания услуг (для кнопки "Подробнее")
service_details = {
    "reg_llc": "<b>Регистрация ООО</b>\n\nВключено:\n✓ Проверка названия\n✓ Подготовка документов\n✓ Открытие расчетного счета\n✓ Государственная пошлина\n\nСрок: 7 рабочих дней\nЦена: 15 000 ₽",
    "reg_ao": "<b>Регистрация АО</b>\n\nВключено:\n✓ Полный юридический сопровождение\n✓ Подготовка устава\n✓ Регистрация в ЦБ РФ\n✓ Консультация по акциям\n\nСрок: 10 рабочих дней\nЦена: 25 000 ₽",
    "reg_ip": "<b>Регистрация ИП</b>\n\nВключено:\n✓ Проверка видов деятельности\n✓ Заполнение заявления\n✓ Оплата госпошлины\n✓ Подача документов\n\nСрок: 3 рабочих дня\nЦена: 5 000 ₽",
    "migration": "<b>Миграция компании в Москву</b>\n\nПроцесс:\n1. Внесение изменений в ЕГРЮЛ\n2. Смена юридического адреса\n3. Уведомление фондов\n4. Постановка на учет в ИФНС\n\nСрок: от 30 дней\nЦена: от 45 000 ₽",
    "liquidation": "<b>Ликвидация юридического лица</b>\n\nЭтапы:\n1. Принятие решения о ликвидации\n2. Уведомление ИФНС\n3. Публикация в Вестнике госрегистрации\n4. Расчет с кредиторами\n5. Закрытие счетов\n6. Снятие с учета\n\nСрок: от 4 месяцев\nЦена: от 60 000 ₽"
}

# ========== ФУНКЦИЯ УВЕДОМЛЕНИЙ ==========
def notify_admin(user_info, action="начал общение", service=""):
    """Отправляет уведомление администратору"""
    try:
        time_now = datetime.datetime.now().strftime('%H:%M %d.%m.%Y')
        message = (
            f"🔔 <b>НОВЫЙ КЛИЕНТ В БОТЕ</b>\n"
            f"▫️ <b>Действие:</b> {action}\n"
            f"▫️ <b>Имя:</b> {user_info.get('first_name', 'Не указано')}\n"
            f"▫️ <b>Фамилия:</b> {user_info.get('last_name', 'Не указана')}\n"
            f"▫️ <b>Логин:</b> @{user_info.get('username', 'Нет логина')}\n"
            f"▫️ <b>ID:</b> <code>{user_info.get('id', 'Нет ID')}</code>\n"
        )
        if service:
            message += f"▫️ <b>Услуга:</b> {service}\n"
        message += f"▫️ <b>Время:</b> {time_now}"
        
        bot.send_message(ADMIN_ID, message, parse_mode='HTML')
        print(f"✅ Уведомление отправлено администратору {ADMIN_ID}")
    except Exception as e:
        print(f"❌ Ошибка отправки уведомления: {e}")

# ========== ФУНКЦИИ КЛАВИАТУР ==========
def main_menu():
    """Главное меню с категориями"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # Кнопки категорий (распределяем по 2 в ряд)
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
    
    # Кнопки в самом низу
    keyboard.row(
        types.InlineKeyboardButton("🌐 Наш сайт", url="https://yandex-legal-pros.lovable.app/"),  # ЗАМЕНИТЕ НА ВАШ САЙТ!
        types.InlineKeyboardButton("📞 Связаться", callback_data="contact_manager")
    )
    
    return keyboard

def category_menu(category_key):
    """Меню конкретной категории"""
    keyboard = types.InlineKeyboardMarkup()
    service = services[category_key]
    
    # Кнопки услуг в этой категории
    for key, option in service["options"].items():
        keyboard.add(types.InlineKeyboardButton(
            option, 
            callback_data=f"serv_{key}"
        ))
    
    # Кнопки навигации
    keyboard.row(
        types.InlineKeyboardButton("◀️ Назад", callback_data="main_menu"),
        types.InlineKeyboardButton("💬 Консультация", callback_data=f"consult_{category_key}")
    )
    
    return keyboard

def service_menu(service_key):
    """Меню конкретной услуги"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # Основные кнопки
    keyboard.add(
        types.InlineKeyboardButton(
            "📄 Подробнее на сайте", 
            url=f"https://yandex-legal-pros.lovable.app//service/{service_key}"  # ЗАМЕНИТЕ НА ВАШ САЙТ!
        ),
        types.InlineKeyboardButton(
            "💬 Обсудить с менеджером", 
            callback_data=f"contact_{service_key}"
        )
    )
    
    # Кнопки навигации
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
    # Отправляем уведомление администратору
    user = message.from_user
    user_info = {
        'id': user.id,
        'first_name': user.first_name or 'Не указано',
        'last_name': user.last_name or 'Не указана',
        'username': user.username or 'Нет логина'
    }
    notify_admin(user_info, "запустил бота")
    
    # Приветствуем пользователя
    welcome_text = (
        "<b>Добро пожаловать в юридическую консультацию!</b>\n\n"
        "Я помогу вам выбрать нужную услугу:\n"
        "• Регистрация ООО, АО, ИП, НКО\n"
        "• Юридические адреса по всей России\n"
        "• Миграция и ликвидация компаций\n\n"
        "<i>Выберите категорию:</i>"
    )
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode='HTML',
        reply_markup=main_menu()
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    """Обработчик команды /help"""
    help_text = (
        "<b>Доступные команды:</b>\n"
        "/start - Главное меню\n"
        "/help - Справка\n"
        "/manager - Связаться с менеджером\n\n"
        "<i>Просто нажимайте на кнопки в меню для навигации</i>"
    )
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')

@bot.message_handler(commands=['manager'])
def manager_command(message):
    """Обработчик команды /manager"""
    # Уведомление администратору
    user = message.from_user
    user_info = {
        'id': user.id,
        'first_name': user.first_name or 'Не указано',
        'last_name': user.last_name or 'Не указана',
        'username': user.username or 'Нет логина'
    }
    notify_admin(user_info, "запросил контакт через команду /manager")
    
    contact_manager(message.chat.id)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Обработчик нажатий на все inline-кнопки"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user = call.from_user
    
    # Убираем "часики" на кнопке
    bot.answer_callback_query(call.id)
    
    # ===== ГЛАВНОЕ МЕНЮ =====
    if call.data == "main_menu":
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="<b>Выберите категорию услуги:</b>",
            parse_mode='HTML',
            reply_markup=main_menu()
        )
    
    # ===== КАТЕГОРИИ (cat_registration, cat_addresses...) =====
    elif call.data.startswith("cat_"):
        category_key = call.data[4:]  # Убираем "cat_"
        
        if category_key in services:
            category = services[category_key]
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"<b>{category['name']}</b>\n\n<i>Выберите конкретную услугу:</i>",
                parse_mode='HTML',
                reply_markup=category_menu(category_key)
            )
    
    # ===== УСЛУГИ (serv_reg_llc, serv_migration...) =====
    elif call.data.startswith("serv_"):
        service_key = call.data[5:]  # Убираем "serv_"
        
        # Если есть описание - показываем его
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
    
    # ===== КОНСУЛЬТАЦИЯ ПО КАТЕГОРИИ =====
    elif call.data.startswith("consult_"):
        category_key = call.data[8:]
        if category_key in services:
            # Уведомление администратору
            user_info = {
                'id': user.id,
                'first_name': user.first_name or 'Не указано',
                'last_name': user.last_name or 'Не указана',
                'username': user.username or 'Нет логина'
            }
            notify_admin(user_info, "запросил консультацию", 
                        f"категория: {services[category_key]['name']}")
            
            contact_manager(chat_id, f"консультация по категории: {services[category_key]['name']}")
    
    # ===== СВЯЗЬ С МЕНЕДЖЕРОМ =====
    elif call.data.startswith("contact_"):
        service_key = call.data[8:] if call.data != "contact_manager" else ""
        
        # Определяем название услуги для уведомления
        service_name = "общая консультация"
        if service_key:
            # Пытаемся найти название услуги
            for category in services.values():
                if service_key in category["options"]:
                    service_name = category["options"][service_key]
                    break
        
        # Уведомление администратору
        user_info = {
            'id': user.id,
            'first_name': user.first_name or 'Не указано',
            'last_name': user.last_name or 'Не указана',
            'username': user.username or 'Нет логина'
        }
        notify_admin(user_info, "запросил контакт с менеджером", service_name)
        
        contact_manager(chat_id, service_name)
    
    # ===== ОШИБКА (если callback_data не распознан) =====
    else:
        bot.answer_callback_query(call.id, text="⚠️ Эта кнопка еще не настроена", show_alert=True)

# ========== ФУНКЦИЯ СВЯЗИ С МЕНЕДЖЕРОМ ==========
def contact_manager(chat_id, service="общая консультация"):
    """Отправляет контакты менеджера"""
    manager_text = (
        f"<b>📞 Связь с менеджером</b>\n\n"
        f"<i>Услуга:</i> {service}\n\n"
        "Чтобы обсудить детали, вы можете:\n\n"
        "1. <b>Позвонить:</b> +7 (985) 057-64-65\n"  # ЗАМЕНИТЕ НА ВАШ ТЕЛЕФОН!
        "2. <b>Email:</b> delovye-resheniya@mail.ru\n"     # ЗАМЕНИТЕ НА ВАШ EMAIL!
        "3. <b>Telegram:</b> @DelovyeResheniya\n\n"     # ЗАМЕНИТЕ НА ЮЗЕРНЕЙМ МЕНЕДЖЕРА!
        "🕐 <i>Рабочее время: Пн-Пт с 9:00 до 18:00</i>\n\n"
        "<i>Укажите, что обратились через бота для получения приоритетного обслуживания.</i>"
    )
    
    # Кнопка для возврата в главное меню
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu"))
    
    bot.send_message(
        chat_id,
        manager_text,
        parse_mode='HTML',
        reply_markup=keyboard
    )

# ========== ОБРАБОТКА ОБЫЧНЫХ СООБЩЕНИЙ ==========
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    """Обработчик текстовых сообщений (если пользователь что-то пишет)"""
    # Уведомление администратору о текстовом сообщении
    user = message.from_user
    user_info = {
        'id': user.id,
        'first_name': user.first_name or 'Не указано',
        'last_name': user.last_name or 'Не указана',
        'username': user.username or 'Нет логина'
    }
    notify_admin(user_info, f"написал сообщение: {message.text[:50]}...")
    
    # Предлагаем воспользоваться меню
    bot.send_message(
        message.chat.id,
        "Используйте кнопки меню для навигации ☝️\n"
        "Или нажмите /start для открытия главного меню.",
        reply_markup=types.ReplyKeyboardRemove()
    )

# ========== ЗАПУСК БОТА ==========
if __name__ == "__main__":
    print("=" * 50)
    print("✅ Бот запущен и работает на Railway!")
    print(f"👨‍💼 Уведомления будут отправляться ID: {ADMIN_ID}")
    print("=" * 50)
    
    # Удаляем вебхук на всякий случай
    bot.remove_webhook()
    
    # Запускаем опрос серверов Telegram
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        print("Перезапуск через 5 секунд...")
        import time
        time.sleep(5)
    
