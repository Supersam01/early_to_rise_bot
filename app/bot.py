from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
from .config import BOT_TOKEN
from .handlers import start, combo_select, add_item, view_cart, clear_cart, back_menu, checkout, hostel_received
from .database import init_db

def main():
    init_db()

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            0: [CallbackQueryHandler(combo_select, pattern="^combo_")],
            1: [CallbackQueryHandler(add_item, pattern="^add_")],
            2: [CallbackQueryHandler(view_cart, pattern="^view_cart$"),
                CallbackQueryHandler(clear_cart, pattern="^clear_cart$"),
                CallbackQueryHandler(checkout, pattern="^checkout$"),
                CallbackQueryHandler(back_menu, pattern="^back_menu$")],
            3: [MessageHandler(Filters.text & ~Filters.command, hostel_received)]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

