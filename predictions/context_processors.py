from predictions.game.models import GameRound

def game_rounds(request):
    return {'game_rounds': GameRound.objects.all()}