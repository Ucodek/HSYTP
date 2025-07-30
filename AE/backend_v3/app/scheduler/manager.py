from fastapi import FastAPI
from fastcore.config.base import BaseAppSettings

from .scheduler import Scheduler


def setup_scheduler(app: FastAPI, settings: BaseAppSettings) -> None:
    """
    Setup the scheduler with the necessary configurations.
    """
    scheduler_manager = Scheduler(settings.ALEMBIC_DATABASE_URL)  # sync db_url

    # Register scheduled jobs using persistent function string references
    async def on_startup():
        scheduler_manager.start()
        # INDICES
        scheduler_manager.add_job(
            "app.scheduler.tasks.indices_tasks:create_market_indices",
            "cron",
            # from monday to friday at 9:00 AM
            day_of_week="mon-fri",
            hour=9,
            minute=0,
            id="create_market_indices",
        )
        scheduler_manager.add_job(
            "app.scheduler.tasks.prices_tasks:update_index_prices",
            "interval",
            # every 15 minutes
            minutes=15,
            id="update_index_prices",
        )
        scheduler_manager.add_job(
            "app.scheduler.tasks.prices_tasks:backfill_index_price_history",
            "cron",
            # January and July at 6:00 AM on Sundays
            month="1,7",
            day_of_week="sun",
            hour=6,
            minute=0,
            id="backfill_index_price_history",
        )
        # STOCKS
        scheduler_manager.add_job(
            "app.scheduler.tasks.stocks_tasks:create_market_stocks",
            "cron",
            # at 3:00 AM on Sundays
            day_of_week="sun",
            hour=5,
            minute=0,
            id="create_market_stocks",
        )
        scheduler_manager.add_job(
            "app.scheduler.tasks.prices_tasks:update_stock_prices",
            "interval",
            # every 15 minutes
            minutes=15,
            id="update_stock_prices",
        )
        scheduler_manager.add_job(
            "app.scheduler.tasks.prices_tasks:backfill_stock_price_history",
            "cron",
            # January and July at 3:00 AM on Sundays
            month="1,7",
            day_of_week="sun",
            hour=7,
            minute=0,
            id="backfill_stock_price_history",
        )

        # scheduler_manager.remove_job("create_market_indices")
        # scheduler_manager.remove_job("update_index_prices")
        # scheduler_manager.remove_job("backfill_index_price_history")
        # scheduler_manager.remove_job("create_market_stocks")
        # scheduler_manager.remove_job("update_stock_prices")
        # scheduler_manager.remove_job("backfill_stock_price_history")

    app.add_event_handler("startup", on_startup)
    app.add_event_handler("shutdown", scheduler_manager.shutdown)
