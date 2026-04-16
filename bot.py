import telebot
from telebot import types 
from telebot import types

# 1. BOT TOKENI
TOKEN = '8419362381:AAER0Nws1WpL6zyfDVGJNFPa8q-Jvw9gTWM'
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# 2. KANAL USERNAMELARI (@ belgisiz yozing)
KINO_USER = "Ishlaydi_Kino"   
BOZOR_USER = "Ishlaydi_Bozor" 

def get_status(user_id):
    """Har bir kanalni alohida tekshirib ✅ yoki ❌ qaytaradi"""
    res = {"k1": False, "k2": False}
    try:
        # 1-kanal tekshiruvi
        s1 = bot.get_chat_member(f"@{KINO_USER}", user_id).status
        res["k1"] = s1 in ['member', 'administrator', 'creator']
        
        # 2-kanal tekshiruvi
        s2 = bot.get_chat_member(f"@{BOZOR_USER}", user_id).status
        res["k2"] = s2 in ['member', 'administrator', 'creator']
    except Exception as e:
        # Agar xato bersa (masalan bot admin bo'lmasa) False qoladi
        print(f"Xatolik: {e}")
    return res

@bot.message_handler(commands=['start'])
def start(message):
    st = get_status(message.from_user.id)
    
    # Agar foydalanuvchi ikkalasiga ham a'zo bo'lgan bo'lsa
    if st["k1"] and st["k2"]:
        bot.send_message(message.chat.id, "🎉 <b>Xush kelibsiz!</b> Barcha obunalar tasdiqlandi. Botdan foydalanishingiz mumkin.")
    else:
        # Galichka tizimi bilan tugmalar yasash
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        txt1 = f"🎬 1-Kanal {'✅' if st['k1'] else '❌'}"
        txt2 = f"🛍 2-Guruh {'✅' if st['k2'] else '❌'}"
        
        btn1 = types.InlineKeyboardButton(txt1, url=f"https://t.me/{KINO_USER}")
        btn2 = types.InlineKeyboardButton(txt2, url=f"https://t.me/{BOZOR_USER}")
        btn3 = types.InlineKeyboardButton("🔄 TASDIQLASH", callback_data="recheck")
        
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, "🛑 <b>Bot yopiq!</b>\n\nDavom etish uchun ikkala kanalga ham obuna bo'ling va pastdagi tugmani bosing:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "recheck")
def recheck(call):
    st = get_status(call.from_user.id)
    
    if st["k1"] and st["k2"]:
        # Agar hammasi ✅ bo'lsa, xabarni o'chirib botni ochish
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "🎉 <b>Rahmat!</b> A'zoligingiz tasdiqlandi.")
    else:
        # KANALGA OTIB YUBORMAYDI! Faqat tepada ogohlantirish beradi
        bot.answer_callback_query(call.id, "❌ Siz hali barcha kanallarga a'zo emassiz!", show_alert=True)
        
        # Tugmalarni yangilash (biriga a'zo bo'lgan bo'lsa ✅ chiqishi uchun)
        markup = types.InlineKeyboardMarkup(row_width=1)
        txt1 = f"1-Kanal {'✅' if st['k1'] else '❌'}"
        txt2 = f"2-Guruh {'✅' if st['k2'] else '❌'}"
        markup.add(
            types.InlineKeyboardButton(txt1, url=f"https://t.me/{KINO_USER}"),
            types.InlineKeyboardButton(txt2, url=f"https://t.me/{BOZOR_USER}"),
            types.InlineKeyboardButton("🔄 TASDIQLASH", callback_data="recheck")
        )
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        except:
            pass

print("Bot yoqildi...")
bot.infinity_polling()
