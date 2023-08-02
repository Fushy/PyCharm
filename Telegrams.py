import sys
from time import sleep
import traceback

import telegram
from telegram import Update, Bot
from telegram.error import NetworkError
from telegram.ext import CallbackContext, Updater, Dispatcher, MessageHandler, Filters, CommandHandler

from Files import get_first_line
import Threads

USER_IDS = {"ale": 1522961892}


def start(update: Update, context: CallbackContext):
    """This function is called every time the Bot receives the command "/start" """
    print(
        update.effective_user,
        update.effective_message.date.strftime("%Y-%m-%d %H:%M:%S"),
        update.effective_message.text, context.args)
    context.bot.send_message(chat_id=update.effective_user.id, text="You have started the bot.")


def echo(update: Update, context: CallbackContext):
    """This function is called every time the Bot receives a message (not a command) """
    print(
        update.effective_user,
        update.effective_message.date.strftime("%Y-%m-%d %H:%M:%S"),
        update.effective_message.text)
    context.bot.send_message(chat_id=update.effective_user.id, text=update.message.text)


def message(msg: str, to: str = None):
    """
    telegram.error.BadRequest: Chat not found
        First send a message to the bot before the bot can send messages to you
    """
    if to is None:
        id_to = USER_IDS["ale"]
    else:
        id_to = USER_IDS[to]
    # logging.basicConfig(date_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    api_key: str = get_first_line("B:\\_Documents\\APIs\\telegram_key")
    bot: Bot = telegram.Bot(token=api_key)
    updater: Updater = Updater(token=api_key, use_context=True)
    dispatcher: Dispatcher = updater.dispatcher
    echo_msg_handler: MessageHandler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_msg_handler)
    start_cmd_handler: CommandHandler = CommandHandler('start', start)
    dispatcher.add_handler(start_cmd_handler)
    try:
        bot.send_message(chat_id=id_to, text=msg)
    except NetworkError:
        print(traceback.format_exc(), file=sys.stderr)
        pass
        sleep(5)
    #     return message(msg, to)
    updater.start_polling()

    def aux():
        updater.stop()
        dispatcher.stop()
        sleep(10)

    Threads.run(aux)
    # Thread(target=aux).start()


if __name__ == '__main__':
    message("telegram message")
