from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Food(models.Model):
    name = models.CharField(max_length=100, unique=True)
    calories_per_100g = models.FloatField()
    protein_per_100g = models.FloatField()
    fat_per_100g = models.FloatField()
    carbohydrate_per_100g = models.FloatField()

    def __str__(self):
        return self.name

class DiaryEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity_grams = models.FloatField()
    date = models.DateField()

    def calculate_nutrition(self):
        factor = self.quantity_grams / 100
        return {
            'calories': self.food.calories_per_100g * factor,
            'protein': self.food.protein_per_100g * factor,
            'fat': self.food.fat_per_100g * factor,
            'carbohydrate': self.food.carbohydrate_per_100g * factor,
        }

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=[('male', 'Мужской'), ('female', 'Женский')])
    birth_date = models.DateField(default=date(1990, 1, 1))  # Значение по умолчанию
    height_cm = models.IntegerField(default=170)  # Значение по умолчанию
    weight_kg = models.FloatField(default=70.0)  # Значение по умолчанию
    activity_level = models.CharField(max_length=20, choices=[
        ('sedentary', 'Сидячий'),
        ('light', 'Легкая активность'),
        ('moderate', 'Умеренная активность'),
        ('active', 'Высокая активность'),
    ], default='sedentary')  # Значение по умолчанию
    goal = models.CharField(max_length=20, choices=[
        ('lose', 'Снижение веса'),
        ('maintain', 'Поддержание веса'),
        ('gain', 'Набор массы'),
    ], default='maintain')  # Значение по умолчанию

    def calculate_targets(self):
        if self.gender == 'male':
            bmr = 10 * self.weight_kg + 6.25 * self.height_cm - 5 * self.get_age() + 5
        else:
            bmr = 10 * self.weight_kg + 6.25 * self.height_cm - 5 * self.get_age() - 161

        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
        }
        tdee = bmr * activity_multipliers[self.activity_level]

        if self.goal == 'lose':
            target_calories = tdee * 0.8
        elif self.goal == 'gain':
            target_calories = tdee * 1.2
        else:
            target_calories = tdee

        protein = (target_calories * 0.3) / 4
        fat = (target_calories * 0.3) / 9
        carbohydrate = (target_calories * 0.4) / 4

        return {
            'calories': target_calories,
            'protein': protein,
            'fat': fat,
            'carbohydrate': carbohydrate,
        }

    def get_age(self):
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))