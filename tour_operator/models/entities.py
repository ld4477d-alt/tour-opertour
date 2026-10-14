from dataclasses import dataclass
from datetime import date


@dataclass
class User:
    id: int | None
    username: str
    full_name: str
    role: str
    is_active: bool = True


@dataclass
class Tour:
    id: int | None
    title: str
    direction_id: int | None
    hotel_id: int | None
    date_start: date
    date_end: date
    price: float
    quota: int
    status: str = "Черновик"


@dataclass
class Client:
    id: int | None
    full_name: str
    phone: str = ""
    email: str = ""
    passport: str = ""


@dataclass
class Contract:
    id: int | None
    client_id: int
    tour_id: int
    manager_id: int | None
    status: str = "Оформлен"
    total: float = 0.0