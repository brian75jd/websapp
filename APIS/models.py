from django.db import models
from django.utils import timezone
import secrets
from django.contrib.auth import get_user_model

User = get_user_model()

class League(models.Model):
    leage_name = models.CharField(max_length=300)

class Team(models.Model):
    name = models.CharField(max_length=300)
    short_hand = models.CharField(max_length=20,null=True,blank=True)

    def __str__(self):
        return self.name

class Match(models.Model):
    home_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,related_name='home_games'
    )
    away_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,related_name='away_games'
    )
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        related_name='matches'
    )
    home_team_scores = models.IntegerField(default=0,null=True,blank=True)
    away_team_scores = models.IntegerField(default=0,null=True,blank=True)
    data_played = models.DateTimeField()
    is_played = models.BooleanField(default=False)
    venue = models.CharField(max_length=300,null=True,blank=True)
    starting_time = models.DateTimeField(default=timezone.now)

    time_started = models.DateField()


    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name}"
    


class APIClient(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    api_key = models.CharField(max_length=300,unique=True)
    secret_key = models.CharField(max_length=300,unique=True)

    def save(self,*args, **kwargs):
        if not self.api_key:
            self.api_key = secrets.token_hex(15)
        
        if not self.secret_key:
            self.secret_key = secrets.token_hex(15)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.get_username()
