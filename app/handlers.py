import uuid
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationType

# Import from your local files
from .config import (
    ADMIN_ID, START_DATE, END_DATE, HOSTELS, 
    PACKAGING_FEE, COMBO_CONFIG
)
from .database import (
    check_stock, reduce_stock, save_order, 
    get_order, update_order_paid, get_paid_count_for_hostel
)
from .utils import calculate_time_slot

# --- HELPER: CHECK IF BOT IS ACTIVE ---
def is_shop_open():
    now = datetime.now()
    
    # 1. Date Range Check
    if not (START_DATE <= now <= END_DATE):
        return False, "⚠️ We are currently closed.\nWe operate from Jan 18 to Feb 28."
    
    # 2. Sunday Check
    if now.weekday() == 6: # 0=Mon, 6=Sun
        return False, "⚠️ We are closed on Sundays.\nSee you on Monday!"
        
    return True, ""

# --- 1. START & HOSTEL SELECTION ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check Kill Switch
    is_open, msg = is_shop_open()
    if not is_open:
        await update.message.reply_text(msg)
        return

    # Reset User Session
    context.user_data.clear()
    context.user_data['cart'] = [] # Stores completed combos
    
    # Show Hostels
    keyboard = []
    # Create rows of 2 buttons for hostels
    row = []
    for hostel in HOSTELS:
        row.append(InlineKeyboardButton(hostel, callback_query_data=f"hostel_{hostel}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row: keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🍳 **Welcome to Early To Rise Breakfast Bot!**\n\n"
        "Please select your **Hostel** for delivery:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# --- 2. COMBO SELECTION ---
async def handle_hostel_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Save Hostel
    hostel_name = query.data.split("_")[1]
    context.user_data['hostel'] = hostel_name
    
    await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart_count = len(context.user_data.get('cart', []))
    
    text = (
        f"📍 Delivery to: **{context.user_data['hostel']}**\n"
        f"🛒 Cart: {cart_count} Combo(s)\n\n"
        "**Choose a Combo to build:**\n"
        "🅰️ **Combo A:** 1 Liquid + 2 Solids\n"
        "🅱️ **Combo B:** 1 Liquid + 1 Solid"
    )
    
    keyboard = [
        [InlineKeyboardButton("Build Combo A", callback_query_data="start_combo_A")],
        [InlineKeyboardButton("Build Combo B", callback_query_data="start_combo_B")]
    ]
    
    # Only show Checkout if cart is not empty
    if cart_count > 0:
        keyboard.append([InlineKeyboardButton(f"✅ Checkout ({cart_count} items)", callback_query_data="checkout")])
        keyboard.append([InlineKeyboardButton("❌ Clear Cart", callback_query_data="clear_cart")])
        
    await update.callback_query.edit_message_text(
        text, 
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode="Markdown"
    )

# --- 3. BUILDING A COMBO ---
async def start_combo_build(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    combo_type = query.data.split("_")[2] # "A" or "B"
    
    # Initialize Temporary Builder State
    context.user_data['builder'] = {
        'type': combo_type,
        'liquids': [], # List of names
        'solids': [],  # List of names
        'price': 0     # Running total for this combo
    }
    
    await refresh_builder_menu(update, context)

async def refresh_builder_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    builder = context.user_data['builder']
    c_type = builder['type']
    config = COMBO_CONFIG[c_type]
    
    req_liq = config['req_liquid']
    req_sol = config['req_solid']
    cur_liq = len(builder['liquids'])
    cur_sol = len(builder['solids'])
    
    # 1. Check if Combo is Complete
    if cur_liq == req_liq and cur_sol == req_sol:
        # Show Summary and "Add to Cart" button
        text = (
            f"✅ **Combo {c_type} Complete!**\n\n"
            f"🥤 Liquids: {', '.join(builder['liquids'])}\n"
            f"🥞 Solids: {', '.join(builder['solids'])}\n\n"
            "Add this to your cart?"
        )
        keyboard = [
            [InlineKeyboardButton("📥 Add to Cart", callback_query_data="commit_combo")],
            [InlineKeyboardButton("🔙 Cancel Combo", callback_query_data="cancel_combo")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # 2. If not complete, show selection menu
    text = (
        f"🔨 **Building Combo {c_type}**\n"
        f"({config['desc']})\n\n"
        f"🥤 Liquids: {cur_liq}/{req_liq}\n"
        f"🥞 Solids: {cur_sol}/{req_sol}\n\n"
        "Select an item to add:"
    )
    
    keyboard = []
    
    # Show Liquid Options if limit not reached
    if cur_liq < req_liq:
        keyboard.append([InlineKeyboardButton("--- LIQUIDS ---", callback_query_data="ignore")])
        for name, price in config['menu']['liquid'].items():
             keyboard.append([InlineKeyboardButton(f"{name} - ₦{price}", callback_query_data=f"add_liquid_{name}")])
             
    # Show Solid Options if limit not reached
    if cur_sol < req_sol:
        keyboard.append([InlineKeyboardButton("--- SOLIDS ---", callback_query_data="ignore")])
        for name, price in config['menu']['solid'].items():
             keyboard.append([InlineKeyboardButton(f"{name} - ₦{price}", callback_query_data=f"add_solid_{name}")])

    keyboard.append([InlineKeyboardButton("🔙 Cancel", callback_query_data="cancel_combo")])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def handle_item_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data # e.g., "add_liquid_Black Coffee"
    _, category, item_name = data.split("_", 2)
    
    # Stock Check
    if not check_stock(item_name):
        await query.answer(f"❌ Sorry, {item_name} is out of stock today!", show_alert=True)
        return
    
    builder = context.user_data['builder']
    c_type = builder['type']
    
    # Get Price
    price = COMBO_CONFIG[c_type]['menu'][category][item_name]
    
    # Update Builder
    if category == "liquid":
        builder['liquids'].append(item_name)
    else:
        builder['solids'].append(item_name)
        
    builder['price'] += price
    
    await query.answer(f"Added {item_name}")
    await refresh_builder_menu(update, context)

async def commit_combo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Combo added to cart!")
    
    # Move builder to cart
    context.user_data['cart'].append(context.user_data['builder'])
    del context.user_data['builder']
    
    # Return to main menu
    await show_main_menu(update, context)

async def cancel_combo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if 'builder' in context.user_data:
        del context.user_data['builder']
    await query.answer("Combo selection cancelled")
    await show_main_menu(update, context)

# --- 4. CART & CHECKOUT ---
async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cart'] = []
    await update.callback_query.answer("Cart cleared")
    await show_main_menu(update, context)

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    cart = context.user_data.get('cart', [])
    hostel = context.user_data.get('hostel')
    
    if not cart:
        await query.answer("Cart is empty!", show_alert=True)
        return

    # Calculate Totals
    items_total = sum(item['price'] for item in cart)
    packaging_total = len(cart) * PACKAGING_FEE
    grand_total = items_total + packaging_total
    
    # Generate Reference
    ref_code = str(uuid.uuid4())[:8].upper()
    
    # Prepare Order Data for DB
    items_summary = []
    receipt_text = "🧾 **ORDER SUMMARY**\n\n"
    
    all_items_flat_list = [] # For stock reduction
    
    for i, combo in enumerate(cart, 1):
        c_items = combo['liquids'] + combo['solids']
        all_items_flat_list.extend(c_items)
        
        line = f"**Combo {combo['type']}** (₦{combo['price']}):\n" + ", ".join(c_items)
        items_summary.append({"type": combo['type'], "items": c_items, "price": combo['price']})
        receipt_text += f"{i}. {line}\n\n"

    receipt_text += f"📦 Packaging Fee: ₦{packaging_total}\n"
    receipt_text += f"💰 **TOTAL TO PAY: ₦{grand_total}**\n"
    receipt_text += f"🔑 **REF CODE:** `{ref_code}`\n\n"
    
    receipt_text += (
        "**PAYMENT INSTRUCTIONS:**\n"
        "1. Transfer ₦{grand_total} to:\n"
        "   **Bank:** OPAY\n"
        "   **Acct:** 1234567890\n"
        "   **Name:** Early To Rise\n\n"
        "2. Include `{ref_code}` in the transfer description.\n"
        "3. Wait for Admin confirmation here."
    ).format(grand_total=grand_total, ref_code=ref_code)

    # SAVE TO DB
    save_order(
        user_id=update.effective_user.id,
        ref_code=ref_code,
        hostel=hostel,
        items_data=items_summary,
        total_price=grand_total
    )
    
    # REDUCE STOCK IMMEDIATELY (As per standard e-commerce reservation logic)
    reduce_stock(all_items_flat_list)
    
    # Notify Admin (Optional, but good for awareness)
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔔 **New Order Placed!**\nRef: `{ref_code}`\nHostel: {hostel}\nTotal: ₦{grand_total}",
            parse_mode="Markdown"
        )
    except:
        pass # If admin hasn't started bot, ignore

    await query.edit_message_text(receipt_text, parse_mode="Markdown")
    # Clear cart after order
    context.user_data['cart'] = []

# --- 5. ADMIN CONFIRMATION COMMAND ---
async def admin_confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Security Check
    if user_id != ADMIN_ID:
        return # Ignore non-admins silently

    try:
        ref_code = context.args[0].strip()
    except (IndexError, AttributeError):
        await update.message.reply_text("❌ Usage: /confirm <REF_CODE>")
        return

    order = get_order(ref_code)
    
    if not order:
        await update.message.reply_text("❌ Order not found.")
        return
        
    if order['status'] == 'PAID':
        await update.message.reply_text(f"⚠️ Order {ref_code} is already confirmed.")
        return

    # Calculate Time Slot
    hostel = order['hostel']
    
    # 1. Get how many people in this hostel have ALREADY paid today
    current_paid_count = get_paid_count_for_hostel(hostel)
    
    # 2. Calculate slot based on (count + 1)
    # The count returns previous orders. The current order is index = count.
    # e.g., if 0 exist, this is index 0 (1st order).
    time_slot = calculate_time_slot(current_paid_count)
    
    # Update DB
    update_order_paid(ref_code, time_slot)
    
    # Notify Admin
    await update.message.reply_text(f"✅ confirmed! Slot {time_slot} assigned to {hostel}.")
    
    # Notify User
    try:
        await context.bot.send_message(
            chat_id=order['user_id'],
            text=(
                f"🎉 **PAYMENT CONFIRMED!**\n\n"
                f"Order Ref: `{ref_code}`\n"
                f"Hostel: {hostel}\n"
                f"🚚 **Your Delivery Window:**\n"
                f"👉 **{time_slot}**\n\n"
                f"Please come out to the entrance at this time."
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Payment saved, but failed to msg user: {e}")

# --- HANDLER MAPPER (Used in bot.py) ---
# We will define the ConversationHandler or basic handlers in bot.py 
# but here are the callback functions ready to be imported.
