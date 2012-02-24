from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from predictions.game.models import Game, GameRound, GamePrediction

@login_required
def predict(request, round_id):
    games = Game.objects.filter(game_round=round_id)
    games_to_return = []
    for game in games:
        game.player_predicted = game.has_player_predicted(request.user.get_profile())
        if game.player_predicted == True:
            prediction = game.get_player_predictions(request.user.get_profile())
            game.home_score_regular_time_prediction = prediction[0].home_score_regular_time
            game.away_score_regular_time_prediction = prediction[0].away_score_regular_time
        games_to_return.append(game)
    
    context = {'round': GameRound.objects.get(pk=round_id),
               'games': games_to_return,
               }    
      
    return render_to_response('pages/predict.html', context , context_instance=RequestContext(request))

def predict_submit(request):
    round_id = request.POST['round_id']
    games = Game.objects.filter(game_round=round_id)
    for game in games:
        if is_prediction_valid(request, game):
            prediction = GamePrediction(game=game, 
                                        player=request.user.get_profile(), 
                                        home_score_regular_time=request.POST['home_score_%d' % game.id],
                                        away_score_regular_time=request.POST['away_score_%d' % game.id],
                                        )
            prediction.save()

    return HttpResponseRedirect('/predict/%s' % round_id)

def is_prediction_valid(request, game):
    return True if \
        request.POST.get('home_score_%d' % game.id,None) and \
        request.POST.get('away_score_%d' % game.id,None) and \
        request.POST.get('home_score_%d' % game.id,None).isdigit() and \
        request.POST.get('away_score_%d' % game.id,None).isdigit() and \
        game.has_player_predicted(request.user.get_profile()) == False \
    else False