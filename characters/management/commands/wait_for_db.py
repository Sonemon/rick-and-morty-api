import time

from django.core.management import BaseCommand
from django.db import connections
from psycopg2 import OperationalError


class Command(BaseCommand):
    """
    Command to wait for the database to be available.
    """

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections["default"]
            except OperationalError:
                self.stdout.write("Database unavailable, waiting 1 second...")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS("Database available!"))
