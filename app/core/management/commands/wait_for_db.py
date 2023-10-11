"""
Django command to wait for the DATABASE to be available for connection.
"""
from django.core.management.base import BaseCommand
from psycopg2 import OperationalError as Psycopg2Error
from django.db.utils import OperationalError
import time


class Command(BaseCommand):
    """Django command for wait for database."""

    def handle(self, *args, **options):
        """Entry point for command"""
        self.stdout.write('Waiting for database...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])  # type: ignore
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write('Database Unavailable, waiting 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database Available!'))
