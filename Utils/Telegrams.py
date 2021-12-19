import Threads
import telegram

from time import sleep
from telegram import Update, Bot
from telegram.ext import CallbackContext, Updater, Dispatcher, MessageHandler, Filters, CommandHandler


def start(update: Update, context: CallbackContext):
    """This function is called every time the Bot receives the command "/start" """
    print(update.effective_user, update.effective_message.date.strftime("%Y-%m-%d %H:%M:%S"), update.effective_message.text, context.args)
    context.bot.send_message(chat_id=update.effective_user.id, text="You have started the bot.")


def echo(update: Update, context: CallbackContext):
    """This function is called every time the Bot receives a message (not a command) """
    print(update.effective_user, update.effective_message.date.strftime("%Y-%m-%d %H:%M:%S"), update.effective_message.text)
    context.bot.send_message(chat_id=update.effective_user.id, text=update.message.text)


def telegram_msg(msg: str, to: int = 1522961892):
    # user_id_ale_lg: int = 1522961892
    # pip install python-telegram-bot
    # logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    api_key: str = "1810940314:AAGLq3Z7SQ90GZMJWzDNS4enHR-QFg_sasw"
    bot: Bot = telegram.Bot(token=api_key)
    updater: Updater = Updater(token=api_key, use_context=True)
    dispatcher: Dispatcher = updater.dispatcher
    echo_msg_handler: MessageHandler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_msg_handler)
    start_cmd_handler: CommandHandler = CommandHandler('start', start)
    dispatcher.add_handler(start_cmd_handler)
    bot.send_message(chat_id=to, text=msg)
    updater.start_polling()

    def aux():
        updater.stop()
        dispatcher.stop()
        sleep(10)

    Threads.run(aux)
    # Thread(target=aux).start()
