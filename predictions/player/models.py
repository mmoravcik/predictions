from django.db import models

class Profile(models.Model):
    '''
    Provides additional details about a user
    '''
    user = models.OneToOneField('auth.User', unique=True)
    nickname = models.CharField(max_length=32, blank=True, null=True)
    
    def __unicode__(self):
        return self.user.username
