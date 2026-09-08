from django.db import models


class Player(models.Model):
    """Football player used as a hidden word in Hangman."""

    name = models.CharField(max_length=120)
    # The puzzle word is a bare slug (e.g. "ronaldonazario") so it has no spaces
    # for the letter-guessing mechanic. display_name holds the real full name
    # ("Ronaldo Nazário") for the roster page and structured data — `name`
    # itself must never change or it breaks in-progress game sessions.
    display_name = models.CharField(max_length=120, blank=True, default='')
    age = models.IntegerField()
    position = models.CharField(max_length=80)
    number = models.IntegerField()
    first_club = models.CharField(max_length=120)
    current_club = models.CharField(max_length=120)

    class Meta:
        db_table = 'players'

    def __str__(self) -> str:
        return self.name
