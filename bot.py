import telebot
from telebot import types
import random
import string
import os
import requests
from concurrent.futures import ThreadPoolExecutor

# --- الإعدادات ---
# تأكد من إضافة BOT_TOKEN في Settings -> Secrets في GitHub
API_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

CHARS = string.ascii_lowercase + string.digits

# --- دالة فحص التوفر ---
def check_availability(platform, username):
    urls = {
        "INSTA": f"https://www.instagram.com/{username}/",
        "TIKTOK": f"https://www.tiktok.com/@{username}",
        "X": f"https://twitter.com/{username}",
        "SNAP": f"https://www.snapchat.com/add/{username}",
        "DISCORD": f"https://discord.com/api/v9/users/{username}"
    }
    
    try:
        # فحص سريع بدون بروكسي للاستفادة من سرعة GitHub
        response = requests.get(urls[platform], timeout=2.0)
        if response.status_code == 404:
            return "✅ متاح"
        else:
            return "❌ ممتلئ"
    except:
        return "⚠️ فحص يدوي"

# --- دالة توليد اليوزرات العشوائية (بدون تربل) ---
def generate_username(filter_type):
    # تم توحيد المنطق ليكون عشوائي تماماً حسب الطول المطلوب
    length = 4 # الطول الافتراضي
    if filter_type in ["3", "3s"]:
        length = 3
    elif filter_type in ["4", "4s"]:
        length = 4
    elif filter_type == "5":
        length = 5
        
    return ''.join(random.choices(CHARS, k=length))

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
    bot.send_message(message.chat.id, "🚀 **بوت الصيد العشوائي السريع**\n\nتم تحديث نظام التوليد ليكون عشوائياً بالكامل بدون تكرار ممل.", reply_markup=main_markup(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('p_'))
def select_filter(call):
    platform = call.data.split('_')[1]
    markup = types.InlineKeyboardMarkup(row_width=2)
    filters = [
        ("ثلاثي عشوائي", "3"),
        ("رباعي عشوائي", "4"),
        ("خماسي عشوائي", "5")
    ]
    for name, key in filters:
        markup.add(types.InlineKeyboardButton(name, callback_data=f"g_{platform}_{key}"))
    
    markup.add(types.InlineKeyboardButton("⬅️ عودة", callback_data="back"))
    bot.edit_message_text(f"🎯 منصة الفحص: **{platform}**", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# --- تنفيذ التخمين بنظام التوازي السريع ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('g_'))
def execute_hunt(call):
    _, platform, f_type = call.data.split('_')
    bot.answer_callback_query(call.id, "⚡ جاري الصيد...")
    
    def worker(_):
        user = generate_username(f_type)
        status = check_availability(platform, user)
        return f"`{user}` -> {status}"

    # فحص 10 يوزرات في وقت واحد لزيادة السرعة
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(worker, range(10)))
    
    msg = f"🛰 **نتائج الصيد لـ {platform}:**\n\n" + "\n".join(results)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 صيد مجموعة جديدة", callback_data=call.data))
    markup.add(types.InlineKeyboardButton("🏠 عودة", callback_data="back"))
    
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    bot.edit_message_text("🎯 اختر المنصة لبدء التخمين:", call.message.chat.id, call.message.message_id, reply_markup=main_markup())

if __name__ == "__main__":
    bot.infinity_polling()
