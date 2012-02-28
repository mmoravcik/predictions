from predictions.game.models import GameRound
from django.conf import settings

def game_rounds(request):
    return {'game_rounds': GameRound.objects.all()}

def scoring_info(request):
    return {'entry_fee': settings.ENTRY_FEE, 'point_result': settings.POINTS_CORRECT_RESULT, 'point_goal': settings.POINTS_CORRECT_ONE_OF_THE_SCORES}