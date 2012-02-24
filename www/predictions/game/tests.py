from django.test import TestCase
from predictions.game.models import Game, GamePrediction, GameRound
from predictions.player.models import Profile
from django.contrib.auth.models import User
from django.conf import settings
import datetime

class SimpleTest(TestCase):
    def setUp(self):
        self.game_round1 = GameRound.objects.create(name='First round', expire_at = datetime.datetime(2100, 12, 6, 12, 13, 14), expirable=True)
        self.game_round2 = GameRound.objects.create(name='Second round', expire_at = datetime.datetime(2011, 12, 6, 12, 13, 14), expirable=False)
        self.game_round3 = GameRound.objects.create(name='Second round', expire_at = datetime.datetime(2011, 12, 6, 12, 13, 14), expirable=True)
        
        self.game1 = Game.objects.create(home_team='Liverpool', 
                                         away_team='Chelsea', 
                                         game_round=self.game_round1, 
                                         date='2012-12-31 15:00:00', 
                                         result_home_regular_time=2, 
                                         result_away_regular_time=2,
                                         )
        
        self.game2 = Game.objects.create(home_team='Bolton', 
                                         away_team='QPR', 
                                         game_round=self.game_round1, 
                                         date='2012-12-31 15:00:00', 
                                         result_home_regular_time=3, 
                                         result_away_regular_time=1,
                                         )
        
        self.game3 = Game.objects.create(home_team='Manchester United', 
                                         away_team='Manchester City', 
                                         game_round=self.game_round1, 
                                         date='2012-12-31 15:00:00', 
                                         result_home_regular_time=0, 
                                         result_away_regular_time=4,
                                         )
        self.game4 = Game.objects.create(home_team='Everton', 
                                         away_team='Fulham', 
                                         game_round=self.game_round1, 
                                         date='2011-12-31 15:00:00', 
                                         result_home_regular_time=3, 
                                         result_away_regular_time=3,
                                         )
        self.game5 = Game.objects.create(home_team='Swansea', 
                                         away_team='Norwich City', 
                                         game_round=self.game_round2, 
                                         date='2012-12-31 15:00:00', 
                                         result_home_regular_time=1, 
                                         result_away_regular_time=1,
                                         )
        
        self.user1 = User.objects.create(username='user 1')
        self.user2 = User.objects.create(username='user 2')
        
        self.player1 = Profile.objects.create(user=self.user1, nickname = 'player 1')
        self.player2 = Profile.objects.create(user=self.user2, nickname = 'player 2')
        
        self.prediction1 = GamePrediction.objects.create(game=self.game1, player=self.player1, home_score_regular_time=2, away_score_regular_time=2)
        self.prediction2 = GamePrediction.objects.create(game=self.game2, player=self.player1, home_score_regular_time=4, away_score_regular_time=2)
        self.prediction3 = GamePrediction.objects.create(game=self.game3, player=self.player1, home_score_regular_time=0, away_score_regular_time=3)
        
        self.prediction4 = GamePrediction.objects.create(game=self.game1, player=self.player2, home_score_regular_time=1, away_score_regular_time=1)
        self.prediction5 = GamePrediction.objects.create(game=self.game2, player=self.player2, home_score_regular_time=2, away_score_regular_time=3)
        self.prediction6 = GamePrediction.objects.create(game=self.game3, player=self.player2, home_score_regular_time=1, away_score_regular_time=4)
               
        
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
    
    def test_calculate_game_points(self):
        self.assertEqual(settings.POINTS_CORRECT_RESULT + settings.POINTS_CORRECT_ONE_OF_THE_SCORES * 2, self.prediction1.get_number_of_points())
        self.assertEqual(settings.POINTS_CORRECT_RESULT, self.prediction2.get_number_of_points())
        self.assertEqual(settings.POINTS_CORRECT_RESULT + settings.POINTS_CORRECT_ONE_OF_THE_SCORES, self.prediction3.get_number_of_points())
        self.assertEqual(settings.POINTS_CORRECT_RESULT, self.prediction4.get_number_of_points())
        self.assertEqual(0, self.prediction5.get_number_of_points())
        self.assertEqual(settings.POINTS_CORRECT_RESULT + settings.POINTS_CORRECT_ONE_OF_THE_SCORES, self.prediction6.get_number_of_points())
        
    def test_game_result_home_away_draw(self):
        self.assertEqual(settings.DRAW, self.game1.home_away_draw_result())
        self.assertEqual(settings.HOME_WIN, self.game2.home_away_draw_result())
        self.assertEqual(settings.AWAY_WIN, self.game3.home_away_draw_result())
        self.assertEqual(settings.DRAW, self.game4.home_away_draw_result())
        
    def test_is_round_expired(self):
        self.assertFalse(self.game_round1.is_expired())
        self.assertFalse(self.game_round2.is_expired())
        self.assertTrue(self.game_round3.is_expired())
    
    