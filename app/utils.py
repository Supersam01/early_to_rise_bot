from datetime import datetime, timedelta

def calculate_time_slot(order_index):
    """
    Calculates the delivery time slot based on the order index for a hostel.
    
    Rules:
    - Starts at 5:30 AM.
    - Windows are 10 minutes long.
    - Each window accommodates 15 orders.
    
    Example:
    Orders 0-14  (First 15) -> 5:30 AM - 5:40 AM
    Orders 15-29 (Next 15)  -> 5:40 AM - 5:50 AM
    ...
    Orders 135-149 (Last 15) -> 7:00 AM - 7:10 AM
    """
    
    # Base start time: 5:30 AM
    # We use a dummy date because we only care about the time
    base_time = datetime.strptime("05:30", "%H:%M")
    
    # Calculate which 10-minute window this order falls into
    # Integer division // 15 groups orders into batches of 15
    window_index = order_index // 15
    
    # Calculate the start time for this specific window
    # window_index * 10 minutes
    time_offset = timedelta(minutes=window_index * 10)
    
    slot_start = base_time + time_offset
    slot_end = slot_start + timedelta(minutes=10)
    
    # Format the time nicely (e.g., "05:30AM – 05:40AM")
    # %I is 12-hour format, %M is minutes, %p is AM/PM
    start_str = slot_start.strftime("%I:%M%p").lower()
    end_str = slot_end.strftime("%I:%M%p").lower()
    
    return f"{start_str} – {end_str}"
