from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import (
    CalorieCounterQuestion,
    GameLevel,
    Product,
    SnakeGameAttempt,
    SnakeGameLevel,
    SnakeGameUserStats,
    UserGameResult,
    VitaminGameAttempt,
    VitaminGameLevel,
)
from .snake_services import calculate_macro_percentages


class ProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Яблоко",
            calories=52,
            description="Спелое красное яблоко",
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Яблоко")
        self.assertEqual(self.product.calories, 52)

    def test_product_str(self):
        self.assertEqual(str(self.product), "Яблоко (52 ккал)")


class GameLevelTest(TestCase):
    def setUp(self):
        self.product1 = Product.objects.create(name="Хлеб", calories=265)
        self.product2 = Product.objects.create(name="Масло", calories=717)
        self.level = GameLevel.objects.create(
            title="Завтрак",
            description="Соберите завтрак на 300 ккал",
            target_calories=300,
            min_calories=250,
            max_calories=350,
            difficulty="easy",
        )
        self.level.products.add(self.product1, self.product2)

    def test_game_level_creation(self):
        self.assertEqual(self.level.title, "Завтрак")
        self.assertEqual(self.level.products.count(), 2)


class InteractiveGameSeedTest(TestCase):
    def test_menu_builder_levels_seeded(self):
        seeded_titles = set(
            GameLevel.objects.values_list("title", flat=True)
        )

        self.assertEqual(
            seeded_titles,
            {"🟢 Лёгкий завтрак", "🟡 Сытный завтрак", "🔴 Обеденный комбо"},
        )
        self.assertEqual(GameLevel.objects.count(), 3)

    def test_calorie_counter_questions_seeded_for_all_difficulties(self):
        self.assertGreaterEqual(CalorieCounterQuestion.objects.filter(difficulty="easy").count(), 5)
        self.assertGreaterEqual(CalorieCounterQuestion.objects.filter(difficulty="medium").count(), 5)
        self.assertGreaterEqual(CalorieCounterQuestion.objects.filter(difficulty="hard").count(), 5)


class UserGameResultTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.result = UserGameResult.objects.create(
            user=self.user,
            game_type="menu_builder",
            total_calories=300,
            is_won=True,
            score=95,
        )

    def test_user_game_result_creation(self):
        self.assertEqual(self.result.user.username, "testuser")
        self.assertTrue(self.result.is_won)
        self.assertEqual(self.result.score, 95)


class SnakeGameLevelSeedTest(TestCase):
    def test_snake_levels_seeded(self):
        seeded_codes = set(
            SnakeGameLevel.objects.filter(
                code__in=["snake-breakfast", "snake-lunch", "snake-dinner"]
            ).values_list("code", flat=True)
        )
        self.assertEqual(
            seeded_codes,
            {"snake-breakfast", "snake-lunch", "snake-dinner"},
        )


class InteractiveGameAuthRedirectTest(TestCase):
    def test_menu_builder_levels_redirects_to_login_for_guest(self):
        response = self.client.get(reverse("menu_builder_levels"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response["Location"])

    def test_calorie_counter_levels_redirects_to_login_for_guest(self):
        response = self.client.get(reverse("calorie_counter_levels"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response["Location"])


class InteractiveGameAuthenticatedAccessTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="interactive_user", password="12345")

    def test_menu_builder_levels_are_visible_for_authenticated_user(self):
        self.client.login(username="interactive_user", password="12345")

        response = self.client.get(reverse("menu_builder_levels"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "🟢 Лёгкий завтрак")
        self.assertContains(response, "🟡 Сытный завтрак")
        self.assertContains(response, "🔴 Обеденный комбо")

    def test_calorie_counter_levels_are_visible_for_authenticated_user(self):
        self.client.login(username="interactive_user", password="12345")

        response = self.client.get(reverse("calorie_counter_levels"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Легко")
        self.assertContains(response, "Средне")
        self.assertContains(response, "Сложно")

    def test_calorie_counter_easy_game_has_seeded_questions_for_authenticated_user(self):
        self.client.login(username="interactive_user", password="12345")

        response = self.client.get(reverse("calorie_counter_game", args=["easy"]))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Вопросы для этого уровня сложности еще не созданы")


class SnakeGameApiTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="snake", password="12345")
        self.level = SnakeGameLevel.objects.get(code="snake-breakfast")

    def test_levels_api_returns_seeded_levels(self):
        response = self.client.get(reverse("snake_levels_api"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["levels"]), 3)
        self.assertEqual(payload["levels"][0]["code"], "snake-breakfast")

    def test_level_detail_api_returns_food_config(self):
        response = self.client.get(reverse("snake_level_detail_api", args=[self.level.id]))

        self.assertEqual(response.status_code, 200)
        payload = response.json()["level"]
        self.assertEqual(payload["code"], "snake-breakfast")
        self.assertIn("foods", payload)
        self.assertGreaterEqual(len(payload["foods"]), 5)

    def test_result_api_requires_authentication(self):
        response = self.client.post(
            reverse("snake_result_api"),
            content_type="application/json",
            data="{}",
        )

        self.assertEqual(response.status_code, 401)

    def test_result_api_saves_attempt_and_updates_stats(self):
        self.client.login(username="snake", password="12345")
        response = self.client.post(
            reverse("snake_result_api"),
            content_type="application/json",
            data="""
            {
                "level_id": %d,
                "is_win": true,
                "lose_reason": "",
                "total_calories": 610,
                "total_protein": 45,
                "total_fat": 16.8,
                "total_carb": 70,
                "protein_percent": 29.5,
                "fat_percent": 24.8,
                "carb_percent": 45.7,
                "duration_seconds": 75
            }
            """ % self.level.id,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(SnakeGameAttempt.objects.count(), 1)

        attempt = SnakeGameAttempt.objects.get()
        self.assertTrue(attempt.is_win)
        self.assertEqual(attempt.total_calories, 610)
        self.assertAlmostEqual(float(attempt.protein_percent), 29.45, places=2)

        stats = SnakeGameUserStats.objects.get(user=self.user)
        self.assertEqual(stats.total_attempts, 1)
        self.assertEqual(stats.total_wins, 1)

    def test_history_api_returns_latest_attempts(self):
        self.client.login(username="snake", password="12345")
        SnakeGameAttempt.objects.create(
            user=self.user,
            level=self.level,
            started_at="2026-03-25T10:00:00Z",
            finished_at="2026-03-25T10:01:00Z",
            duration_seconds=60,
            is_win=False,
            lose_reason="self_collision",
            total_calories=430,
            total_protein=Decimal("30.00"),
            total_fat=Decimal("6.00"),
            total_carb=Decimal("35.00"),
            protein_percent=Decimal("41.38"),
            fat_percent=Decimal("18.62"),
            carb_percent=Decimal("40.00"),
            score=29,
        )
        SnakeGameUserStats.objects.create(user=self.user, total_attempts=1, total_wins=0)

        response = self.client.get(reverse("snake_history_api"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["attempts"]), 1)
        self.assertEqual(payload["attempts"][0]["lose_reason"], "self_collision")


class SnakeMacroCalculationTest(TestCase):
    def test_macro_percentages_are_calculated_from_macro_calories(self):
        percentages = calculate_macro_percentages(
            total_protein=Decimal("45.00"),
            total_fat=Decimal("16.80"),
            total_carb=Decimal("70.00"),
        )

        self.assertAlmostEqual(float(percentages["protein_percent"]), 29.45, places=2)
        self.assertAlmostEqual(float(percentages["fat_percent"]), 24.74, places=2)
        self.assertAlmostEqual(float(percentages["carb_percent"]), 45.81, places=2)


class VitaminGameApiTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="vitamin", password="12345")

    def test_config_api_returns_default_level_and_products(self):
        response = self.client.get(reverse("vitamin_game_config_api"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()["level"]
        self.assertEqual(payload["code"], "vitamin-balance")
        self.assertEqual(payload["start_value"], 55)
        self.assertEqual(payload["selection_size"], 3)
        self.assertEqual(len(payload["vitamins"]), 6)
        self.assertEqual(len(payload["products"]), 12)
        self.assertTrue(VitaminGameLevel.objects.filter(code="vitamin-balance").exists())

    def test_result_api_requires_authentication(self):
        response = self.client.post(
            reverse("vitamin_game_result_api"),
            content_type="application/json",
            data="{}",
        )

        self.assertEqual(response.status_code, 401)

    def test_result_api_saves_attempt(self):
        level_response = self.client.get(reverse("vitamin_game_config_api"))
        level_id = level_response.json()["level"]["id"]

        self.client.login(username="vitamin", password="12345")
        response = self.client.post(
            reverse("vitamin_game_result_api"),
            content_type="application/json",
            data="""
            {
                "level_id": %d,
                "is_win": false,
                "lose_reason": "vitamin_c_low",
                "selected_vitamins": ["vitamin_c", "vitamin_d", "vitamin_k"],
                "vitamin_a": 44.5,
                "vitamin_b": 55.0,
                "vitamin_c": 19.8,
                "vitamin_d": 52.1,
                "vitamin_e": 55.0,
                "vitamin_k": 61.0,
                "duration_seconds": 31
            }
            """ % level_id,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(VitaminGameAttempt.objects.count(), 1)

        attempt = VitaminGameAttempt.objects.get()
        self.assertFalse(attempt.is_win)
        self.assertEqual(attempt.lose_reason, "vitamin_c_low")
        self.assertEqual(attempt.selected_vitamins, ["vitamin_c", "vitamin_d", "vitamin_k"])
        self.assertAlmostEqual(float(attempt.vitamin_c), 19.8, places=2)

    def test_result_api_saves_win_attempt(self):
        level_response = self.client.get(reverse("vitamin_game_config_api"))
        level_id = level_response.json()["level"]["id"]

        self.client.login(username="vitamin", password="12345")
        response = self.client.post(
            reverse("vitamin_game_result_api"),
            content_type="application/json",
            data="""
            {
                "level_id": %d,
                "is_win": true,
                "lose_reason": "",
                "selected_vitamins": ["vitamin_a", "vitamin_e", "vitamin_b"],
                "vitamin_a": 48.4,
                "vitamin_b": 57.1,
                "vitamin_c": 55.0,
                "vitamin_d": 55.0,
                "vitamin_e": 53.2,
                "vitamin_k": 55.0,
                "duration_seconds": 30
            }
            """ % level_id,
        )

        self.assertEqual(response.status_code, 201)
        attempt = VitaminGameAttempt.objects.get()
        self.assertTrue(attempt.is_win)
        self.assertEqual(attempt.lose_reason, "")
        self.assertEqual(attempt.selected_vitamins, ["vitamin_a", "vitamin_e", "vitamin_b"])


class VitaminStatisticsPageTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="vitamin_stats", password="12345")
        self.level = VitaminGameLevel.objects.create(
            code="vitamin-balance",
            title="Баланс витаминов",
            time_limit_seconds=30,
            start_value=55,
            normal_min_value=40,
            normal_max_value=70,
            min_critical_value=20,
            max_critical_value=90,
            drain_per_second=5.6,
        )
        VitaminGameAttempt.objects.create(
            user=self.user,
            level=self.level,
            started_at="2026-03-26T00:00:00Z",
            finished_at="2026-03-26T00:00:18Z",
            duration_seconds=18,
            is_win=False,
            lose_reason="vitamin_c_low",
            selected_vitamins=["vitamin_a", "vitamin_c", "vitamin_d"],
            vitamin_a=42.5,
            vitamin_b=55.0,
            vitamin_c=19.7,
            vitamin_d=51.3,
            vitamin_e=55.0,
            vitamin_k=55.0,
        )

    def test_games_home_shows_vitamin_summary(self):
        self.client.login(username="vitamin_stats", password="12345")

        response = self.client.get(reverse("games_home"))

        self.assertContains(response, "Витамины")
        self.assertContains(response, "1 игр")
        self.assertContains(response, "0 побед")

    def test_user_statistics_shows_vitamin_card_and_history(self):
        self.client.login(username="vitamin_stats", password="12345")

        response = self.client.get(reverse("user_statistics"))

        self.assertContains(response, "Баланс витаминов")
        self.assertContains(response, "Среднее время:")
        self.assertContains(response, "Авитаминоз: витамин C")
        self.assertContains(response, "A 42,50")
        self.assertContains(response, "C 19,70")


class CalorieCounterQuestionTest(TestCase):
    def test_question_creation(self):
        question = CalorieCounterQuestion.objects.create(
            products_list=[{"name": "Яблоко", "quantity": "100 г"}],
            correct_answer=52,
            option1=40,
            option2=52,
            option3=65,
            difficulty="easy",
        )

        self.assertEqual(question.correct_answer, 52)
        self.assertEqual(question.difficulty, "easy")
