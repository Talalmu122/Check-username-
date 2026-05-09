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

# --- دالة الفحص الذكي ---
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
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
    }
    
    try:
        response = requests.get(urls[platform], headers=headers, timeout=4.0, allow_redirects=True)
        content = response.text.lower()
        status = response.status_code

        # شروط المتاح لكل منصة
        is_available = False
        if platform == "SONY":
            if status == 404 or "login" in response.url.lower(): is_available = True
        elif platform == "INSTA" and (status == 404 or "isn't available" in content): is_available = True
        elif platform == "TIKTOK" and (status == 404 or "couldn't find" in content): is_available = True
        elif platform == "X" and (status == 404 or "doesn’t exist" in content): is_available = True
        elif platform == "SNAP" and (status == 404 or "not found" in content): is_available = True
        elif platform == "DISCORD" and status == 404: is_available = True

        if is_available:
            return f"✅ `{username}`"
        return None # العودة بـ None إذا كان مأخوذاً
    except:
        return None

# --- دالة التوليد العشوائي ---
def generate_username(length):
    return ''.join(random.choices(CHARS, k=int(length)))

# --- القائمة الرئيسية ---
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
    bot.send_message(message.chat.id, "🛰 **بوت الصيد الذكي (المتاح فقط)**\n\nسيتم عرض اليوزرات المتاحة ✅ فقط لتسريع عملية القنص.", reply_markup=main_markup(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('p_'))
def select_filter(call):
    platform = call.data.split('_')[1]
    markup = types.InlineKeyboardMarkup(row_width=1)
    for l in ["3", "4", "5"]:
        markup.add(types.InlineKeyboardButton(f"تخمين عشوائي ({l}) أحرف", callback_data=f"g_{platform}_{l}"))
    markup.add(types.InlineKeyboardButton("⬅️ عودة", callback_data="back"))
    bot.edit_message_text(f"🎯 منصة: **{platform}**\nاختر الطول:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('g_'))
def execute_hunt(call):
    _, platform, length = call.data.split('_')
    bot.answer_callback_query(call.id, "🔎 جاري البحث عن متاح...")
    
    def worker(_):
        user = generate_username(length)
        return check_availability(platform, user)

    # فحص 15 يوزر في كل ضغطة لزيادة فرص إيجاد متاح
    with ThreadPoolExecutor(max_workers=15) as executor:
        all_results = list(executor.map(worker, range(15)))
    
    # تصفية النتائج لإبقاء المتاح فقط (حذف الـ None)
    available_only = [res for res in all_results if res is not None]
    
    if available_only:
        msg = f"🛰 **يوزرات متاحة لـ {platform}:**\n\n" + "\n".join(available_only)
    else:
        msg = f"🛰 **نتائج {platform}:**\n\nللأسف، لم يتم العثور على متاح في هذه الدفعة (15 محاولة). جرب مرة أخرى 🔄"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 صيد جديد", callback_data=call.data))
    markup.add(types.InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="back"))
    
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    bot.edit_message_text("🎯 اختر المنصة:", call.message.chat.id, call.message.message_id, reply_markup=main_markup())

if __name__ == "__main__":
    bot.infinity_polling()
