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

# --- دالة فحص التوفر المتقدمة ---
def check_availability(platform, username):
    # الروابط المحدثة للفحص
    urls = {
        "INSTA": f"https://www.instagram.com/{username}/",
        "TIKTOK": f"https://www.tiktok.com/@{username}",
        "X": f"https://twitter.com/{username}",
        "SNAP": f"https://www.snapchat.com/add/{username}",
        "SONY": f"https://my.playstation.com/profile/{username}", # رابط سوني
        "DISCORD": f"https://discord.com/api/v9/users/{username}"
    }
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }
        response = requests.get(urls[platform], headers=headers, timeout=3.0, allow_redirects=True)
        
        # منطق الفحص المحدث:
        # 404 تعني الصفحة غير موجودة (غالباً متاح)
        if response.status_code == 404:
            return "✅ متاح"
        # في سوني وبعض المنصات، قد يعيد توجيهك لصفحة تسجيل دخول إذا كان اليوزر متاح
        elif platform == "SONY" and "login" in response.url.lower():
            return "✅ متاح"
        else:
            return "❌ ممتلئ"
    except:
        return "⚠️ خطأ فحص"

# --- دالة توليد اليوزرات العشوائية ---
def generate_username(length):
    return ''.join(random.choices(CHARS, k=int(length)))

# --- لوحة التحكم ---
def main_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    platforms = [
        types.InlineKeyboardButton("Snapchat", callback_data="p_SNAP"),
        types.InlineKeyboardButton("X (Twitter)", callback_data="p_X"),
        types.InlineKeyboardButton("TikTok", callback_data="p_TIKTOK"),
        types.InlineKeyboardButton("Instagram", callback_data="p_INSTA"),
        types.InlineKeyboardButton("PlayStation 🎮", callback_data="p_SONY"),
        types.InlineKeyboardButton("Discord", callback_data="p_DISCORD")
    ]
    markup.add(*platforms)
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(message.chat.id, "🚀 **بوت الصيد المطور (نسخة سوني + العشوائية)**\n\nاختر المنصة وابدأ التخمين السريع:", reply_markup=main_markup(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('p_'))
def select_filter(call):
    platform = call.data.split('_')[1]
    markup = types.InlineKeyboardMarkup(row_width=2)
    # خيارات الطول عشوائية تماماً
    for l in ["3", "4", "5"]:
        markup.add(types.InlineKeyboardButton(f"تخمين {l} أحرف", callback_data=f"g_{platform}_{l}"))
    
    markup.add(types.InlineKeyboardButton("⬅️ عودة", callback_data="back"))
    bot.edit_message_text(f"🎯 منصة الفحص: **{platform}**\nاختر طول اليوزر:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('g_'))
def execute_hunt(call):
    _, platform, length = call.data.split('_')
    bot.answer_callback_query(call.id, "⚡ جاري الفحص الذكي...")
    
    def worker(_):
        user = generate_username(length)
        status = check_availability(platform, user)
        return f"`{user}` -> {status}"

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(worker, range(10)))
    
    msg = f"🛰 **نتائج صيد {platform}:**\n\n" + "\n".join(results)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 صيد جديد", callback_data=call.data))
    markup.add(types.InlineKeyboardButton("🏠 عودة", callback_data="back"))
    
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    bot.edit_message_text("🎯 اختر المنصة:", call.message.chat.id, call.message.message_id, reply_markup=main_markup())

if __name__ == "__main__":
    bot.infinity_polling()
