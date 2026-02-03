import telebot
from telebot import types
import os
from keep_alive import keep_alive

# Запускаем веб-сервер для поддержания активности
keep_alive()

# Токен берется из секретов Replit
TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)

# --- БАЗА ДАННЫХ УСЛУГ ---
# Простая структура для примера. Можно расширять.
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

# --- ОПИСАНИЯ УСЛУГ ДЛЯ КНОПКИ "ПОДРОБНЕЕ" ---
service_details = {
    "reg_llc": "<b>Регистрация ООО</b>\n\nВключено:\n✓ Проверка названия\n✓ Подготовка документов\n✓ Открытие расчетного счета\n✓ Государственная пошлина\n\nСрок: 7 рабочих дней\nЦена: 15 000 ₽",
    "migration": "<b>Миграция компании в Москву</b>\n\nПроцесс:\n1. Внесение изменений в ЕГРЮЛ\n2. Смена юридического адреса\n3. Уведомление фондов\n4. Постановка на учет в ИФНС\n\nСрок: от 30 дней\nЦена: от 45 000 ₽",
    # Добавьте описания для других услуг по аналогии
}

# --- ГЛАВНОЕ МЕНЮ ---
def main_menu():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    buttons = []
    for key, service in services.items():
        buttons.append(
            types.InlineKeyboardButton(
                service["name"], 
                callback_data=f"cat_{key}"
            )
        )
    
    # Распределяем кнопки по 2 в строке
    for i in range(0, len(buttons), 2):
        if i+1 < len(buttons):
            keyboard.add(buttons[i], buttons[i+1])
        else:
            keyboard.add(buttons[i])
    
    # Кнопки связи всегда внизу
    keyboard.row(
        types.InlineKeyboardButton("🌐 https://yandex-legal-pros.lovable.app/", url="https://ваш-сайт.ru"),
        types.InlineKeyboardButton("👨‍💼 Связаться с менеджером", callback_data="contact_manager")
    )
    
    return keyboard

# --- МЕНЮ КОНКРЕТНОЙ КАТЕГОРИИ ---
def category_menu(category_key):
    keyboard = types.InlineKeyboardMarkup()
    service = services[category_key]
    
    for key, option in service["options"].items():
        keyboard.add(
            types.InlineKeyboardButton(option, callback_data=f"serv_{key}")
        )
    
    keyboard.row(
        types.InlineKeyboardButton("◀️ Назад", callback_data="main_menu"),
        types.InlineKeyboardButton("📞 Консультация", callback_data="contact_manager")
    )
    
    return keyboard

# --- МЕНЮ КОНКРЕТНОЙ УСЛУГИ ---
def service_menu(service_key):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        types.InlineKeyboardButton("📄 Подробнее на сайте", url=f"https://yandex-legal-pros.lovable.app/{service_key}"),
        types.InlineKeyboardButton("💬 Обсудить с менеджером", callback_data=f"contact_{service_key}")
    )
    
    keyboard.add(
        types.InlineKeyboardButton("◀️ К категории", callback_data=f"cat_{service_key.split('_')[0]}"),
        types.InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu")
    )
    
    return keyboard

# --- ОБРАБОТЧИКИ КОМАНД ---
@bot.message_handler(commands=['start'])
def start_command(message):
    welcome_text = (
        "<b>Добро пожаловать в юридическую консультацию!</b>\n\n"
        "Я помогу вам выбрать нужную услугу:\n"
        "• Регистрация ООО, АО, ИП, НКО\n"
        "• Юридические адреса по всей России\n"
        "• Миграция и ликвидация компаний\n\n"
        "Выберите категорию:"
    )
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode='HTML',
        reply_markup=main_menu()
    )

@bot.message_handler(commands=['manager'])
def manager_command(message):
    contact_manager(message.chat.id)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # Удаляем "часики" на кнопке
    bot.answer_callback_query(call.id)
    
    # Главное меню
    if call.data == "main_menu":
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Выберите категорию услуги:",
            parse_mode='HTML',
            reply_markup=main_menu()
        )
    
    # Категории услуг (cat_registration, cat_addresses...)
    elif call.data.startswith("cat_"):
        category_key = call.data[4:]  # Убираем "cat_"
        
        if category_key in services:
            category = services[category_key]
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"<b>{category['name']}</b>\n\nВыберите конкретную услугу:",
                parse_mode='HTML',
                reply_markup=category_menu(category_key)
            )
    
    # Конкретные услуги (serv_reg_llc, serv_migration...)
    elif call.data.startswith("serv_"):
        service_key = call.data[5:]  # Убираем "serv_"
        
        # Если есть описание - показываем
        if service_key in service_details:
            text = service_details[service_key]
        else:
            # Иначе показываем стандартное
            text = f"<b>Услуга</b>\n\nВы выбрали услугу. Хотите узнать подробности на сайте или обсудить с менеджером?"
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text + "\n\n👇 Выберите действие:",
            parse_mode='HTML',
            reply_markup=service_menu(service_key)
        )
    
    # Связь с менеджером
    elif call.data.startswith("contact_"):
        service_key = call.data[8:] if call.data != "contact_manager" else "общая консультация"
        contact_manager(chat_id, service_key)
    
    # Просто контакт (без указания услуги)
    elif call.data == "contact_manager":
        contact_manager(chat_id)

def contact_manager(chat_id, service="общая консультация"):
    manager_text = (
        f"<b>Связь с менеджером</b>\n\n"
        f"Услуга: <i>{service}</i>\n\n"
        "Чтобы обсудить детали, вы можете:\n\n"
        "1. 📞 Позвонить: <b>+7 (985) 057-64-65</b>\n"
        "2. 📧 Email: <b>delovye-resheniya@mail.ru</b>\n"
        "3. ✍️ Написать в Telegram: @DelovyeResheniya\n\n"
        "<i>Укажите, что обратились через бота для получения приоритетного обслуживания.</i>"
    )
    
    bot.send_message(
        chat_id,
        manager_text,
        parse_mode='HTML',
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("✅ Я связался", callback_data="main_menu")
        )
    )

# Запуск бота
print("✅ Бот запущен и работает в облаке!")
bot.infinity_polling(timeout=60, long_polling_timeout=60)
