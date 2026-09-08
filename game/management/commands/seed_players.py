import json

from django.core.management.base import BaseCommand

from game.models import Player

DATA_FILE = 'game/data/players.json'


class Command(BaseCommand):
    help = 'Seed the players table from game/data/players.json.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing players before insert.',
        )

    def handle(self, *args, **options):
        if options['reset']:
            deleted_count, _ = Player.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Removed {deleted_count} existing rows.'))

        with open(DATA_FILE, encoding='utf-8') as data_file:
            players = json.load(data_file)

        created_count = 0
        for payload in players:
            _, created = Player.objects.get_or_create(name=payload['name'], defaults=payload)
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Seed completed. Created: {created_count}.'))
