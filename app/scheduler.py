from apscheduler.schedulers.background import BackgroundScheduler
import traceback
from datetime import datetime
import os


# def update_inventory():
#     from .data_base.models import Out_of_stock
#
#     return Out_of_stock.update_inventory_from_odoo(0)

# def counter_update():
#     counter = 0
#     print(datetime.now())
#
#     return print(f"Counter updated on {datetime.now()}")

def setup_scheduler(app):
    scheduler = BackgroundScheduler()

    # Wrap your scheduled function in a function that uses the app's context
    def update_inventory_with_app_context():
        with app.app_context():
            from .data_base.models import Out_of_stock
            return Out_of_stock.update_inventory_from_odoo(0)

    # Pass the function and its argument separately to add_job()
    interval_minutes = int(os.getenv('INTERVAL_MINUTES', 30))  # Use a default value of 30  if the environment variable is not set
    scheduler.add_job(update_inventory_with_app_context, 'interval', minutes=interval_minutes)
    scheduler.start()