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

# --- دالة الفحص الصارم ---
def check_availability(platform, username):
    urls = {
        "INSTA": f"https://www.instagram.com/{username}/",
        "TIKTOK": f"https://www.tiktok.com/@{username}",
        "X": f"https://twitter.com/{username}",
        "SNAP": f"https://www.snapchat.com/add/{username}",
        "SONY": f"https://my.playstation.com/profile/{username}"
    }
    
    # محاكاة متصفح آيفون حقيقي لتجنب الحظر قدر الإمكان
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    try:
        # زيادة الـ Timeout لضمان استلام كامل الصفحة
        response = requests.get(urls[platform], headers=headers, timeout=10, allow_redirects=True)
        content = response.text.lower()
        status = response.status_code

        # --- فحص سناب شات الصارم ---
        if platform == "SNAP":
            # لو الصفحة تحتوي على كود "Add" أو "Snapcode" فاليوزر مأخوذ 100%
            if "snapcode" in content or "add me" in content or "bitmoji" in content:
                return None
            # لو الصفحة أعطت 404 فعلي أو خلت من عناصر البروفايل
            if status == 404 or "not found" in content:
                return f"✅ `{username}`"
        
        # --- فحص إنستقرام الصارم ---
        elif platform == "INSTA":
            if "sorry, this page isn't available" in content or status == 404:
                return f"✅ `{username}`"
        
        # --- فحص سوني الصارم ---
        elif platform == "SONY":
            if status == 404 or "error" in response.url.lower():
                return f"✅ `{username}`"

        # --- فحص X و تيك توك ---
        elif platform in ["X", "TIKTOK"]:
            if status == 404:
                return f"✅ `{username}`"

        return None
    except:
        return None

# --- بقية الكود (التوليد والقوائم) ---
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
    bot.send_message(message.chat.id, "🛰 **بوت الصيد الصارم | طلال**\n\nتم تحديث الفحص لمنع النتائج الوهمية ✅.", reply_markup=main_markup(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('p_'))
def select_filter(call):
    platform = call.data.split('_')[1]
    markup = types.InlineKeyboardMarkup(row_width=1)
    for l in ["3", "4", "5"]:
        markup.add(types.InlineKeyboardButton(f"تخمين عشوائي ({l}) أحرف", callback_data=f"g_{platform}_{l}"))
    markup.add(types.InlineKeyboardButton("⬅️ عودة", callback_data="back"))
    bot.edit_message_text(f"🎯 منصة: **{platform}**", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('g_'))
def execute_hunt(call):
    _, platform, length = call.data.split('_')
    bot.answer_callback_query(call.id, "🔎 جاري الفحص الصارم...")
    
    def worker(_):
        user = generate_username(length)
        return check_availability(platform, user)

    with ThreadPoolExecutor(max_workers=5) as executor: # تقليل السرعة قليلاً لزيادة الدقة وتجنب الحظر
        all_results = [res for res in executor.map(worker, range(10)) if res]
    
    if all_results:
        msg = f"🛰 **يوزرات متاح فعلياً لـ {platform}:**\n\n" + "\n".join(all_results)
    else:
        msg = f"🛰 **نتائج {platform}:**\n\nلم نجد متاحاً حقيقياً في هذه الدفعة. جرب مرة أخرى 🔄"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 صيد جديد", callback_data=call.data))
    markup.add(types.InlineKeyboardButton("🏠 القائمة", callback_data="back"))
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    bot.edit_message_text("🎯 اختر المنصة:", call.message.chat.id, call.message.message_id, reply_markup=main_markup())

if __name__ == "__main__":
    bot.infinity_polling()
