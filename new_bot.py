import html
import os
from threading import Thread
from flask import Flask
import telebot
from telebot import types

# ==================== RENDER SLEEP MODE ÖŇÜNI ALYŞ (FLASK SERVER) ====================
app = Flask('')


@app.route('/')
def home():
  return 'Bot 24/7 işjeň ýagdaýda!'


def run():
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)


def keep_alive():
  t = Thread(target=run)
  t.daemon = True
  t.start()


# ==================== ESASY SAZLAMALAR ====================
TELEGRAM_TOKEN = '8862361317:AAG3eBmVIc-Is1z8wBtx1VAsIRiScFkartw'
ADMIN_ID = 6640701495
ADMIN_USERNAME = 'Jordiiin7'

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Satlyk VPN açarlaryň gory
vpn_keys_stock = {
    '1_month': [
        (
            'vless://turkmenistan-v2ray-key-1-month-01@server.ip:443?encryption=none&security=tls#1'
            ' Aylyk Acar 01'
        ),
        (
            'vless://turkmenistan-v2ray-key-1-month-02@server.ip:443?encryption=none&security=tls#1'
            ' Aylyk Acar 02'
        ),
    ],
    '3_months': [
        (
            'vless://turkmenistan-v2ray-key-3-months-01@server.ip:443?encryption=none&security=tls#3'
            ' Aylyk Acar'
        )
    ],
}

# Mugt barlag (test) üçin açarlar we MTProto proksiler
free_resources = {
    'free_vpn': [
        (
            'vless://free-test-key-01@free.server.net:443?security=reality#Mugt'
            ' Test VPN Acar'
        )
    ],
    'mtproto_proxy': [
        'https://t.me/proxy?server=149.154.175.50&port=443&secret=ee1111111111111111111111111111111173332e676f6f676c652e636f6d'
    ],
}

admin_state = {}

# ==================== BAŞ MENÝU (DÜWMELER) ====================


def get_main_keyboard(user_id):
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

  btn_buy = types.KeyboardButton('🛒 Açar satyn al')
  btn_free = types.KeyboardButton('🎁 Mugt açarlar / Proxy')
  btn_keys = types.KeyboardButton('🔑 Açarlarym')
  btn_balance = types.KeyboardButton('💰 Balans')
  btn_profile = types.KeyboardButton('👤 Profil')
  btn_help = types.KeyboardButton('📖 Nädip birikmeli')
  btn_support = types.KeyboardButton('💬 Goldaw')

  markup.add(btn_buy, btn_free)
  markup.add(btn_keys, btn_balance)
  markup.add(btn_profile, btn_help)
  markup.add(btn_support)

  if user_id == ADMIN_ID:
    btn_admin = types.KeyboardButton('👑 Admin Panel')
    markup.add(btn_admin)

  return markup


# ==================== /START KOMANDASY ====================


@bot.message_handler(commands=['start'])
def start_message(message):
  try:
    user = message.from_user
    print(
        f'🟢 [TÄZE ULANYJY]: {user.first_name} (ID: {user.id}) bota /start'
        ' basdy!'
    )

    safe_name = html.escape(user.first_name)
    keyboard = get_main_keyboard(user.id)

    welcome_text = (
        f'🌐 <b>Salam, {safe_name}!</b>\n\n'
        'Türkmenistanyň internet şertlerinde durnukly we ýokary tizlikde'
        ' işleýän <b>V2Ray / VLESS / Outline / MTProto</b> hyzmatlaryna hoş'
        ' geldiňiz!\n\n🚀 Aşakdaky menýu arkaly islän hyzmatyňyzy saýlap'
        ' bilersiňiz:'
    )
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode='HTML',
        reply_markup=keyboard,
    )
  except Exception as e:
    print(f'❌ Ýalňyşlyk /start-da: {e}')


# ==================== /ADMIN KOMANDASY ====================


@bot.message_handler(commands=['admin'])
def admin_command(message):
  if message.from_user.id != ADMIN_ID:
    bot.send_message(
        message.chat.id, '⚠️ Bu komanda diňe admin üçin elýeterli!'
    )
    return
  open_admin_panel(message.chat.id)


def open_admin_panel(chat_id):
  markup = types.InlineKeyboardMarkup(row_width=2)
  markup.add(
      types.InlineKeyboardButton(
          '➕ Satlyk açar goş', callback_data='adm_add_paid'
      ),
      types.InlineKeyboardButton(
          '🗑 Satlyk açarlary boz', callback_data='adm_del_paid'
      ),
      types.InlineKeyboardButton(
          '🎁 Mugt açar goş', callback_data='adm_add_free'
      ),
      types.InlineKeyboardButton(
          '🗑 Mugt açarlary boz', callback_data='adm_clear_free'
      ),
      types.InlineKeyboardButton(
          '📊 Baza hasabaty', callback_data='adm_stats'
      ),
  )
  bot.send_message(
      chat_id,
      '👑 <b>Admin Dolandyryş Paneli:</b>\n\nEdiljek amaly saýlaň:',
      parse_mode='HTML',
      reply_markup=markup,
  )


# ==================== MENÝU WE DÜWMELERI IŞLEDİŞ ====================


@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
  try:
    user_id = message.from_user.id
    text = message.text
    print(f'📩 [HAT]: {message.from_user.first_name}: {text}')

    # Eger admin maglumat girizýän bolsa
    if user_id == ADMIN_ID and user_id in admin_state:
      state = admin_state[user_id]
      if state == 'WAIT_ADD_PAID':
        vpn_keys_stock['1_month'].append(text)
        del admin_state[user_id]
        bot.send_message(
            message.chat.id, '✅ Täze 1 aýlyk satlyk açar baza goşuldy!'
        )
        return
      elif state == 'WAIT_ADD_FREE':
        if text.startswith('https://t.me/proxy'):
          free_resources['mtproto_proxy'].append(text)
          bot.send_message(
              message.chat.id, '✅ Täze Telegram MTProto proxy goşuldy!'
          )
        else:
          free_resources['free_vpn'].append(text)
          bot.send_message(
              message.chat.id, '✅ Täze mugt synag açary goşuldy!'
          )
        del admin_state[user_id]
        return

    if text == '🛒 Açar satyn al':
      markup = types.InlineKeyboardMarkup(row_width=1)
      markup.add(
          types.InlineKeyboardButton(
              '📦 1 Aýlyk Açary Saýla', callback_data='buy_1m'
          ),
          types.InlineKeyboardButton(
              '📦 3 Aýlyk Açary Saýla', callback_data='buy_3m'
          ),
      )
      bot.send_message(
          message.chat.id,
          '🛒 <b>VPN Açar Tariflerini Saýlaň:</b>\n\n'
          '• 1 Aýlyk Premium Açar\n'
          '• 3 Aýlyk Premium Açar (Amatly baha)\n\n'
          'Açarlar ýörite optimizirlenen we çäklendirmesiz işleýär.',
          parse_mode='HTML',
          reply_markup=markup,
      )

    elif text == '🎁 Mugt açarlar / Proxy':
      markup = types.InlineKeyboardMarkup(row_width=1)
      markup.add(
          types.InlineKeyboardButton(
              '🚀 Mugt Synag VPN Açary', callback_data='get_free_vpn'
          ),
          types.InlineKeyboardButton(
              '🛡 Telegram MTProto Proxy', callback_data='get_free_proxy'
          ),
      )
      bot.send_message(
          message.chat.id,
          '🎁 <b>Mugt Barlag Bölümi:</b>\n\n'
          'Serwerlerimizi ilki barlap görmek üçin aşakdakylardan birini'
          ' saýlaň:',
          parse_mode='HTML',
          reply_markup=markup,
      )

    elif text == '🔑 Açarlarym':
      bot.send_message(
          message.chat.id,
          '🔑 <b>Meniň Açarlarym:</b>\n\nSizde häzirki wagtda satyn alnan'
          ' işjeň açar ýok.',
          parse_mode='HTML',
      )

    elif text == '💰 Balans':
      bot.send_message(
          message.chat.id,
          '💰 <b>Siziň Balansyňyz:</b> <code>0.00 TMT</code>\n\nBalansy'
          ' doldurmak üçin admina ýüz tutuň.',
          parse_mode='HTML',
      )

    elif text == '👤 Profil':
      u = message.from_user
      uname = f'@{u.username}' if u.username else 'Görkezilmedik'
      profile_text = (
          f'👤 <b>Siziň Profiliňiz:</b>\n\n'
          f'• Adyňyz: {html.escape(u.first_name)}\n'
          f'• Telegram ID: <code>{u.id}</code>\n'
          f'• Username: {uname}\n'
          f'• Hasap derejesi: Standart ulanyjy'
      )
      bot.send_message(message.chat.id, profile_text, parse_mode='HTML')

    elif text == '📖 Nädip birikmeli':
      guide_text = (
          '📖 <b>Nädip birikmeli we ulanmaly?</b>\n\n'
          '1. Telefonyňyza <b>v2rayNG</b> (Android) ýa-da <b>Streisand /'
          ' FoXray</b> (iPhone) programmasyny ýükläň.\n'
          '2. Botdan alan açaryňyzy göçürip (kopirowat edip) alyň.\n'
          '3. Programmany açyň we <b>+</b> (goşmak) basyp, <i>Import from'
          ' clipboard</i> saýlaň.\n'
          '4. Aşakdaky birikme düwmesine basyň!'
      )
      bot.send_message(message.chat.id, guide_text, parse_mode='HTML')

    elif text == '💬 Goldaw':
      markup = types.InlineKeyboardMarkup()
      markup.add(
          types.InlineKeyboardButton(
              '📞 Administratora Ýaz', url=f'https://t.me/{ADMIN_USERNAME}'
          )
      )
      bot.send_message(
          message.chat.id,
          f'💬 Islendik sorag ýa-da töleg boýunça @{ADMIN_USERNAME} ýüz tutup'
          ' bilersiňiz:',
          reply_markup=markup,
      )

    elif text == '👑 Admin Panel':
      if user_id != ADMIN_ID:
        bot.send_message(message.chat.id, '⚠️ Bu düwme diňe admin üçin!')
        return
      open_admin_panel(message.chat.id)

  except Exception as e:
    print(f'❌ Ýalňyşlyk düwmelerde: {e}')


# ==================== INLINE DÜWMELER (CALLBACKS) ====================


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
  try:
    user_id = call.from_user.id
    data = call.data

    if data == 'get_free_vpn':
      if free_resources['free_vpn']:
        key = free_resources['free_vpn'][0]
        msg = (
            '🎁 <b>Mugt Synag VPN Açaryňyz:</b>\n\n'
            f'<code>{html.escape(key)}</code>\n\n'
            '<i>(Göçürip almak üçin açaryň üstüne basyň)</i>'
        )
      else:
        msg = (
            '😔 Häzirki wagtda elýeterli mugt açar ýok. Soňrak synanyşyp'
            ' görüň!'
        )
      bot.send_message(call.message.chat.id, msg, parse_mode='HTML')
      bot.answer_callback_query(call.id)

    elif data == 'get_free_proxy':
      if free_resources['mtproto_proxy']:
        proxy_url = free_resources['mtproto_proxy'][0]
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('⚡️ Proxy-ni Birikdir', url=proxy_url)
        )
        bot.send_message(
            call.message.chat.id,
            '🛡 <b>Telegram üçin Mugt MTProto Proxy:</b>\n\nAşakdaky düwmä'
            ' basyp göni birigiň:',
            reply_markup=markup,
        )
      else:
        bot.send_message(
            call.message.chat.id, '😔 Häzirki wagtda mugt proxy ýok.'
        )
      bot.answer_callback_query(call.id)

    elif data in ['buy_1m', 'buy_3m']:
      bot.send_message(
          call.message.chat.id,
          '💳 Töleg etmek we açary almak üçin administratora ýazyň:'
          f' @{ADMIN_USERNAME}\n\n'
          f'Siziň Telegram ID belgiňiz: <code>{user_id}</code>',
          parse_mode='HTML',
      )
      bot.answer_callback_query(call.id)

    elif data.startswith('adm_'):
      if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, 'Rugsat ýok!')
        return

      if data == 'adm_stats':
        stats = (
            '📊 <b>Bazadaky açarlaryň sany:</b>\n\n'
            f"• Satlyk (1 aýlyk): {len(vpn_keys_stock['1_month'])} sany\n"
            f"• Satlyk (3 aýlyk): {len(vpn_keys_stock['3_months'])} sany\n"
            f"• Mugt VPN açarlar: {len(free_resources['free_vpn'])} sany\n"
            f"• Mugt MTProto proksiler:"
            f" {len(free_resources['mtproto_proxy'])} sany"
        )
        bot.send_message(call.message.chat.id, stats, parse_mode='HTML')
        bot.answer_callback_query(call.id)

      elif data == 'adm_add_free':
        admin_state[user_id] = 'WAIT_ADD_FREE'
        bot.send_message(
            call.message.chat.id,
            '📝 Täze mugt açary (vless://...) ýa-da MTProto proxy linkini'
            ' (https://t.me/proxy?...) şu ýere ugradyň:',
        )
        bot.answer_callback_query(call.id)

      elif data == 'adm_clear_free':
        free_resources['free_vpn'] = []
        free_resources['mtproto_proxy'] = []
        bot.send_message(
            call.message.chat.id, '🗑 Ähli mugt açarlar we proksiler pozuldy!'
        )
        bot.answer_callback_query(call.id)

      elif data == 'adm_add_paid':
        admin_state[user_id] = 'WAIT_ADD_PAID'
        bot.send_message(
            call.message.chat.id,
            '📝 Täze satlyk 1 aýlyk açary (vless://...) ugradyň:',
        )
        bot.answer_callback_query(call.id)

      elif data == 'adm_del_paid':
        vpn_keys_stock['1_month'] = []
        vpn_keys_stock['3_months'] = []
        bot.send_message(
            call.message.chat.id, '🗑 Ähli satlyk açarlar pozuldy!'
        )
        bot.answer_callback_query(call.id)

  except Exception as e:
    print(f'❌ Ýalňyşlyk callback-de: {e}')


# ==================== BOTY DURNUKLY IŞLETMEK ====================
if __name__ == '__main__':
  print('==================================================')
  print('🚀 Bot üstünlikli işläp başlady (Türkmen dilinde)!')
  print('==================================================')

  # Render serweri üçin port ugratmak
  keep_alive()

  # Konflikt ýalňyşlyklarynyň öňüni alyş
  try:
    bot.remove_webhook()
  except Exception as e:
    print(f'Webhook arassalandy: {e}')

  # Siziň original infinity_polling funksiýaňyz
  bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
