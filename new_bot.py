import html
import os
from flask import Flask, abort, request
import telebot
from telebot import types

# ==================== ESASY SAZLAMALAR ====================
TELEGRAM_TOKEN = "8862361317:AAG8NDX_Z1LKg0pbyfozcW0Cc0WiVFJSV80"
ADMIN_ID = 6640701495
ADMIN_USERNAME = "Jordiiin7"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask('')

RENDER_URL = os.environ.get('RENDER_EXTERNAL_URL')

# Satlyk VPN açarlaryň gory
vpn_keys_stock = {
    "1_month": [
        "vless://turkmenistan-v2ray-key-1-month-01@server.ip:443?encryption=none&security=tls#1 Aylyk Acar 01",
        "vless://turkmenistan-v2ray-key-1-month-02@server.ip:443?encryption=none&security=tls#1 Aylyk Acar 02",
    ],
    "3_months": [
        "vless://turkmenistan-v2ray-key-3-months-01@server.ip:443?encryption=none&security=tls#3 Aylyk Acar"
    ],
}

free_resources = {
    "free_vpn": [
        "vless://free-test-key-01@free.server.net:443?security=reality#Mugt Test VPN Acar"
    ],
    "mtproto_proxy": [
        "https://t.me/proxy?server=149.154.175.50&port=443&secret=ee1111111111111111111111111111111173332e676f6f676c652e636f6d"
    ],
}

admin_state = {}

# ==================== WEBHOOK ROUTE ====================


@app.route('/')
def home():
  return 'Bot Webhook rejiminde işjeň işleýär!'


@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
  if request.headers.get('content-type') == 'application/json':
    json_string = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '', 200
  else:
    abort(403)


# ==================== DÜWMELER ====================


def get_main_keyboard(user_id):
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
  btn_proxy = types.KeyboardButton("⚡️ Telegram MTProto Proxylar")
  btn_free = types.KeyboardButton("🎁 Mugt Açarlar (Free)")
  btn_buy = types.KeyboardButton("💳 VIP VPN Satyn al")
  btn_keys = types.KeyboardButton("🔑 Açarlarym")
  btn_profile = types.KeyboardButton("👤 Profil")
  btn_help = types.KeyboardButton("📖 Nädip birikmeli?")
  btn_support = types.KeyboardButton("💬 Goldaw / Admin")

  markup.add(btn_proxy, btn_free)
  markup.add(btn_buy, btn_keys)
  markup.add(btn_profile, btn_help)
  markup.add(btn_support)

  if user_id == ADMIN_ID:
    btn_admin = types.KeyboardButton("👑 Admin Panel")
    markup.add(btn_admin)

  return markup


# ==================== /START ====================


@bot.message_handler(commands=['start'])
def start_message(message):
  try:
    user = message.from_user
    safe_name = html.escape(user.first_name)
    keyboard = get_main_keyboard(user.id)
    welcome_text = (
        f"🌐 <b>Salam, {safe_name}!</b>\n\n"
        f"Türkmenistanyň internet şertlerinde durnukly we ýokary tizlikde"
        f" işleýän <b>V2Ray / VLESS / Outline / MTProto</b> hyzmatlaryna hoş"
        f" geldiňiz!\n\n🚀 Aşakdaky menýu arkaly islän hyzmatyňyzy saýlap"
        f" bilersiňiz:"
    )
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="HTML",
        reply_markup=keyboard,
    )
  except Exception as e:
    print(f" Ýalňyşlyk: {e}")


# ==================== /ADMIN ====================


@bot.message_handler(commands=['admin'])
def admin_command(message):
  if message.from_user.id != ADMIN_ID:
    bot.send_message(message.chat.id, "⚠️ Rugsat ýok!")
    return
  open_admin_panel(message.chat.id)


def open_admin_panel(chat_id):
  markup = types.InlineKeyboardMarkup(row_width=2)
  markup.add(
      types.InlineKeyboardButton(
          "➕ Satlyk açar goş", callback_data="adm_add_paid"
      ),
      types.InlineKeyboardButton(
          "🗑 Satlyk açarlary boz", callback_data="adm_del_paid"
      ),
      types.InlineKeyboardButton(
          "🎁 Mugt açar goş", callback_data="adm_add_free"
      ),
      types.InlineKeyboardButton(
          "🗑 Mugt açarlary boz", callback_data="adm_clear_free"
      ),
      types.InlineKeyboardButton(
          "🛡 Proxy goş", callback_data="adm_add_proxy"
      ),
      types.InlineKeyboardButton(
          "🗑 Proxylary boz", callback_data="adm_clear_proxy"
      ),
      types.InlineKeyboardButton(
          "📊 Baza hasabaty", callback_data="adm_stats"
      ),
  )
  bot.send_message(
      chat_id,
      "👑 <b>Admin Dolandyryş Paneli:</b>\n\nEdiljek amaly saýlaň:",
      parse_mode="HTML",
      reply_markup=markup,
  )


# ==================== MESSAGE HANDLER ====================


@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
  try:
    user_id = message.from_user.id
    text = message.text

    if user_id == ADMIN_ID and user_id in admin_state:
      state = admin_state[user_id]
      if state == "WAIT_ADD_PAID":
        vpn_keys_stock["1_month"].append(text)
        del admin_state[user_id]
        bot.send_message(message.chat.id, "✅ Satlyk açar goşuldy!")
        return
      elif state == "WAIT_ADD_FREE":
        free_resources["free_vpn"].append(text)
        del admin_state[user_id]
        bot.send_message(message.chat.id, "✅ Mugt açar goşuldy!")
        return
      elif state == "WAIT_ADD_PROXY":
        free_resources["mtproto_proxy"].append(text)
        del admin_state[user_id]
        bot.send_message(message.chat.id, "✅ Proxy goşuldy!")
        return

    if text == "⚡️ Telegram MTProto Proxylar":
      if free_resources["mtproto_proxy"]:
        proxy_url = free_resources["mtproto_proxy"][0]
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("⚡️ Proxy-ni Birikdir", url=proxy_url)
        )
        bot.send_message(
            message.chat.id,
            "🛡 <b>Mugt MTProto Proxy:</b>",
            parse_mode="HTML",
            reply_markup=markup,
        )
      else:
        bot.send_message(message.chat.id, "😔 Häzir proxy ýok.")

    elif text == "🎁 Mugt Açarlar (Free)":
      if free_resources["free_vpn"]:
        key = free_resources["free_vpn"][0]
        bot.send_message(
            message.chat.id, f"🎁 <b>Açar:</b>\n\n<code>{key}</code>", parse_mode="HTML"
        )
      else:
        bot.send_message(message.chat.id, "😔 Mugt açar ýok.")

    elif text == "💳 VIP VPN Satyn al":
      markup = types.InlineKeyboardMarkup(row_width=1)
      markup.add(
          types.InlineKeyboardButton(
              "📦 1 Aýlyk Açary Saýla", callback_data="buy_1m"
          ),
          types.InlineKeyboardButton(
              "📦 3 Aýlyk Açary Saýla", callback_data="buy_3m"
          ),
      )
      bot.send_message(
          message.chat.id,
          "🛒 <b>Tarifler:</b>",
          parse_mode="HTML",
          reply_markup=markup,
      )

    elif text == "🔑 Açarlarym":
      bot.send_message(message.chat.id, "🔑 Sizde işjeň açar ýok.")

    elif text == "👤 Profil":
      u = message.from_user
      bot.send_message(
          message.chat.id,
          f"👤 <b>Profil:</b>\nAdy: {u.first_name}\nID: <code>{u.id}</code>",
          parse_mode="HTML",
      )

    elif text == "📖 Nädip birikmeli?":
      bot.send_message(
          message.chat.id, "📖 v2rayNG programmasyny ulanmaly.", parse_mode="HTML"
      )

    elif text == "💬 Goldaw / Admin":
      markup = types.InlineKeyboardMarkup()
      markup.add(
          types.InlineKeyboardButton(
              "📞 Admina Ýaz", url=f"https://t.me/{ADMIN_USERNAME}"
          )
      )
      bot.send_message(message.chat.id, "💬 Soraglar boýunça:", reply_markup=markup)

    elif text == "👑 Admin Panel":
      if user_id == ADMIN_ID:
        open_admin_panel(message.chat.id)

  except Exception as e:
    print(f"Ýalňyşlyk: {e}")


# ==================== CALLBACKS ====================


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
  try:
    user_id = call.from_user.id
    data = call.data

    if data in ["buy_1m", "buy_3m"]:
      bot.send_message(
          call.message.chat.id,
          f"💳 Töleg üçin ýazyň: @{ADMIN_USERNAME}\nID: <code>{user_id}</code>",
          parse_mode="HTML",
      )
      bot.answer_callback_query(call.id)

    elif data.startswith("adm_"):
      if user_id != ADMIN_ID:
        return

      if data == "adm_stats":
        stats = f"📊 Sany: 1 aýlyk: {len(vpn_keys_stock['1_month'])}, Proxy: {len(free_resources['mtproto_proxy'])}"
        bot.send_message(call.message.chat.id, stats)
        bot.answer_callback_query(call.id)
      elif data == "adm_add_free":
        admin_state[user_id] = "WAIT_ADD_FREE"
        bot.send_message(call.message.chat.id, "Mugt açary ugradyň:")
        bot.answer_callback_query(call.id)
      elif data == "adm_clear_free":
        free_resources["free_vpn"] = []
        bot.send_message(call.message.chat.id, "Pozuldy!")
        bot.answer_callback_query(call.id)
      elif data == "adm_add_proxy":
        admin_state[user_id] = "WAIT_ADD_PROXY"
        bot.send_message(call.message.chat.id, "Proxy ugradyň:")
        bot.answer_callback_query(call.id)
      elif data == "adm_clear_proxy":
        free_resources["mtproto_proxy"] = []
        bot.send_message(call.message.chat.id, "Proksiler pozuldy!")
        bot.answer_callback_query(call.id)
      elif data == "adm_add_paid":
        admin_state[user_id] = "WAIT_ADD_PAID"
        bot.send_message(call.message.chat.id, "Satlyk açary ugradyň:")
        bot.answer_callback_query(call.id)
      elif data == "adm_del_paid":
        vpn_keys_stock["1_month"] = []
        bot.send_message(call.message.chat.id, "Pozuldy!")
        bot.answer_callback_query(call.id)
  except Exception as e:
    print(f"Ýalňyşlyk: {e}")


# ==================== RUN ====================
if __name__ == "__main__":
  if RENDER_URL:
    webhook_url = f"{RENDER_URL}/{TELEGRAM_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    print(f"Webhook guruldy: {webhook_url}")

  port = int(os.environ.get("PORT", 8080))
  app.run(host="0.0.0.0", port=port)
