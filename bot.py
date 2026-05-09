import telebot
from telebot import types
import random
import string
import os
import requests
import time
from concurrent.futures import ThreadPoolExecutor

# --- الإعدادات ---
API_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)
CHARS = string.ascii_lowercase + string.digits

# قائمة متصفحات وهمية لتمويه المنصات
USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
]

def check_availability(platform, username):
    urls = {
        "INSTA": f"https://www.instagram.com/{username}/",
        "TIKTOK": f"https://www.tiktok.com/@{username}",
        "X": f"https://twitter.com/{username}",
        "SNAP": f"https://www.snapchat.com/add/{username}",
        "SONY": f"https://my.playstation.com/profile/{username}"
    }
    
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    
    try:
        # إضافة وقت انتظار عشوائي بسيط (0.5 إلى 1.5 ثانية) لتجنب كشف البوت
        time.sleep(random.uniform(0.5, 1.5))
        
        response = requests.get(urls[platform], headers=headers, timeout=8, allow_redirects=True)
        content = response.text.lower()
        
        # --- فحص سناب شات (الأكثر دقة) ---
        if platform == "SNAP":
            # إذا الصفحة فيها "bitmoji" أو "snapcode" أو "displayname" يعني مأخوذ 100%
            if any(word in content for word in ["bitmoji", "snapcode", "og:title", "public profile"]):
                return None
            if response.status_code == 404 or "not found" in content:
                return f"✅ SNAP: `{username}`"

        # --- فحص إنستقرام ---
        elif platform == "INSTA":
            if "isn't available" in content or response.status_code == 404:
                return f"✅ INSTA: `{username}`"

        # --- فحص سوني ---
        elif platform == "SONY":
            if response.status_code == 404 or "error" in response.url.lower():
                return f"✅ SONY: `{username}`"

        return None
    except:
        return None

# --- نظام التوليد والقوائم ---
def generate_username(length):
    return ''.join(random.choices(CHARS, k=int(length)))

def main_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [
        types.InlineKeyboardButton("Snapchat", callback_data="p_SNAP"),
        types.InlineKeyboardButton("Instagram", callback_data="p_INSTA"),
        types.InlineKeyboardButton("PlayStation 🎮", callback_data="p_SONY"),
        types.InlineKeyboardButton("TikTok", callback_data="p_TIKTOK"),
        types.InlineKeyboardButton("X (Twitter)", callback_data="p_X")
    ]
    markup.add(*btns)
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(message.chat.id, "🛰 **بوت الصيد الذكي | طلال**\n\nيتم الآن عرض المتاح فقط مع حماية من الحظر.", reply_markup=main_markup(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('p_'))
def select_filter(call):
    platform = call.data.split('_')[1]
    markup = types.InlineKeyboardMarkup(row_width=1)
    for l in ["3", "4", "5"]:
        markup.add(types.InlineKeyboardButton(f"تخمين ({l}) أحرف", callback_data=f"g_{platform}_{l}"))
    markup.add(types.InlineKeyboardButton("⬅️ عودة", callback_data="back"))
    bot.edit_message_text(f"🎯 منصة: **{platform}**", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('g_'))
def execute_hunt(call):
    _, platform, length = call.data.split('_')
    bot.answer_callback_query(call.id, "🔎 جاري الفحص (تم تفعيل نظام منع الحظر)...")
    
    def worker(_):
        user = generate_username(length)
        return check_availability(platform, user)

    # تقليل عدد العمال (Workers) لضمان الدقة وعدم الحظر السريع
    with ThreadPoolExecutor(max_workers=3) as executor:
        all_results = [res for res in executor.map(worker, range(10)) if res]
    
    if all_results:
        msg = f"🛰 **يوزرات متاحة لـ {platform}:**\n\n" + "\n".join(all_results)
    else:
        msg = f"🛰 **نتائج {platform}:**\n\nلم نجد متاحاً مؤكداً في هذه الدفعة. جرب مرة أخرى 🔄"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 صيد جديد", callback_data=call.data))
    markup.add(types.InlineKeyboardButton("🏠 القائمة", callback_data="back"))
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    bot.edit_message_text("🎯 اختر المنصة:", call.message.chat.id, call.message.message_id, reply_markup=main_markup())

if __name__ == "__main__":
    bot.infinity_polling()
