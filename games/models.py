from django.db import models
from django.contrib.auth.models import User

from .vitamin_game_config import (
    VITAMIN_CODE_SET,
    VITAMIN_GAME_DEFAULT_SELECTION,
    VITAMIN_LABELS,
    VITAMIN_SHORT_LABELS,
)


class Product(models.Model):
    """Модель продукта с калорийностью"""
    name = models.CharField(max_length=255)
    calories = models.IntegerField()  # Калории на 100г
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.calories} ккал)"


class GameLevel(models.Model):
    """Уровни для игры 'Собери здоровое меню'"""
    DIFFICULTY_CHOICES = [
        ('easy', 'Легко'),
        ('medium', 'Средне'),
        ('hard', 'Сложно'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    target_calories = models.IntegerField()  # Целевая калорийность
    min_calories = models.IntegerField()  # Минимально допустимо
    max_calories = models.IntegerField()  # Максимально допустимо
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    products = models.ManyToManyField(Product)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class UserGameResult(models.Model):
    """Результаты прохождения игры пользователем"""
    GAME_TYPE_CHOICES = [
        ('menu_builder', 'Собери здоровое меню'),
        ('calorie_counter', 'Подсчитай калории'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_results')
    game_type = models.CharField(max_length=20, choices=GAME_TYPE_CHOICES)
    level = models.ForeignKey(GameLevel, on_delete=models.SET_NULL, null=True, blank=True)
    # Для игр типа `calorie_counter` сохраняем сложность раунда
    difficulty = models.CharField(max_length=10, choices=[
        ('easy', 'Легко'),
        ('medium', 'Средне'),
        ('hard', 'Сложно'),
    ], null=True, blank=True)
    total_calories = models.IntegerField(null=True, blank=True)
    is_won = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_game_type_display()} ({self.completed_at})"


class CalorieCounterQuestion(models.Model):
    """Вопросы для игры 'Подсчитай калории'"""
    products_list = models.JSONField()  # Список продуктов с количеством
    correct_answer = models.IntegerField()  # Правильный ответ в калориях
    option1 = models.IntegerField()
    option2 = models.IntegerField()
    option3 = models.IntegerField()
    option4 = models.IntegerField(null=True, blank=True)  # Для средних (4) и сложных (5) вопросов
    option5 = models.IntegerField(null=True, blank=True)  # Для сложных вопросов
    difficulty = models.CharField(max_length=10, choices=[
        ('easy', 'Легко'),
        ('medium', 'Средне'),
        ('hard', 'Сложно'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Вопрос #{self.id} - {self.difficulty}"


class SnakeGameLevel(models.Model):
    """Настраиваемые уровни игры 'Змейка про здоровое питание'."""

    DIFFICULTY_CHOICES = [
        ('easy', 'Лёгкая'),
        ('medium', 'Средняя'),
        ('hard', 'Сложная'),
    ]

    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Завтрак'),
        ('lunch', 'Обед'),
        ('dinner', 'Ужин'),
    ]

    code = models.SlugField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    sort_order = models.PositiveSmallIntegerField(default=1)
    target_calories = models.PositiveIntegerField()
    min_calories = models.PositiveIntegerField()
    max_calories = models.PositiveIntegerField()
    target_protein_percent = models.PositiveSmallIntegerField()
    min_protein_percent = models.PositiveSmallIntegerField()
    max_protein_percent = models.PositiveSmallIntegerField()
    target_fat_percent = models.PositiveSmallIntegerField()
    min_fat_percent = models.PositiveSmallIntegerField()
    max_fat_percent = models.PositiveSmallIntegerField()
    target_carb_percent = models.PositiveSmallIntegerField()
    min_carb_percent = models.PositiveSmallIntegerField()
    max_carb_percent = models.PositiveSmallIntegerField()
    time_limit_seconds = models.PositiveIntegerField()
    initial_speed = models.DecimalField(max_digits=4, decimal_places=2, default=6.00)
    speed_step = models.DecimalField(max_digits=4, decimal_places=2, default=3.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'game_level'
        ordering = ('sort_order', 'id')

    def __str__(self):
        return self.title


class SnakeGameAttempt(models.Model):
    """Сохранённые результаты прохождения игры 'Змейка про здоровое питание'."""

    LOSE_REASON_CHOICES = [
        ('wall_collision', 'Столкновение со стеной'),
        ('self_collision', 'Столкновение с собой'),
        ('chemical_wall_collision', 'Столкновение со стеной во время действия колбы'),
        ('chemical_self_collision', 'Столкновение с собой во время действия колбы'),
        ('not_enough_calories', 'Не хватило калорий'),
        ('macro_balance_failed', 'Нарушен баланс БЖУ'),
        ('calorie_overflow', 'Превышены калории'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='snake_game_attempts',
    )
    level = models.ForeignKey(
        SnakeGameLevel,
        on_delete=models.CASCADE,
        related_name='attempts',
    )
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField()
    duration_seconds = models.PositiveIntegerField()
    is_win = models.BooleanField(default=False)
    lose_reason = models.CharField(
        max_length=32,
        choices=LOSE_REASON_CHOICES,
        blank=True,
    )
    total_calories = models.PositiveIntegerField(default=0)
    total_protein = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_fat = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_carb = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    protein_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fat_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    carb_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    score = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'snake_game_session'
        ordering = ('-created_at', '-id')

    def __str__(self):
        return f"{self.user.username} - {self.level.title} ({'win' if self.is_win else 'lose'})"


class SnakeGameUserStats(models.Model):
    """Агрегированная статистика пользователя по игре 'Змейка'."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='snake_game_stats',
    )
    total_attempts = models.PositiveIntegerField(default=0)
    total_wins = models.PositiveIntegerField(default=0)
    best_result_level_1 = models.PositiveIntegerField(default=0)
    best_result_level_2 = models.PositiveIntegerField(default=0)
    best_result_level_3 = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'snake_game_user_stats'

    def __str__(self):
        return f"Snake stats for {self.user.username}"


class VitaminGameLevel(models.Model):
    """Конфигурация игры 'Баланс витаминов'."""

    code = models.SlugField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    time_limit_seconds = models.PositiveIntegerField(default=60)
    start_value = models.PositiveSmallIntegerField(default=55)
    normal_min_value = models.PositiveSmallIntegerField(default=40)
    normal_max_value = models.PositiveSmallIntegerField(default=70)
    min_critical_value = models.PositiveSmallIntegerField(default=20)
    max_critical_value = models.PositiveSmallIntegerField(default=90)
    drain_per_second = models.DecimalField(max_digits=4, decimal_places=2, default=3.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vitamin_game_level'
        ordering = ('id',)

    def __str__(self):
        return self.title


class VitaminGameAttempt(models.Model):
    """Результаты прохождения игры 'Баланс витаминов'."""

    LOSE_REASON_CHOICES = [
        ('vitamin_a_low', 'Авитаминоз: витамин A'),
        ('vitamin_c_low', 'Авитаминоз: витамин C'),
        ('vitamin_d_low', 'Авитаминоз: витамин D'),
        ('vitamin_e_low', 'Авитаминоз: витамин E'),
        ('vitamin_k_low', 'Авитаминоз: витамин K'),
        ('vitamin_b_low', 'Авитаминоз: витамин B'),
        ('vitamin_a_high', 'Гипервитаминоз: витамин A'),
        ('vitamin_c_high', 'Гипервитаминоз: витамин C'),
        ('vitamin_d_high', 'Гипервитаминоз: витамин D'),
        ('vitamin_e_high', 'Гипервитаминоз: витамин E'),
        ('vitamin_k_high', 'Гипервитаминоз: витамин K'),
        ('vitamin_b_high', 'Гипервитаминоз: витамин B'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vitamin_game_attempts',
    )
    level = models.ForeignKey(
        VitaminGameLevel,
        on_delete=models.CASCADE,
        related_name='attempts',
    )
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField()
    duration_seconds = models.PositiveIntegerField()
    is_win = models.BooleanField(default=False)
    lose_reason = models.CharField(
        max_length=32,
        choices=LOSE_REASON_CHOICES,
        blank=True,
    )
    selected_vitamins = models.JSONField(default=list, blank=True)
    vitamin_a = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    vitamin_b = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    vitamin_c = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    vitamin_d = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    vitamin_e = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    vitamin_k = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vitamin_game_attempt'
        ordering = ('-created_at', '-id')

    def __str__(self):
        return f"{self.user.username} - {self.level.title} ({'win' if self.is_win else 'lose'})"

    @property
    def selected_vitamin_codes(self):
        codes = [
            code
            for code in (self.selected_vitamins or [])
            if code in VITAMIN_CODE_SET
        ]
        return codes or list(VITAMIN_GAME_DEFAULT_SELECTION)

    @property
    def selected_vitamin_rows(self):
        return [
            {
                'code': code,
                'short_label': VITAMIN_SHORT_LABELS.get(code, code),
                'label': VITAMIN_LABELS.get(code, code),
                'value': getattr(self, code),
            }
            for code in self.selected_vitamin_codes
        ]
