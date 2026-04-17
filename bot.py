import telebot
from telebot import types
import sqlite3

# --- 1. SOZLAMALAR ---
# Siz bergan @Ishlaydi_bot tokeni
TOKEN = "8419362381:AAER0Nws1WpL6zyfDVGJNFPa8q-Jvw9gTWM" 

# Kanallaringiz usernamesi (@ belgisiz)
KINO_USER = "Ishlaydi_Kino"
BOZOR_USER = "Ishlaydi_Bozor"

# Admin va takliflar soni
ADMIN_USER = "Zshoxruh"
REFS_NEEDED = 10 
# ---------------------

bot = telebot.TeleBot(TOKEN)

# --- 2. MA'LUMOTLAR BAZASI ---
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

# --- 3. OBUNA TEKSHIRUVI ---
def check_sub(user_id):
    try:
        r1 = bot.get_chat_member(f"@{KINO_USER}", user_id)
        r2 = bot.get_chat_member(f"@{BOZOR_USER}", user_id)
        statuslar = ["creator", "administrator", "member"]
        return r1.status in statuslar and r2.status in statuslar
    except:
        return False

# --- 4. ASOSIY XABAR (SALOM BILAN) ---
def send_welcome(chat_id, user_id, name):
    refs = get_refs(user_id)
    bot_info = bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={user_id}"
    share = f"https://t.me/share/url?url={link}&text=Bu botda hamma yangi kinolar bor ekan, kirib ko'r! 🎬🚀"

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🎬 1-kanal (Kino)", url=f"https://t.me/{KINO_USER}"),
        types.InlineKeyboardButton("🛍 2-kanal (Bozor)", url=f"https://t.me/{BOZOR_USER}"),
        types.InlineKeyboardButton("🚀 Do'stlarimga yuborish", url=share),
        types.InlineKeyboardButton("👤 Reklama va hamkorlik", url=f"https://t.me/{ADMIN_USER}"),
        types.InlineKeyboardButton("🔄 Tekshirish", callback_data="check")
    )
    
    text = (f"<b>Assalomu alaykum, hurmatli {name}!</b> 👋\n\n"
            f"Botimizga xush kelibsiz! Botni faollashtirish uchun:\n\n"
            f"✅ Yuqoridagi 2 ta kanalga obuna bo'ling\n"
            f"✅ Botga kamida <b>{REFS_NEEDED} ta do'stingizni</b> taklif qiling\n\n"
            f"📊 Natijangiz: <b>{refs} / {REFS_NEEDED}</b>\n"
            f"📉 Yana <b>{max(0, REFS_NEEDED - refs)} ta</b> taklif kerak.\n\n"
            f"<i>Hamkorlik uchun @{ADMIN_USER} ga yozing.</i>")
    
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    args = message.text.split()
    ref = args[1] if len(args) > 1 and args[1].isdigit() else None
    
    manage_user(uid, ref)
    send_welcome(message.chat.id, uid, message.from_user.first_name)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def handle_check(call):
    uid = call.from_user.id
    name = call.from_user.first_name
    sub = check_sub(uid)
    refs = get_refs(uid)
    
    if sub and refs >= REFS_NEEDED:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, f"🎉 <b>Assalomu alaykum, {name}!</b>\nBarcha shartlar bajarildi. Bot endi ochiq!")
    else:
        status = (f"<b>Assalomu alaykum, {name}!</b> 👋\n\n"
                  f"⚠️ <b>Shartlar to'liq bajarilmagan:</b>\n"
                  f"{'✅' if sub else '❌'} Kanallarga obuna\n"
                  f"{'✅' if refs >= REFS_NEEDED else '❌'} Do'stlar: {refs}/{REFS_NEEDED}\n\n"
                  f"<i>Iltimos, shartlarni oxirigacha bajaring!</i>")
        
        bot.answer_callback_query(call.id, "Natija yetarli emas!", show_alert=False)
        try:
            bot.edit_message_text(status, call.message.chat.id, call.message.message_id, 
                                  parse_mode="HTML", reply_markup=call.message.reply_markup)
        except:
            pass

print("Ishlaydi_bot muvaffaqiyatli ishga tushdi...")
bot.infinity_polling()
