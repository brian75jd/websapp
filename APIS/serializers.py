from rest_framework import serializers
from APIS.models import *

class TeamSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['name','short_hand']

class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = ['leage_name']


class MatchSerializer(serializers.ModelSerializer):
    home_team = TeamSeralizer(read_only=True)
    away_team = TeamSeralizer(read_only=True)
    league   = LeagueSerializer(read_only=True)
    

    class Meta:
        model = Match
        fields = ['home_team',
                  'away_team',
                  'league',
                  'is_played',
                  'time_started','away_team_scores','home_team_scores','venue']
