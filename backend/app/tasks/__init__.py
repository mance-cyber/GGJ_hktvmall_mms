# Celery 任務模組
from app.tasks.celery_app import celery_app
from app.tasks.scrape_tasks import scrape_competitor, scrape_all_competitors, scrape_single_product

__all__ = [
    "celery_app",
    "scrape_competitor",
    "scrape_all_competitors",
    "scrape_single_product",
]
