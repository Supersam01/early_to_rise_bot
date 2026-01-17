import random
import string
from datetime import datetime, timedelta
from typing import List
from .config import HOSTEL_PRIORITY, DELIVERY_WINDOW_MINUTES, PACKAGING_FEE_PER_ITEM
from .models import CartItem, MenuItem


def generate_reference_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def calculate_packaging_fee(num_items: int):
    return num_items * PACKAGING_FEE_PER_ITEM


def calculate_total(items: List[MenuItem], quantities: List[int]):
    total = 0
    for item, qty in zip(items, quantities):
        total += item.price * qty
    return total


def validate_combo(combo_type: str, liquid_count: int, solid_count: int):
    """
    Combo A: 1 liquid + 2 solids
    Combo B: 1 liquid + 1 solid
    """
    if combo_type == "A":
        return liquid_count == 1 and solid_count == 2
    if combo_type == "B":
        return liquid_count == 1 and solid_count == 1
    return False


def assign_time_slot(hostel: str, position: int):
    """
    Assign time slot based on hostel priority and order position.
    Each hostel gets a 10-minute window.
    """
    try:
        index = HOSTEL_PRIORITY.index(hostel)
    except ValueError:
        index = 0

    start_time = datetime.strptime("05:30", "%H:%M")
    start_time += timedelta(minutes=index * DELIVERY_WINDOW_MINUTES)

    end_time = start_time + timedelta(minutes=DELIVERY_WINDOW_MINUTES)
    return f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
