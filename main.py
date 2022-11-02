import logging
import json
import sqlite3
from random import choice as random_choice
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import *
from constants import *

logging.basicConfig(filename='molut_bot.log', encoding='utf-8',level=logging.INFO)

stickerset = None

def init_db():
    db_con = sqlite3.connect(DB_PATH)
    cur = db_con.cursor()
    res = cur.execute("SELECT name FROM sqlite_master")
    if res.fetchone() is None:
        db_con.cursor().execute("CREATE TABLE mokous(id, paikka, kaupunki, mindeksi)")
        db_con.commit()
        logging.info("Mokous database created")

def insert_to_db(place, city, mindeksi):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    res = cur.execute("SELECT COUNT(ALL) FROM mokous")
    count = res.fetchone()[0]
    cur.execute(f"""
        INSERT INTO mokous VALUES 
            ({count}, '{place.lower().strip()}', '{city.lower().strip()}', {mindeksi.lower().strip()})
    """)
    con.commit()
    logging.info(f"saved mokous ({count}, {place.lower().strip()}, {city.lower().strip()}, {mindeksi.lower().strip()}")

def get_from_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()    
    res = cur.execute("""
    SELECT * FROM mokous
    """)
    mokouslist = res.fetchall()
    print(mokouslist)
    return mokouslist

def get_filedata(path: str):
    try:
        with open(path, 'r') as rfile:
            data = rfile.read()
        logging.info(f"File {path} read successfully")
    except:
        logging.error(f"ERROR: No file found in {path}")
        return
    return data
 
def greet(update: Update, context: CallbackContext):
    global stickerset
    if not stickerset:
        stickerset = context.bot.get_sticker_set("molutpack")
        logging.info(f"stickerset {stickerset.title} get successful")
    rand_sticker = random_choice(stickerset.stickers)
    context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=rand_sticker)
    logging.info(f"greeted chat: {update.effective_chat.id} with sticker {rand_sticker.file_id}")

def help(update: Update, context: CallbackContext):
    msg = ""
    for command in COMMANDS.keys():
        msg += f"{command} - {COMMANDS[command]}\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

def mokous(update: Update, context: CallbackContext):
    arguments = context.args
    if ',' in arguments[-1]:
        arguments[-1] = arguments[-1][::-1].replace(',', '.', 1)[::-1]
    arguments = " ".join(arguments)
    arguments = [a.strip() for a in arguments.split(",")]
    if len(arguments) != 3:
        context.bot.send_message(chat_id=update.effective_chat.id, text="komennon ohje: /mokous paikka,kaupunki,mindeksi")
        return
    place, city, mindex = arguments
    insert_to_db(place=place, city=city, mindeksi=mindex)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Mokous tallennettu!")

def mokoukset(update: Update, context: CallbackContext):
    mokouslist = get_from_db()
    count = len(mokouslist)
    if count == 0:
        msg = "Ei tallennettuja mokouksia!"
    else:
        total = sum([float(m[3]) for m in mokouslist])
        avg = f"{(total/count):.02}"
        msg = f"Mokouksia yhteensä: {count}\nKeskiverto mindeksi: {avg}"
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
    

def juoma_command(key):
    if key == "mieto":
        maito = random_choice(MAITO)
        mieto = random_choice(MIEDOT)
        msg = f"{maito} + {mieto.strip()}\n= {maito[0] + mieto[1:]}"
    elif key == "kova":
        maito = random_choice(MAITO)
        kova = random_choice(KOVAT)
        msg = f"{maito} + {kova}\n= {maito[0] + kova[1:]}"
    elif key == "macktail":
        maito = random_choice(MAITO)
        mieto = random_choice(MIEDOT)
        kova = random_choice(KOVAT)
        msg = f"{maito} + {mieto.strip()} + {kova}\n= {maito[0] + mieto[1] + kova[2:]}"
    else:
        logging.error(f"invalid juoma button callback data: {key}")
        msg = "Fatal backend error :D"
    return msg

def button(update: Update, context: CallbackContext):
    query = json.loads(update.callback_query["data"])
    command = query['cmd']
    action = query['action']
    if command == "juoma":
        msg = juoma_command(action)
        update.callback_query.edit_message_text(f"{action} juoma:\n{msg}")
        logging.info(f"created drink:\n{msg}")
    else:
        logging.error("invalid button command")
        

def juoma(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Mieto", callback_data=json.dumps({"cmd": "juoma", "action": "mieto"}))],
        [InlineKeyboardButton("Kova", callback_data=json.dumps({"cmd": "juoma", "action": "kova"}))],
        [InlineKeyboardButton("Macktail", callback_data=json.dumps({"cmd": "juoma", "action": "macktail"}))]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Valitse juoma:", reply_markup=markup)

def ohjesaanto(update: Update, context: CallbackContext):
    if (update.effective_chat['type'] == update.effective_chat.PRIVATE):
        context.bot.send_message(chat_id=update.effective_chat.id, text=MOKOUS_TEXT)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=f"@{update.effective_user['username']} Mokousohjesääntö lähetetty yv:llä"
            )
        context.bot.send_message(chat_id=update.effective_user.id, text=MOKOUS_TEXT)

handlers = [
    CommandHandler('help', help),
    CommandHandler('ohjesaanto', ohjesaanto),
    CommandHandler('mokous', mokous),
    CommandHandler('mokoukset', mokoukset),
    CommandHandler('juoma', juoma, filters=Filters.chat_type.private),
    MessageHandler(Filters.status_update.new_chat_members, greet),
    CallbackQueryHandler(button),
]

if __name__ == '__main__':
    init_db()
    token = get_filedata("./token")
    updater = Updater(token)
    dispatcher = updater.dispatcher
    for handler in handlers:
        dispatcher.add_handler(handler)
    updater.start_polling()
    