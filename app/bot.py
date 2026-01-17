import logging
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

# Import local modules
from app.config import BOT_TOKEN
from app.database import init_db
from app.handlers import (
    start,
    handle_hostel_selection,
    start_combo_build,
    handle_item_add,
    commit_combo,
    cancel_combo,
    clear_cart,
    checkout,
    admin_confirm_payment,
    show_main_menu
)

# Configure Logging (Helps debug issues)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Entry point for the bot."""
    
    # 1. Initialize the Database
    print("Initializing Database...")
    init_db()
    
    # 2. Build the Application
    print("Starting Bot...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # --- COMMAND HANDLERS ---
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("confirm", admin_confirm_payment))
    
    # --- CALLBACK QUERY HANDLERS (Button Clicks) ---
    
    # Hostel Selection (Pattern: "hostel_Dorcas", "hostel_Mary"...)
    application.add_handler(CallbackQueryHandler(handle_hostel_selection, pattern="^hostel_"))
    
    # Start Building Combo (Pattern: "start_combo_A", "start_combo_B")
    application.add_handler(CallbackQueryHandler(start_combo_build, pattern="^start_combo_"))
    
    # Add Item to Builder (Pattern: "add_liquid_Coffee", "add_solid_Pancakes"...)
    application.add_handler(CallbackQueryHandler(handle_item_add, pattern="^add_"))
    
    # Commit/Finish Combo
    application.add_handler(CallbackQueryHandler(commit_combo, pattern="^commit_combo$"))
    
    # Cancel Combo Building
    application.add_handler(CallbackQueryHandler(cancel_combo, pattern="^cancel_combo$"))
    
    # Clear Entire Cart
    application.add_handler(CallbackQueryHandler(clear_cart, pattern="^clear_cart$"))
    
    # Checkout
    application.add_handler(CallbackQueryHandler(checkout, pattern="^checkout$"))
    
    # Navigation / Ignore (Used for headers like "--- LIQUIDS ---")
    application.add_handler(CallbackQueryHandler(lambda u, c: u.callback_query.answer(), pattern="^ignore$"))

    # 3. Run the Bot
    print("Bot is running! Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == "__main__":
    main()
