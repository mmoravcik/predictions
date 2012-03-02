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
    user_predicted_all_games = True
    for game in games:
        game.player_predicted = game.has_player_predicted(request.user.get_profile())
        if game.player_predicted:
            prediction = game.get_player_predictions(request.user.get_profile())
            game.home_score_regular_time_prediction = prediction.home_score_regular_time
            game.away_score_regular_time_prediction = prediction.away_score_regular_time
        else:
            user_predicted_all_games = False
        
        games_to_return.append(game)
    
    context = {'round': game_round,
               'games': games_to_return,
               'user_predicted_all_games': user_predicted_all_games,
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
            if game.display_in_results(player, request.user.get_profile()):
                prediction = GamePrediction.objects.filter(player=player, game=game)
                player_points += prediction[0].get_number_of_points()
                player_predictions.append(prediction[0])
        
        if player_predictions:
            player.predictions = player_predictions
            player.total_points =  player_points       
            player_info.append(player)
                
    context = {'round': game_round,
               'player_info': player_info,
               }    
      
    return render_to_response('pages/round_results.html', context , context_instance=RequestContext(request))

@login_required
def predict_submit(request):
    round_id = request.POST['round_id']
    games = Game.objects.filter(game_round=round_id)
    for game in games:
        prediction = GamePrediction(game=game, 
                                    player=request.user.get_profile(), 
                                    home_score_regular_time=request.POST.get('home_score_%d' % game.id, None),
                                    away_score_regular_time=request.POST.get('away_score_%d' % game.id, None),
                                    )
        if prediction.is_valid_for_save():
            prediction.save()

    return HttpResponseRedirect('/round/predict/%s' % round_id)