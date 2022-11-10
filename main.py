import logging
import json
from utils import *
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import *
from constants import *


logging.basicConfig(filename='molut_bot.log', encoding='utf-8',level=logging.INFO)

stickerset = None
 
def greet(update: Update, context: CallbackContext):
    """Greeting functionality handler

    Args:
        update (Update): telegram client update
        context (CallbackContext): telegram context
    """
    global stickerset
    if not stickerset:
        stickerset = context.bot.get_sticker_set("molutpack")
        logging.info(f"stickerset {stickerset.title} get successful")
    
    rand_sticker = random_choice(stickerset.stickers)
    context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=rand_sticker)
    logging.info(f"greeted chat: {update.effective_chat.id} with sticker {rand_sticker.file_id}")


def help(update: Update, context: CallbackContext):
    """Help functionality handler

    Args:
        update (Update): telegram client update
        context (CallbackContext): telegram context
    """

    msg = ""
    for command in COMMANDS.keys():
        msg += f"{command} - {COMMANDS[command]}\n"
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
    logging.info(f"provided help to chat: {update.effective_chat.id}")


def meeting(update: Update, context: CallbackContext):
    """Meeting functionality handler

    Args:
        update (Update): telegram client update
        context (CallbackContext): telegram context
    """
    arguments = "".join(context.args)
    if (arguments.count(",") not in range(1,3)):
        logging.warning(f"weird arguments given to /mokous: {context.args}")
        context.bot.send_message(chat_id=update.effective_chat.id, text="komennon ohje: /mokous paikka,mindeksi")
        return
    if arguments.count(",") == 2:
        last_colon_i = arguments.rfind(",")
        print(last_colon_i)
        arglist = list(arguments)
        arglist[last_colon_i] = "."
        arguments = "".join(arglist)
    arguments = [a.strip() for a in arguments.split(",")]

    if len(arguments) != 2:
        logging.warning(f"wrong number of arguments given to /mokous: {context.args}")
        context.bot.send_message(chat_id=update.effective_chat.id, text="komennon ohje: /mokous paikka,mindeksi")
        return

    place, mindex = arguments

    if insert_to_db(place=place, mindeksi=mindex):
        logging.info(f"inserted mokous to database with place: {place} + mindex: {mindex}")
        context.bot.send_message(chat_id=update.effective_chat.id, text="Mokous tallennettu!")
        return

    logging.info(f"declined inserting mokous with place: {place} + mindex: {mindex}")
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hyi!")


def meetings(update: Update, context: CallbackContext):
    """Meeting summary functionality handler

    Args:
        update (Update): telegram client update
        context (CallbackContext): telegram context
    """
    mokouslist = get_from_db()
    count = len(mokouslist)
    if count == 0:
        msg = "Ei tallennettuja mokouksia!"
    else:
        total = sum([float(m[2]) for m in mokouslist])
        avg = f"{(total/count):.02}"
        msg = f"Mokouksia yhteensä: {count}\nKeskiverto mindeksi: {avg}"
    logging.info(f"sent mokous summary ({msg}) to chat: {update.effective_chat.id}")
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def button(update: Update, context: CallbackContext):
    """Button functionality handler

    Args:
        update (Update): telegram client update
        context (CallbackContext): telegram context
    """
    query = json.loads(update.callback_query["data"])
    command = query['cmd']
    action = query['action']
    if command == "juoma":
        msg = drink_command(action)
        update.callback_query.edit_message_text(f"{action} juoma:\n{msg}")
        logging.info(f"created drink: {msg} for user: {update.effective_chat.id}")
    else:
        logging.error("invalid button command")   


def drink(update: Update, context: CallbackContext):
    """Drink generator functionality handler

    Args:
        update (Update): telegram client update
        context (CallbackContext): telegram context
    """

    keyboard = [
        [InlineKeyboardButton("Mieto", callback_data=json.dumps({"cmd": "juoma", "action": "mieto"}))],
        [InlineKeyboardButton("Kova", callback_data=json.dumps({"cmd": "juoma", "action": "kova"}))],
        [InlineKeyboardButton("Macktail", callback_data=json.dumps({"cmd": "juoma", "action": "macktail"}))]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Valitse juoma:", reply_markup=markup)


def guidelines(update: Update, context: CallbackContext):
    """Guidelines command handler

    Args:
        update (Update): telegram client update
        context (CallbackContext): telegram context
    """
    logging.info(f"sent guidelines to chat: {update.effective_chat.id}")
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
    CommandHandler('ohjesaanto', guidelines),
    CommandHandler('mokous', meeting),
    CommandHandler('mokoukset', meetings),
    CommandHandler('kirottu', drink, filters=Filters.chat_type.private),
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
    