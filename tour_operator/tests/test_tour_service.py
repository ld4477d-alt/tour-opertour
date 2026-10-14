from datetime import date
import pytest

from db.database import Database
from models.entities import Tour
from services.tour_service import TourService


@pytest.fixture(autouse=True)
def clean_db():
    Database.init_schema()
    conn = Database.connect()
    with conn.cursor() as cur:
        cur.execute(
            "TRUNCATE contracts, tours, clients RESTART IDENTITY CASCADE"
        )
    conn.commit()
    yield
    conn = Database.connect()
    with conn.cursor() as cur:
        cur.execute(
            "TRUNCATE contracts, tours, clients RESTART IDENTITY CASCADE"
        )
    conn.commit()


def test_create_and_list_tour():
    service = TourService()
    pk = service.save(Tour(
        id=None, title="Тестовый тур", direction_id=None, hotel_id=None,
        date_start=date(2027, 1, 1), date_end=date(2027, 1, 10),
        price=50000, quota=10, status="Активен",
    ))
    assert pk > 0
    tours = service.list_tours()
    assert len(tours) == 1
    assert tours[0].title == "Тестовый тур"


def test_search_tour():
    service = TourService()
    service.save(Tour(None, "Сочи", None, None,
                      date(2027, 1, 1), date(2027, 1, 5), 30000, 5))
    service.save(Tour(None, "Казань", None, None,
                      date(2027, 2, 1), date(2027, 2, 5), 20000, 5))
    result = service.search("сочи")
    assert len(result) == 1
    assert result[0].title == "Сочи"


def test_delete_tour():
    service = TourService()
    pk = service.save(Tour(None, "Удаляемый", None, None,
                           date(2027, 1, 1), date(2027, 1, 5), 1000, 1))
    service.delete(pk)
    assert service.list_tours() == []