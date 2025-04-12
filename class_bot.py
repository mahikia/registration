
import telebot
from datetime import datetime, timedelta
import os

# توکن ربات از متغیر محیطی
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

students = {
    "مریم گل پاشا": {"days": ["Sunday"], "sessions": 8},
    "مرجان": {"days": ["Saturday", "Monday"], "sessions": 8},
    "سهیل": {"days": ["Monday", "Wednesday"], "sessions": 8},
    "محمدرضا": {"days": ["Saturday", "Wednesday"], "sessions": 8},
    "لیدا": {"days": ["Sunday", "Tuesday"], "sessions": 8},
    "هستی": {"days": ["Saturday", "Monday"], "sessions": 8},
    "نیکی": {"days": ["Saturday", "Monday"], "sessions": 8},
    "محدثه": {"days": ["Monday", "Wednesday"], "sessions": 8},
    "زیور": {"days": ["Saturday", "Sunday", "Wednesday"], "sessions": 12},
    "زینب": {"days": ["Tuesday", "Thursday"], "sessions": 8},
    "سارا": {"days": ["Monday", "Wednesday"], "sessions": 8},
    "احسان": {"days": ["Tuesday", "Thursday"], "sessions": 8},
    "الا": {"days": ["Monday", "Wednesday"], "sessions": 8},
    "هانیه": {"days": ["Monday", "Wednesday"], "sessions": 8},
    "اشکان": {"days": ["Monday", "Wednesday"], "sessions": 8},
    "مریم": {"days": ["Sunday", "Tuesday"], "sessions": 8}
}

user_data = {}

def generate_schedule():
    schedule = ""
    for name, details in students.items():
        schedule += f"**{name}:**\n"
        for day in details["days"]:
            schedule += f"- {day}\n"
        schedule += f"  *Sessions*: {details['sessions']} sessions\n\n"
    return schedule

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! به بوت کلاس‌ها خوش آمدید.\nبرای مشاهده برنامه کلاس‌ها، از دستور /schedule استفاده کنید.\nبرای ثبت نام از دستور /register استفاده کنید.")

@bot.message_handler(commands=['schedule'])
def send_schedule(message):
    schedule = generate_schedule()
    bot.reply_to(message, schedule, parse_mode="Markdown")

@bot.message_handler(commands=['register'])
def register_user(message):
    bot.reply_to(message, "برای ثبت‌نام، لطفا نام خود را ارسال کنید.\n(مثال: مریم گل پاشا)")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def process_registration(message):
    user_name = message.text.strip()
    if user_name in students:
        user_data[message.chat.id] = {"name": user_name}
        bot.reply_to(message, f"شما برای کلاس‌های {user_name} ثبت‌نام شدید.\nلطفا تاریخ شروع کلاس خود را وارد کنید (مثال: 2025-04-10).")
        bot.register_next_step_handler(message, get_start_date)
    else:
        bot.reply_to(message, "نام شما در لیست کلاس‌ها نیست. لطفا نام خود را صحیح وارد کنید.")

def get_start_date(message):
    start_date_str = message.text.strip()
    chat_id = message.chat.id
    user_name = user_data[chat_id]["name"]

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = start_date + timedelta(weeks=students[user_name]["sessions"] // 2)

        bot.reply_to(message, f"تاریخ شروع کلاس: {start_date.date()}\nتاریخ پایان: {end_date.date()}\nروزهای کلاس: {', '.join(students[user_name]['days'])}")
        bot.reply_to(message, "لطفا فیش پرداخت را ارسال کنید.")
        bot.register_next_step_handler(message, handle_receipt)
    except ValueError:
        bot.reply_to(message, "فرمت تاریخ اشتباه است. لطفا فرمت YYYY-MM-DD را وارد کنید.")

def handle_receipt(message):
    chat_id = message.chat.id
    user_name = user_data[chat_id]["name"]

    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        os.makedirs("images", exist_ok=True)
        with open(f"images/{user_name}_receipt.jpg", 'wb') as f:
            f.write(downloaded_file)

        bot.reply_to(message, "فیش پرداخت با موفقیت دریافت شد ✅\nپرداخت تایید و ثبت‌نام شما کامل شد 🎉")
    else:
        bot.reply_to(message, "لطفا عکس فیش را ارسال کنید.")

bot.infinity_polling()
