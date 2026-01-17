from dataclasses import dataclass
from typing import List, Optional

@dataclass
class MenuItem:
    id: int
    name: str
    price: int
    profit: int
    category: str  # liquid or solid
    stock: int

@dataclass
class CartItem:
    menu_item_id: int
    quantity: int
    combo_type: str  # A or B

@dataclass
class Order:
    id: int
    user_id: int
    username: str
    hostel: str
    combo_type: str
    items: List[CartItem]
    packaging_fee: int
    total_amount: int
    status: str  # pending, paid, delivered
    time_slot: str
    reference_code: str
