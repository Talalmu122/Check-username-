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
# استخرج الـ SessionID من متصفحك بعد تسجيل الدخول لحسابك الجديد
INSTA_SESSION_ID = os.getenv('INSTA_SESSION') 

bot = telebot.TeleBot(API_TOKEN)
CHARS = string.ascii_lowercase + string.digits

def check_insta_linked(username):
    """فحص اليوزر من داخل الحساب المربوط"""
    # رابط داخلي للفحص السريع
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)",
        "X-IG-App-ID": "936619743392459", # ثابت لنسخة الويب
        "Cookie": f"sessionid={INSTA_SESSION_ID}"
    }
    try:
        # تأخير بسيط لحماية الحساب الجديد من البند السريع
        time.sleep(random.uniform(1.5, 3.0))
        response = requests.get(url, headers=headers, timeout=10)
        
        # إذا كانت الاستجابة 404 أو محتوى فارغ يعني متاح
        if response.status_code == 404:
            return f"✅ INSTA (Linked): `{username}`"
        return None
    except:
        return None

def generate_pattern(p_type):
    """توليد الأنماط الفخمة (ثلاثي، شبه رباعي...)"""
    c = random.choices(CHARS, k=3)
    if p_type == "3":
        return "".join(random.choices(CHARS, k=3))
    elif p_type == "3s": # aab / aba
        return random.choice([f"{c[0]}{c[0]}{c[1]}", f"{c[0]}{c[1]}{c[0]}"])
    elif p_type == "4":
        return "".join(random.choices(CHARS, k=4))
    elif p_type == "4s": # aaab / aabb
        return random.choice([f"{c[0]}{c[0]}{c[0]}{c[1]}", f"{c[1]}{c[1]}{c[0]}{c[0]}"])
    return "".join(random.choices(CHARS, k=5))

# --- لوحة التحكم ---
def main_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    options = [("ثلاثي", "3"), ("شبه ثلاثي", "3s"), ("رباعي", "4"), ("شبه رباعي", "4s")]
    for text, val in options:
        markup.add(types.InlineKeyboardButton(text, callback_data=f"g_LINK_{val}"))
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(message.chat.id, "🛰 **قناص إنستقرام المربوط | نسخة طلال**\n\nيتم التخمين الآن عبر جلسة حسابك النشطة. يرجى مراقبة الحساب من البند.", reply_markup=main_markup(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('g_'))
def execute_hunt(call):
    _, _, p_type = call.data.split('_')
    bot.answer_callback_query(call.id, "🔎 جاري التخمين من داخل الحساب...")
    
    def worker(_):
        user = generate_pattern(p_type)
        return check_insta_linked(user)

    # السرعة منخفضة جداً (2 فقط) لأن الحسابات الجديدة حساسة جداً
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = [res for res in executor.map(worker, range(5)) if res]
    
    if results:
        msg = f"🛰 **صيد مؤكد من الحساب ✅:**\n\n" + "\n".join(results)
    else:
        msg = "🛰 **نتائج الفحص:**\n\nلم يتم العثور على متاح حالياً. تم الفحص ببطء لحماية حسابك 🛡"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 صيد جديد", callback_data=call.data))
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

if __name__ == "__main__":
    bot.infinity_polling()
