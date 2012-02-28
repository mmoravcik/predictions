from django.test import TestCase
from predictions.game.models import Game, GamePrediction, GameRound
from predictions.player.models import Profile
from django.contrib.auth.models import User
from django.conf import settings
import datetime

class SimpleTest(TestCase):
    def setUp(self):
        self.now = datetime.datetime.now()
        self.current_year = self.now.year
        self.year_old = self.current_year-1
        self.year_ahead = self.current_year+1
        
        self.game_round1 = GameRound.objects.create(name='First round', expire_at = datetime.datetime(self.year_ahead, 12, 6, 12, 13, 14), expirable=True)
        self.game_round2 = GameRound.objects.create(name='Second round', expire_at = datetime.datetime(self.year_old, 12, 6, 12, 13, 14), expirable=False)
        self.game_round3 = GameRound.objects.create(name='Third round', expire_at = datetime.datetime(self.year_old, 12, 6, 12, 13, 14), expirable=True)
        self.game_round4 = GameRound.objects.create(name='Fourth round', expire_at = None, expirable=True)
        
        self.game1 = Game.objects.create(home_team='Liverpool', 
                                         away_team='Chelsea', 
                                         game_round=self.game_round1, 
                                         date=datetime.datetime(self.year_ahead, 12, 6, 12, 13, 14), 
                                         result_home_regular_time=2, 
                                         result_away_regular_time=2,
                                         )
        
        self.game2 = Game.objects.create(home_team='Bolton', 
                                         away_team='QPR', 
                                         game_round=self.game_round1, 
                                         date=datetime.datetime(self.year_ahead, 12, 6, 12, 13, 14), 
                                         result_home_regular_time=3, 
                                         result_away_regular_time=1,
                                         )
        
        self.game3 = Game.objects.create(home_team='Manchester United', 
                                         away_team='Manchester City', 
                                         game_round=self.game_round1, 
                                         date=datetime.datetime(self.year_ahead, 12, 6, 12, 13, 14), 
                                         result_home_regular_time=0, 
                                         result_away_regular_time=4,
                                         )
        self.game4 = Game.objects.create(home_team='Everton', 
                                         away_team='Fulham', 
                                         game_round=self.game_round1, 
                                         date=datetime.datetime(self.year_old, 12, 6, 12, 13, 14), 
                                         result_home_regular_time=3, 
                                         result_away_regular_time=3,
                                         )
        self.game5 = Game.objects.create(home_team='Swansea', 
                                         away_team='Norwich City', 
                                         game_round=self.game_round2, 
                                         date=datetime.datetime(self.year_old, 12, 6, 12, 13, 14),  
                                         result_home_regular_time=1, 
                                         result_away_regular_time=1,
                                         )
        
        self.user1 = User.objects.create(username='user 1')
        self.user2 = User.objects.create(username='user 2')
        self.user3 = User.objects.create(username='user 3')
        
        self.player1 = Profile.objects.create(user=self.user1, nickname = 'player 1', free_game=False)
        self.player2 = Profile.objects.create(user=self.user2, nickname = 'player 2', free_game=True)
        self.player3 = Profile.objects.create(user=self.user3, nickname = 'player 3', free_game=False)
        
        self.prediction1 = GamePrediction.objects.create(game=self.game1, player=self.player1, home_score_regular_time=2, away_score_regular_time=2)
        self.prediction2 = GamePrediction.objects.create(game=self.game2, player=self.player1, home_score_regular_time=4, away_score_regular_time=2)
        self.prediction3 = GamePrediction.objects.create(game=self.game3, player=self.player1, home_score_regular_time=0, away_score_regular_time=3)
        
        self.prediction4 = GamePrediction.objects.create(game=self.game1, player=self.player2, home_score_regular_time=1, away_score_regular_time=1)
        self.prediction5 = GamePrediction.objects.create(game=self.game2, player=self.player2, home_score_regular_time=2, away_score_regular_time=3)
        self.prediction6 = GamePrediction.objects.create(game=self.game3, player=self.player2, home_score_regular_time=1, away_score_regular_time=4)
        
        self.prediction7 = GamePrediction(game=self.game3, player=self.player2, home_score_regular_time=None, away_score_regular_time=4)
        self.prediction8 = GamePrediction(game=self.game3, player=self.player2, home_score_regular_time="er", away_score_regular_time="4")
        
        self.prediction9 = GamePrediction(game=self.game1, player=self.player3, home_score_regular_time=1, away_score_regular_time=2)
        self.prediction10 = GamePrediction(game=self.game4, player=self.player3, home_score_regular_time=1, away_score_regular_time=None)
        self.prediction11 = GamePrediction(game=self.game5, player=self.player3, home_score_regular_time=1, away_score_regular_time=2)
        self.prediction12 = GamePrediction(game=self.game1, player=self.player3, home_score_regular_time="1", away_score_regular_time=2)
        self.prediction13 = GamePrediction(game=self.game1, player=self.player3, home_score_regular_time="1", away_score_regular_time="1s")
        
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
        
    def test_game_home_away_draw_regular_time(self):
        self.assertEqual(settings.DRAW, self.game1.home_away_draw_result())
        self.assertEqual(settings.HOME_WIN, self.game2.home_away_draw_result())
        self.assertEqual(settings.AWAY_WIN, self.game3.home_away_draw_result())
    
    def test_prediction_away_draw_regular_time(self):
        self.assertEqual(settings.DRAW, self.prediction1.get_home_away_draw_guess())
        self.assertEqual(settings.HOME_WIN, self.prediction2.get_home_away_draw_guess())
        self.assertEqual(settings.AWAY_WIN, self.prediction5.get_home_away_draw_guess())
    
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
        self.assertFalse(self.game_round4.is_expired())
        
    def test_competitive_prediction(self):
        self.assertTrue(self.prediction1.competitive)
        self.assertFalse(self.prediction6.competitive)
    
    def test_is_game_expired(self):
        self.assertFalse(self.game1.is_expired())
        self.assertTrue(self.game5.is_expired())
    

    def test_is_prediction_valid_for_save(self):
        self.assertFalse(self.prediction7.is_valid_for_save())
        self.assertFalse(self.prediction8.is_valid_for_save())
        self.assertFalse(self.prediction1.is_valid_for_save())
        self.assertFalse(self.prediction4.is_valid_for_save())
        self.assertTrue(self.prediction9.is_valid_for_save())
        self.assertFalse(self.prediction10.is_valid_for_save())
        self.assertFalse(self.prediction11.is_valid_for_save())
        self.assertTrue(self.prediction12.is_valid_for_save())
        self.assertFalse(self.prediction13.is_valid_for_save())