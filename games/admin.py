from django.contrib import admin
from .models import (
    CalorieCounterQuestion,
    GameLevel,
    Product,
    SnakeGameAttempt,
    SnakeGameLevel,
    SnakeGameUserStats,
    UserGameResult,
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'calories', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)


@admin.register(GameLevel)
class GameLevelAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'target_calories', 'min_calories', 'max_calories')
    search_fields = ('title',)
    list_filter = ('difficulty',)
    filter_horizontal = ('products',)


@admin.register(UserGameResult)
class UserGameResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'game_type', 'level', 'score', 'is_won', 'completed_at')
    search_fields = ('user__username',)
    list_filter = ('game_type', 'is_won', 'completed_at')
    readonly_fields = ('user', 'game_type', 'level', 'total_calories', 'is_won', 'score', 'completed_at')


@admin.register(CalorieCounterQuestion)
class CalorieCounterQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'difficulty', 'correct_answer', 'created_at')
    list_filter = ('difficulty', 'created_at')


@admin.register(SnakeGameLevel)
class SnakeGameLevelAdmin(admin.ModelAdmin):
    list_display = (
        'sort_order',
        'title',
        'meal_type',
        'difficulty',
        'target_calories',
        'time_limit_seconds',
        'is_active',
    )
    list_filter = ('difficulty', 'meal_type', 'is_active')
    search_fields = ('title', 'code')
    ordering = ('sort_order', 'id')


@admin.register(SnakeGameAttempt)
class SnakeGameAttemptAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'level',
        'is_win',
        'lose_reason',
        'total_calories',
        'score',
        'finished_at',
    )
    list_filter = ('is_win', 'lose_reason', 'level', 'finished_at')
    search_fields = ('user__username', 'level__title')
    readonly_fields = (
        'user',
        'level',
        'started_at',
        'finished_at',
        'duration_seconds',
        'is_win',
        'lose_reason',
        'total_calories',
        'total_protein',
        'total_fat',
        'total_carb',
        'protein_percent',
        'fat_percent',
        'carb_percent',
        'score',
        'created_at',
    )


@admin.register(SnakeGameUserStats)
class SnakeGameUserStatsAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'total_attempts',
        'total_wins',
        'best_result_level_1',
        'best_result_level_2',
        'best_result_level_3',
        'updated_at',
    )
    search_fields = ('user__username',)
    readonly_fields = (
        'user',
        'total_attempts',
        'total_wins',
        'best_result_level_1',
        'best_result_level_2',
        'best_result_level_3',
        'updated_at',
    )
