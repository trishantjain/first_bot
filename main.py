import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from pymongo import MongoClient
from telegram import Update


client = MongoClient()
client = MongoClient("mongodb://localhost:27017/")
myDatabase = client["Order_list"]
mycollection = myDatabase["royale"]


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)
token = "6258989185:AAEzPzeOPue371Qbbsz15MHSDTlSfuM0WUI"
freshner_list = ["Bonanza", "Lemon", "Grapes", "Mint"]
ADDRESS, PHONE, FRESHNER_LIST, QUANTITY = range(4)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


# def order(update: Update, context):
#     user_id = update.message.from_user.id
#     context.user_data[user_id] = {}
#     context.user_data[user_id]['order_list'] = None

#     update.message.reply_text('''Please give order with name and its quantity.
# Name of room freshner - Quantity
# Address
# Phone Numbner

# Start your order with below line
# "Order Placement"
#     ''')


def start(update, context):
    update.message.reply_text('Hi! Give your address')
    return ADDRESS


def set_address(update, context):
    # global address
    user_name = update.message.from_user.first_name
    address = update.message.text
    context.user_data['address'] = address
    context.user_data['user_name'] = user_name
    update.message.reply_text("Please enter your phone number: ")
    return PHONE


def set_phone(update, context):
    global phone
    phone = update.message.text
    context.user_data['phone'] = phone
    update.message.reply_text("type /order to get list of Room freshners.")
    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text('Command canceled.')
    return ConversationHandler.END


def order(update, context):
    update.message.reply_text("Please select a freshner from the list or type /cancel to cancel the procedure." +
                              "\n".join(f"{i+1}, {freshner}" for i, freshner in enumerate(freshner_list)))
    return FRESHNER_LIST


def set_freshner(update, context):
    selected_freshner = update.message.text

    if selected_freshner.lower() == "/order":
        update.message.reply_text("Order Cancelled")
        return ConversationHandler.END
    

    context.user_data["selected_freshner"] = selected_freshner
    order_details = {
        "user_name": context.user_data.get('user_name'),
        "address": context.user_data.get('address'),
        "phone": context.user_data.get('phone'),
        'selected_freshner': context.user_data.get('selected_freshner')
    }
    mycollection.insert_one(order_details)
    update.message.reply_text(
        f"This is your order. \n{selected_freshner}")
    # return QUANTITY
    return ConversationHandler.END

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(
        token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ADDRESS: [MessageHandler(Filters.text, set_address)],
            PHONE: [MessageHandler(Filters.text, set_phone)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_handler2 = ConversationHandler(
        entry_points=[CommandHandler('order', order)],
        states={
            FRESHNER_LIST: [MessageHandler(Filters.text, set_freshner)],
            # QUANTITY: [MessageHandler(Filters.text, set_quantity)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(conv_handler2)

    # start the bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
