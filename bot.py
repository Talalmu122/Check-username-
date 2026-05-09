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

# --- دالة الفحص الذكي (الأكثر دقة) ---
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
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    try:
        response = requests.get(urls[platform], headers=headers, timeout=5.0, allow_redirects=True)
        content = response.text.lower()
        status = response.status_code

        # منطق الفحص المخصص لكل منصة لضمان الدقة
        if platform == "SONY":
            # سوني إذا كان متاح يحولك لصفحة تسجيل الدخول أو يعطي خطأ معين
            if status == 404 or "login" in response.url.lower() or "not found" in content:
                return "✅ متاح"
        
        elif platform == "INSTA":
            if status == 404 or "isn't available" in content:
                return "✅ متاح"
        
        elif platform == "TIKTOK":
            if status == 404 or "couldn't find this account" in content:
                return "✅ متاح"
        
        elif platform == "X":
            if status == 404 or "this account doesn’t exist" in content:
                return "✅ متاح"
        
        elif platform == "SNAP":
            if status == 404 or "not found" in content:
                return "✅ متاح"

        return "❌ ممتلئ"
    except:
        return "⚠️ فحص يدوي"

# --- دالة التوليد العشوائي ---
def generate_username(length):
    return ''.join(random.choices(CHARS, k=int(length)))

# --- القائمة الرئيسية (PlayStation ثابتة هنا) ---
def main_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [
        types.InlineKeyboardButton("Instagram", callback_data="p_INSTA"),
        types.InlineKeyboardButton("TikTok", callback_data="p_TIKTOK"),
        types.InlineKeyboardButton("Snapchat", callback_data="p_SNAP"),
        types.InlineKeyboardButton("X (Twitter)", callback_data="p_X"),
        types.InlineKeyboardButton("PlayStation 🎮", callback_data="p_SONY"),
        types.InlineKeyboardButton("Discord", callback_data="p_DISCORD")
    ]
    markup.add(*btns)
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(message.chat.id, "🛰 **بوت الصيد الدقيق | نسخة طلال**\n\nتم تحسين خوارزمية الفحص لتفادي النتائج الخاطئة.", reply_markup=main_markup(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('p_'))
def select_filter(call):
    platform = call.data.split('_')[1]
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # خيارات التوليد العشوائي
    for l in ["3", "4", "5"]:
        markup.add(types.InlineKeyboardButton(f"تخمين عشوائي ({l}) أحرف", callback_data=f"g_{platform}_{l}"))
    
    markup.add(types.InlineKeyboardButton("⬅️ عودة", callback_data="back"))
    bot.edit_message_text(f"🎯 منصة: **{platform}**\nاختر الطول لبدء الفحص الذكي:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('g_'))
def execute_hunt(call):
    _, platform, length = call.data.split('_')
    bot.answer_callback_query(call.id, "🔎 جاري الفحص الدقيق...")
    
    def worker(_):
        user = generate_username(length)
        status = check_availability(platform, user)
        return f"`{user}` -> {status}"

    # تشغيل 8 مهام في وقت واحد لضمان الاستقرار والدقة
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(worker, range(8)))
    
    msg = f"🛰 **نتائج الفحص لـ {platform}:**\n\n" + "\n".join(results)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 صيد جديد", callback_data=call.data))
    markup.add(types.InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="back"))
    
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    bot.edit_message_text("🎯 اختر المنصة:", call.message.chat.id, call.message.message_id, reply_markup=main_markup())

if __name__ == "__main__":
    bot.infinity_polling()
