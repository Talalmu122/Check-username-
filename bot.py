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

def check_availability(platform, username):
    # تم تحديث الروابط لمنطق أكثر دقة
    urls = {
        "INSTA": f"https://www.instagram.com/{username}/",
        "TIKTOK": f"https://www.tiktok.com/@{username}",
        "X": f"https://twitter.com/{username}",
        "SNAP": f"https://www.snapchat.com/add/{username}",
        "SONY": f"https://psnprofiles.com/{username}" # استخدام مرجع أدق لسوني
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    try:
        response = requests.get(urls[platform], headers=headers, timeout=10, allow_redirects=True)
        content = response.text
        status = response.status_code

        is_available = False

        # --- فحص سناب شات المطور ---
        if platform == "SNAP":
            # إذا لم يوجد نص "og:title" يحتوي على اسم المستخدم، فاليوزر متاح
            if f'property="og:title" content="{username}"' not in content and status == 404:
                is_available = True
        
        # --- فحص إنستقرام المطور ---
        elif platform == "INSTA":
            # إنستقرام يغير العنوان إلى "Instagram" فقط في صفحة الـ 404
            if "<title>Instagram</title>" in content or status == 404:
                is_available = True
        
        # --- فحص سوني (عبر PSNProfiles) ---
        elif platform == "SONY":
            # هذا الموقع يعطي 404 حقيقي إذا كان اليوزر غير موجود في قاعدة بيانات سوني
            if status == 404:
                is_available = True
        
        # --- فحص تيك توك ---
        elif platform == "TIKTOK":
            if "notfound" in response.url or status == 404:
                is_available = True

        # --- فحص X ---
        elif platform == "X":
            if status == 404:
                is_available = True

        if is_available:
            return f"✅ `{username}`"
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
    bot.send_message(message.chat.id, "🛰 **بوت الصيد المطور | الإصدار الأخير**\n\nتم تحديث روابط الفحص لتكون أكثر دقة ✅.", reply_markup=main_markup(), parse_mode="Markdown")

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
    bot.answer_callback_query(call.id, "🔎 جاري الفحص الدقيق...")
    
    def worker(_):
        user = generate_username(length)
        return check_availability(platform, user)

    # تقليل عدد المحاولات المتزامنة لضمان استقرار الاستجابة من المنصات
    with ThreadPoolExecutor(max_workers=5) as executor:
        all_results = [res for res in executor.map(worker, range(10)) if res]
    
    if all_results:
        msg = f"🛰 **يوزرات متاحة لـ {platform}:**\n\n" + "\n".join(all_results)
    else:
        msg = f"🛰 **نتائج {platform}:**\n\nلم يتم العثory على متاح مؤكد. جرب مجدداً 🔄"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 صيد جديد", callback_data=call.data))
    markup.add(types.InlineKeyboardButton("🏠 القائمة", callback_data="back"))
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    bot.edit_message_text("🎯 اختر المنصة:", call.message.chat.id, call.message.message_id, reply_markup=main_markup())

if __name__ == "__main__":
    bot.infinity_polling()
