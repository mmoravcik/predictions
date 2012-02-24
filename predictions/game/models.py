from django.db import models
from predictions.models import CommonInfo

class GameRound(CommonInfo):
    name = models.CharField(max_length=128)
    submission_until = models.DateTimeField()
    
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

    
class GamePrediction(CommonInfo):
    player = models.ForeignKey('player.Profile')
    game = models.ForeignKey('Game')
    home_score_regular_time = models.SmallIntegerField()
    away_score_regular_time = models.SmallIntegerField()
    
    def __unicode__(self):
        return "%s - %s - %s vs %s - %s:%s" % (self.game.game_round.name, self.player.user.username, self.game.home_team, self.game.away_team, self.home_score_regular_time, self.away_score_regular_time)
    