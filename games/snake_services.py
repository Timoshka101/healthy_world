from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Max

from .models import SnakeGameAttempt, SnakeGameLevel, SnakeGameUserStats


FOUR = Decimal('4')
NINE = Decimal('9')
TWO_DECIMALS = Decimal('0.01')


def to_decimal(value):
    return Decimal(str(value)).quantize(TWO_DECIMALS, rounding=ROUND_HALF_UP)


def calculate_macro_percentages(total_protein, total_fat, total_carb):
    protein_calories = to_decimal(total_protein) * FOUR
    fat_calories = to_decimal(total_fat) * NINE
    carb_calories = to_decimal(total_carb) * FOUR
    total_macro_calories = protein_calories + fat_calories + carb_calories

    if total_macro_calories <= 0:
        zero = Decimal('0.00')
        return {
            'protein_percent': zero,
            'fat_percent': zero,
            'carb_percent': zero,
        }

    return {
        'protein_percent': ((protein_calories / total_macro_calories) * 100).quantize(
            TWO_DECIMALS, rounding=ROUND_HALF_UP
        ),
        'fat_percent': ((fat_calories / total_macro_calories) * 100).quantize(
            TWO_DECIMALS, rounding=ROUND_HALF_UP
        ),
        'carb_percent': ((carb_calories / total_macro_calories) * 100).quantize(
            TWO_DECIMALS, rounding=ROUND_HALF_UP
        ),
    }


def calculate_snake_score(level, is_win, total_calories, protein_percent, fat_percent, carb_percent, duration_seconds):
    calorie_tolerance = max(level.max_calories - level.min_calories, 1)
    calorie_accuracy = max(
        0.0,
        1.0 - (abs(total_calories - level.target_calories) / calorie_tolerance),
    )

    macro_deviation = (
        abs(float(protein_percent) - level.target_protein_percent)
        + abs(float(fat_percent) - level.target_fat_percent)
        + abs(float(carb_percent) - level.target_carb_percent)
    ) / 3.0
    macro_accuracy = max(0.0, 1.0 - (macro_deviation / 25.0))

    if level.time_limit_seconds > 0:
        time_ratio = max(0.0, (level.time_limit_seconds - duration_seconds) / level.time_limit_seconds)
    else:
        time_ratio = 0.0

    if is_win:
        return round((calorie_accuracy * 60) + (macro_accuracy * 25) + (time_ratio * 15))

    progress_ratio = min(total_calories / level.target_calories, 1.0) if level.target_calories else 0.0
    return round((progress_ratio * 40) + (macro_accuracy * 20))


def refresh_snake_user_stats(user):
    stats, _ = SnakeGameUserStats.objects.get_or_create(user=user)
    attempts = SnakeGameAttempt.objects.filter(user=user)

    stats.total_attempts = attempts.count()
    stats.total_wins = attempts.filter(is_win=True).count()

    ordered_levels = list(SnakeGameLevel.objects.order_by('sort_order', 'id')[:3])
    best_scores = [0, 0, 0]

    for index, level in enumerate(ordered_levels, start=1):
        best_score = attempts.filter(level=level).aggregate(Max('score'))['score__max'] or 0
        best_scores[index - 1] = best_score

    stats.best_result_level_1 = best_scores[0]
    stats.best_result_level_2 = best_scores[1]
    stats.best_result_level_3 = best_scores[2]
    stats.save()

    return stats
