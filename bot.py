import telebot
from telebot import types
import random
import string
import os
import requests
from concurrent.futures import ThreadPoolExecutor

# --- الإعدادات ---
API_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

CHARS = string.ascii_lowercase + string.digits

# --- دالة فحص التوفر المسرّعة ---
def check_availability(platform, username):
    urls = {
        "INSTA": f"https://www.instagram.com/{username}/",
        "TIKTOK": f"https://www.tiktok.com/@{username}",
        "X": f"https://twitter.com/{username}",
        "SNAP": f"https://www.snapchat.com/add/{username}",
        "DISCORD": f"https://discord.com/api/v9/users/{username}"
    }
    
    try:
        # تقليل الـ timeout لـ 2.5 ثانية لزيادة السرعة
        response = requests.get(urls[platform], timeout=2.5)
        if response.status_code == 404:
            return "✅ متاح"
        else:
            return "❌ ممتلئ"
    except:
        return "⚠️ فحص يدوي"

# --- دالة توليد اليوزرات ---
def generate_username(filter_type):
    if filter_type == "3": return ''.join(random.choices(CHARS, k=3))
    elif filter_type == "3s":
        c1 = random.choice(string.ascii_lowercase)
        c2 = random.choice(CHARS)
        return c1 + c1 + c2
    elif filter_type == "4": return ''.join(random.choices(CHARS, k=4))
    elif filter_type == "4s":
        c1 = random.choice(string.ascii_lowercase)
        c2 = random.choice(CHARS)
        return c1 + c1 + c1 + c2
    elif filter_type == "5": return ''.join(random.choices(CHARS, k=5))
    return None

# --- لوحة التحكم ---
def main_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    platforms = [
        types.InlineKeyboardButton("Snapchat", callback_data="p_SNAP"),
        types.InlineKeyboardButton("X (Twitter)", callback_data="p_X"),
        types.InlineKeyboardButton("TikTok", callback_data="p_TIKTOK"),
        types.InlineKeyboardButton("Instagram", callback_data="p_INSTA"),
        types.InlineKeyboardButton("Discord", callback_data="p_DISCORD")
    ]
    markup.add(*platforms)
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(message.chat.id, "🚀 **بوت الصيد السريع (Turbo Mode)**\nتم تفعيل نظام المهام المتعددة.", reply_markup=main_markup(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('p_'))
def select_filter(call):
    platform = call.data.split('_')[1]
    markup = types.InlineKeyboardMarkup(row_width=2)
    for f in [("ثلاثي","3"), ("شبه ثلاثي","3s"), ("رباعي","4"), ("شبه رباعي","4s"), ("خماسي","5")]:
        markup.add(types.InlineKeyboardButton(f[0], callback_data=f"g_{platform}_{f[1]}"))
    bot.edit_message_text(f"🎯 منصة: **{platform}** | اختر الفلتر:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# --- تنفيذ التخمين بنظام التوازي (Threading) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('g_'))
def execute_hunt(call):
    _, platform, f_type = call.data.split('_')
    bot.answer_callback_query(call.id, "⚡ جاري الصيد السريع...")
    
    def worker(_):
        user = generate_username(f_type)
        status = check_availability(platform, user)
        return f"`{user}` -> {status}"

    # تنفيذ 10 عمليات فحص في وقت واحد
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(worker, range(10)))
    
    msg = f"🛰 **نتائج الصيد لـ {platform}:**\n\n" + "\n".join(results)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 صيد مجموعة جديدة", callback_data=call.data))
    markup.add(types.InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="back"))
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    bot.edit_message_text("🎯 اختر المنصة:", call.message.chat.id, call.message.message_id, reply_markup=main_markup())

if __name__ == "__main__":
    bot.infinity_polling()
