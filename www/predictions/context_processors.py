from predictions.game.models import GameRound
from django.conf import settings

def game_rounds(request):
    return {'game_rounds': GameRound.objects.all()}

def scoring_info(request):
    return {'entry_fee': settings.ENTRY_FEE}