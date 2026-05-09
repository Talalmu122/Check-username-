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

# --- دالة فحص التوفر المحدثة ---
def check_availability(platform, username):
    urls = {
        "INSTA": f"https://www.instagram.com/{username}/",
        "TIKTOK": f"https://www.tiktok.com/@{username}",
        "X": f"https://twitter.com/{username}",
        "SNAP": f"https://www.snapchat.com/add/{username}",
        "SONY": f"https://my.playstation.com/profile/{username}",
        "DISCORD": f"https://discord.com/api/v9/users/{username}"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(urls[platform], headers=headers, timeout=3.0, allow_redirects=True)
        
        # تحسين فحص سوني: سوني غالباً تعيد 404 أو تحول لصفحة دخول إذا كان متاح
        if response.status_code == 404:
            return "✅ متاح"
        elif platform == "SONY" and ("login" in response.url.lower() or "error" in response.url.lower()):
            return "✅ متاح"
        else:
            return "❌ ممتلئ"
    except:
        return "⚠️ فحص يدوي"

# --- دالة توليد اليوزرات العشوائية تماماً ---
def generate_username(length):
    return ''.join(random.choices(CHARS, k=int(length)))

# --- لوحة التحكم الرئيسية ---
def main_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    # تأكدت هنا من وجود PlayStation 🎮
    platforms = [
        types.InlineKeyboardButton("Instagram", callback_data="p_INSTA"),
        types.InlineKeyboardButton("TikTok", callback_data="p_TIKTOK"),
        types.InlineKeyboardButton("Snapchat", callback_data="p_SNAP"),
        types.InlineKeyboardButton("X (Twitter)", callback_data="p_X"),
        types.InlineKeyboardButton("PlayStation 🎮", callback_data="p_SONY"),
        types.InlineKeyboardButton("Discord", callback_data="p_DISCORD")
    ]
    markup.add(*platforms)
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(message.chat.id, "🚀 **بوت الصيد السريع | طلال**\n\nاختر المنصة وابدأ التخمين العشوائي:", reply_markup=main_markup(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('p_'))
def select_filter(call):
    platform = call.data.split('_')[1]
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # خيارات التخمين بناءً على عدد الحرف
    lengths = [("ثلاثي عشوائي", "3"), ("رباعي عشوائي", "4"), ("خماسي عشوائي", "5")]
    for text, val in lengths:
        markup.add(types.InlineKeyboardButton(text, callback_data=f"g_{platform}_{val}"))
    
    markup.add(types.InlineKeyboardButton("⬅️ عودة للمنصات", callback_data="back"))
    bot.edit_message_text(f"🎯 منصة الفحص: **{platform}**\n\nاختر طول اليوزر المطلوب:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('g_'))
def execute_hunt(call):
    _, platform, length = call.data.split('_')
    bot.answer_callback_query(call.id, "⚡ جاري الفحص السريع...")
    
    def worker(_):
        user = generate_username(length)
        status = check_availability(platform, user)
        return f"`{user}` -> {status}"

    # زيادة السرعة بـ 10 مهام متزامنة
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(worker, range(10)))
    
    msg = f"🛰 **نتائج الصيد لـ {platform}:**\n\n" + "\n".join(results)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 صيد مجموعة جديدة", callback_data=call.data))
    markup.add(types.InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="back"))
    
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    bot.edit_message_text("🎯 اختر المنصة لبدء التخمين:", call.message.chat.id, call.message.message_id, reply_markup=main_markup())

if __name__ == "__main__":
    bot.infinity_polling()
