from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from game.models import Game, GameRound, GamePrediction

@login_required
def predict(request, round_id):
    return render_to_response('pages/predict.html', {'round': GameRound.objects.get(pk=round_id), 'games': Game.objects.filter(game_round=round_id)}, context_instance=RequestContext(request))

def predict_submit(request):
    round_id = request.POST['round_id']
    games = Game.objects.filter(game_round=round_id)
    for game in games:
        prediction = GamePrediction(game=game, player=request.user.get_profile(), home_score_regular_time=request.POST['home_score_1'])
        prediction.save()
    submita = "ok"

    return render_to_response('pages/predict.html', {'submita': submita,'round': GameRound.objects.get(pk=round_id), 'games': Game.objects.filter(game_round=round_id)}, context_instance=RequestContext(request))