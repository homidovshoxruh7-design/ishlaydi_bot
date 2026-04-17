import telebot
from telebot import types
import sqlite3

# --- 1. SOZLAMALAR ---
TOKEN = "8419362381:AAER0Nws1WpL6zyfDVGJNFPa8q-Jvw9gTWM" 

# Kanallaringiz (Username-lar aynan shunday bo'lishi shart!)
KINO_USER = "Ishlaydi_Kino"
BOZOR_USER = "Ishlaydi_Bozor"

ADMIN_USER = "Zshoxruh"
REFS_NEEDED = 10 

bot = telebot.TeleBot(TOKEN)

# --- 2. BAZA ---
def init_db():
    conn = sqlite3.connect('ishlaydi_bot_main.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, invited_by INTEGER, ref_count INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def manage_user(user_id, referrer_id=None):
    conn = sqlite3.connect('ishlaydi_bot_main.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, invited_by) VALUES (?, ?)", (user_id, referrer_id))
        if referrer_id and int(referrer_id) != user_id:
            cursor.execute("UPDATE users SET ref_count = ref_count + 1 WHERE user_id = ?", (referrer_id,))
    conn.commit()
    conn.close()

def get_refs(user_id):
    conn = sqlite3.connect('ishlaydi_bot_main.db')
    cursor = conn.cursor()
    cursor.execute("SELECT ref_count FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else 0

init_db()

# --- 3. OBUNA TEKSHIRISH (PROFESSIONAL) ---
def check_sub_status(user_id, chat_id):
    try:
        member = bot.get_chat_member(f"@{chat_id}", user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return "✅"
        else:
            return "❌"
    except:
        return "❌"

# --- 4. ASOSIY MENU ---
def get_main_markup(user_id):
    s1 = check_sub_status(user_id, KINO_USER)
    s2 = check_sub_status(user_id, BOZOR_USER)
    refs = get_refs(user_id)
    s3 = "✅" if refs >= REFS_NEEDED else "❌"

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(f"{s1} 1-kanal (Kino)", url=f"https://t.me/{KINO_USER}"),
        types.InlineKeyboardButton(f"{s2} 2-kanal (Bozor)", url=f"https://t.me/{BOZOR_USER}"),
        types.InlineKeyboardButton(f"{s3} Do'stlar taklifi ({refs}/{REFS_NEEDED})", callback_data="ref_info"),
        types.InlineKeyboardButton("🔄 Tekshirish va Kirish", callback_data="check_all")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    args = message.text.split()
    ref = args[1] if len(args) > 1 and args[1].isdigit() else None
    
    manage_user(uid, ref)
    bot.send_message(message.chat.id, 
                     f"<b>Assalomu alaykum, {message.from_user.first_name}!</b>\n\nBotdan foydalanish uchun hamma belgilarni ✅ holatiga keltiring:", 
                     parse_mode="HTML", reply_markup=get_main_markup(uid))

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    uid = call.from_user.id
    
    if call.data == "check_all":
        s1 = check_sub_status(uid, KINO_USER)
        s2 = check_sub_status(uid, BOZOR_USER)
        refs = get_refs(uid)
        
        if s1 == "✅" and s2 == "✅" and refs >= REFS_NEEDED:
            # HAMMA SHART BAJARILDI - KINO REKLAMALARNI OCHAMIZ
            bot.edit_message_text(chat_id=call.message.chat.id, 
                                  message_id=call.message.message_id,
                                  text=f"🎉 <b>Tabriklaymiz!</b> Hamma shartlar bajarildi.\n\n👇 <b>Mana sizga kerakli kinolar va linklar:</b>\n1. [Kino Link 1]\n2. [Kino Link 2]\n\n<i>Hamkorlik: @{ADMIN_USER}</i>", 
                                  parse_mode="HTML")
        else:
            # SHARTLAR HALI TO'LIQ EMAS
            bot.answer_callback_query(call.id, "Hali hamma shartlar bajarilmadi!", show_alert=True)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_main_markup(uid))

    elif call.data == "ref_info":
        bot_info = bot.get_me()
        link = f"https://t.me/{bot_info.username}?start={uid}"
        bot.answer_callback_query(call.id, f"Sizga yana {REFS_NEEDED - get_refs(uid)} ta taklif kerak.", show_alert=True)

bot.infinity_polling()
