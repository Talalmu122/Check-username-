import telebot
from telebot import types
import random
import string

# ضع التوكن الخاص بك هنا
API_TOKEN = 'YOUR_BOT_TOKEN'
bot = telebot.TeleBot(API_TOKEN)

# الحروف المستخدمة في التخمين
chars = string.ascii_lowercase + string.digits

def generate_user(filter_type):
    if filter_type == "3": # ثلاثي
        return ''.join(random.choices(chars, k=3))
    elif filter_type == "3s": # شبه ثلاثي (حرفين مكررين وثالث مختلف)
        c1 = random.choice(string.ascii_lowercase)
        c2 = random.choice(chars)
        return c1 + c1 + c2
    elif filter_type == "4": # رباعي
        return ''.join(random.choices(chars, k=4))
    elif filter_type == "4s": # شبه رباعي
        c1 = random.choice(string.ascii_lowercase)
        c2 = random.choice(chars)
        return c1 + c1 + c1 + c2
    elif filter_type == "5": # خماسي
        return ''.join(random.choices(chars, k=5))
    return None

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    platforms = [
        types.InlineKeyboardButton("Snapchat", callback_data="plat_snap"),
        types.InlineKeyboardButton("Twitter (X)", callback_data="plat_x"),
        types.InlineKeyboardButton("TikTok", callback_data="plat_tiktok"),
        types.InlineKeyboardButton("Instagram", callback_data="plat_insta"),
        types.InlineKeyboardButton("PlayStation", callback_data="plat_psn")
    ]
    markup.add(*platforms)
    bot.send_message(message.chat_id, "🎯 **مرحباً بك في بوت صيد اليوزرات**\n\nاختر المنصة التي تريد البدء بتخمين يوزراتها:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('plat_'))
def choose_filter(call):
    platform = call.data.split('_')[1]
    markup = types.InlineKeyboardMarkup(row_width=2)
    filters = [
        types.InlineKeyboardButton("ثلاثي", callback_data=f"go_{platform}_3"),
        types.InlineKeyboardButton("شبه ثلاثي", callback_data=f"go_{platform}_3s"),
        types.InlineKeyboardButton("رباعي", callback_data=f"go_{platform}_4"),
        types.InlineKeyboardButton("شبه رباعي", callback_data=f"go_{platform}_4s"),
        types.InlineKeyboardButton("خماسي", callback_data=f"go_{platform}_5"),
    ]
    markup.add(*filters)
    bot.edit_message_text(f"تم اختيار **{platform}**\nالآن اختر نوع الفلتر المطلوب:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('go_'))
def start_hunting(call):
    _, platform, filter_type = call.data.split('_')
    bot.answer_callback_query(call.id, "جاري بدء التخمين...")
    
    # هنا يتم توليد 5 يوزرات كمثال
    results = []
    for _ in range(5):
        user = generate_user(filter_type)
        results.append(f"`{user}`") # وضع اليوزر في كود ليسهل نسخه
    
    msg = f"✅ **نتائج التخمين لـ {platform} ({filter_type}):**\n\n"
    msg += "\n".join(results)
    msg += "\n\n⚠️ *ملاحظة: تأكد من فحص التوفر يدوياً أو عبر أداة Checker.*"
    
    bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")

bot.polling()
