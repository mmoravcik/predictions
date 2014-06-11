from django.db import models
from predictions.game.models import GamePrediction


class Profile(models.Model):
    '''
    Provides additional details about a user
    '''
    user = models.OneToOneField('auth.User', unique=True)
    nickname = models.CharField(max_length=32, blank=True, null=True)
    free_game = models.BooleanField(default=False)
    
    
    def __unicode__(self):
        return "%s, free game: %s, predicted: %s, email: %s" % (
            self.user.username, self.user.profile.free_game,
            GamePrediction.objects.filter(player=self).exists(), self.user.email)
