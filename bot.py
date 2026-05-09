import telebot
from telebot import types
import random
import string

# --- الإعدادات ---
API_TOKEN = 'ضع_توكن_بوتك_هنا'
bot = telebot.TeleBot(API_TOKEN)

# الحروف والأرقام المستخدمة في التخمين
CHARS = string.ascii_lowercase + string.digits

# --- دالة توليد اليوزرات حسب الفلتر ---
def generate_username(filter_type):
    if filter_type == "3": # ثلاثي
        return ''.join(random.choices(CHARS, k=3))
    elif filter_type == "3s": # شبه ثلاثي (حرف مكرر مرتين + حرف مختلف)
        c1 = random.choice(string.ascii_lowercase)
        c2 = random.choice(CHARS)
        return c1 + c1 + c2
    elif filter_type == "4": # رباعي
        return ''.join(random.choices(CHARS, k=4))
    elif filter_type == "4s": # شبه رباعي (حرف مكرر 3 مرات + حرف مختلف)
        c1 = random.choice(string.ascii_lowercase)
        c2 = random.choice(CHARS)
        return c1 + c1 + c1 + c2
    elif filter_type == "5": # خماسي
        return ''.join(random.choices(CHARS, k=5))
    return None

# --- التعامل مع أمر البداية ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    platforms = [
        types.InlineKeyboardButton("Snapchat", callback_data="p_snap"),
        types.InlineKeyboardButton("Twitter (X)", callback_data="p_x"),
        types.InlineKeyboardButton("TikTok", callback_data="p_tiktok"),
        types.InlineKeyboardButton("Instagram", callback_data="p_insta"),
        types.InlineKeyboardButton("PlayStation", callback_data="p_psn"),
        types.InlineKeyboardButton("Discord", callback_data="p_discord")
    ]
    markup.add(*platforms)
    
    welcome_text = (
        "🎯 **أهلاً بك في بوت تخمين اليوزرات**\n\n"
        "يرجى اختيار المنصة التي تريد تخمين يوزرات لها من القائمة أدناه:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

# --- اختيار الفلتر ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('p_'))
def select_filter(call):
    platform = call.data.split('_')[1].upper()
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    filters = [
        types.InlineKeyboardButton("ثلاثي", callback_data=f"g_{platform}_3"),
        types.InlineKeyboardButton("شبه ثلاثي", callback_data=f"g_{platform}_3s"),
        types.InlineKeyboardButton("رباعي", callback_data=f"g_{platform}_4"),
        types.InlineKeyboardButton("شبه رباعي", callback_data=f"g_{platform}_4s"),
        types.InlineKeyboardButton("خماسي", callback_data=f"g_{platform}_5")
    ]
    markup.add(*filters)
    # إضافة زر للعودة
    markup.add(types.InlineKeyboardButton("⬅️ عودة للمنصات", callback_data="back_to_start"))
    
    bot.edit_message_text(f"✅ تم اختيار: **{platform}**\nالآن اختر نوع الفلتر المطلوب:", 
                          call.message.chat.id, call.message.message_id, 
                          reply_markup=markup, parse_mode="Markdown")

# --- عملية التخمين وعرض النتائج ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('g_'))
def execute_guess(call):
    _, platform, f_type = call.data.split('_')
    
    # توليد قائمة من 10 يوزرات
    user_list = []
    for _ in range(10):
        u = generate_username(f_type)
        user_list.append(f"`{u}`")
    
    result_msg = (
        f"🚀 **نتائج التخمين لـ {platform}:**\n"
        f"نوع الفلتر: {f_type}\n\n"
        + "\n".join(user_list) +
        "\n\n"
        "💡 **نصيحة لليوزرات الخامله:**\n"
        "في حال كان اليوزر لشخص خامل، يمكنك محاولة مراسلة الدعم الفني للمنصة "
        "أو مراقبة الحساب حتى يتم حذفه تلقائياً من قبل المنصة."
    )
    
    # أزرار إضافية بعد التخمين
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 تخمين مجموعة أخرى", callback_data=call.data))
    markup.add(types.InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="back_to_start"))
    
    bot.edit_message_text(result_msg, call.message.chat.id, call.message.message_id, 
                          reply_markup=markup, parse_mode="Markdown")

# --- العودة للبداية ---
@bot.callback_query_handler(func=lambda call: call.data == "back_to_start")
def back_to_start(call):
    # إعادة استدعاء قائمة المنصات
    markup = types.InlineKeyboardMarkup(row_width=2)
    platforms = [
        types.InlineKeyboardButton("Snapchat", callback_data="p_snap"),
        types.InlineKeyboardButton("Twitter (X)", callback_data="p_x"),
        types.InlineKeyboardButton("TikTok", callback_data="p_tiktok"),
        types.InlineKeyboardButton("Instagram", callback_data="p_insta"),
        types.InlineKeyboardButton("PlayStation", callback_data="p_psn"),
        types.InlineKeyboardButton("Discord", callback_data="p_discord")
    ]
    markup.add(*platforms)
    bot.edit_message_text("🎯 اختر المنصة لبدء التخمين:", 
                          call.message.chat.id, call.message.message_id, 
                          reply_markup=markup)

# --- تشغيل البوت ---
print("البوت يعمل الآن...")
bot.infinity_polling()
