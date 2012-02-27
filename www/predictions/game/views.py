from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from predictions.game.models import Game, GameRound, GamePrediction
from predictions.player.models import Profile

@login_required
def predict(request, round_id):
    game_round = GameRound.objects.get(pk=round_id)
    games_to_return = []
    games = Game.objects.filter(game_round=game_round)
    for game in games:
        game.player_predicted = game.has_player_predicted(request.user.get_profile())
        if game.player_predicted:
            prediction = game.get_player_predictions(request.user.get_profile())
            game.home_score_regular_time_prediction = prediction[0].home_score_regular_time
            game.away_score_regular_time_prediction = prediction[0].away_score_regular_time
        games_to_return.append(game)
    
    context = {'round': game_round,
               'games': games_to_return,
               }    
      
    return render_to_response('pages/predict.html', context , context_instance=RequestContext(request))

@login_required
def round_results(request, round_id):
    game_round = GameRound.objects.get(pk=round_id)
    players = Profile.objects.all()
    games = Game.objects.filter(game_round=game_round)
    
    player_info = []
    for player in players:
        player_points = 0
        player_predictions = []
        
        for game in games:
            if should_be_game_displayed_in_results(request, player, game):
                prediction = GamePrediction.objects.get(player=player, game=game)
                
                player_points += prediction.get_number_of_points()
                player_predictions.append(prediction)
        
        player.predictions = player_predictions
        player.total_points =  player_points       
        player_info.append(player)
                
                
    context = {'round': game_round,
               'player_info': player_info,
               }    
      
    return render_to_response('pages/round_results.html', context , context_instance=RequestContext(request))

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

    return HttpResponseRedirect('/round/predict/%s' % round_id)

def should_be_game_displayed_in_results(request, player, game):
    return game.has_player_predicted(player) and (game.has_player_predicted(request.user.get_profile()) or game.game_round.is_expired() or game.is_expired())

def is_prediction_valid(request, game):
    return True if \
        request.POST.get('home_score_%d' % game.id,None) and \
        request.POST.get('away_score_%d' % game.id,None) and \
        request.POST.get('home_score_%d' % game.id,None).isdigit() and \
        request.POST.get('away_score_%d' % game.id,None).isdigit() and \
        not game.game_round.is_expired() and \
        not game.is_expired() and \
        game.has_player_predicted(request.user.get_profile()) == False \
    else False