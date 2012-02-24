from django.db import models
from predictions.models import CommonInfo
import datetime

from django.conf import settings

class GameRound(CommonInfo):
    name = models.CharField(max_length=128)
    expire_at = models.DateTimeField(blank=True,null=True)
    expirable = models.BooleanField(default=True)
        
    def is_expired(self):
        if self.expirable and self.expire_at < datetime.datetime.now():
            return True
        return False
       
    def __unicode__(self):
        return self.name
    
class Game(CommonInfo):
    home_team = models.CharField(max_length=128)
    away_team = models.CharField(max_length=128)
    date = models.DateTimeField()
    game_round = models.ForeignKey('GameRound')
    result_home_regular_time = models.SmallIntegerField(blank=True,null=True)
    result_away_regular_time = models.SmallIntegerField(blank=True,null=True)

    def __unicode__(self):
        return "%s - %s vs %s" % (self.game_round.name, self.home_team, self.away_team)

    def has_player_predicted(self, player):
        prediction = GamePrediction.objects.filter(player=player,game=self)
        return True if prediction else False
    
    def get_player_predictions(self, player):
        return GamePrediction.objects.filter(player=player,game=self)
    
    def is_finished(self):
        return True if self.result_home_regular_time != None and self.result_away_regular_time != None else False
    
    def home_away_draw_result(self):
        if self.is_finished():
            if self.result_home_regular_time > self.result_away_regular_time:
                return settings.HOME_WIN
            else: 
                if self.result_home_regular_time < self.result_away_regular_time:
                    return settings.AWAY_WIN
            return settings.DRAW
        
        return False
    
class GamePrediction(CommonInfo):
    player = models.ForeignKey('player.Profile')
    game = models.ForeignKey('Game')
    home_score_regular_time = models.SmallIntegerField()
    away_score_regular_time = models.SmallIntegerField()
        
    def get_home_away_draw_guess(self):
        if self.home_score_regular_time > self.away_score_regular_time:
            return settings.HOME_WIN
        else: 
            if self.home_score_regular_time < self.away_score_regular_time:
                return settings.AWAY_WIN
        return settings.DRAW    
        
    def get_number_of_points(self):
        total_points = 0
        if self.game.is_finished():
            if self.get_home_away_draw_guess() == self.game.home_away_draw_result():
                total_points += settings.POINTS_CORRECT_RESULT
                if self.home_score_regular_time == self.game.result_home_regular_time:
                    total_points += settings.POINTS_CORRECT_ONE_OF_THE_SCORES
                if self.away_score_regular_time == self.game.result_away_regular_time:
                    total_points += settings.POINTS_CORRECT_ONE_OF_THE_SCORES
        return total_points
        
    def __unicode__(self):
        return "%s - %s - %s vs %s - %s:%s" % (self.game.game_round.name, self.player.user.username, self.game.home_team, self.game.away_team, self.home_score_regular_time, self.away_score_regular_time)