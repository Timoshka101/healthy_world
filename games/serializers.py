from .snake_config import LOSE_REASON_LABELS, SNAKE_BOARD_CONFIG, SNAKE_FOOD_ITEMS
from .vitamin_game_config import (
    VITAMIN_GAME_DEFAULT_SELECTION,
    VITAMIN_GAME_LOSE_REASON_LABELS,
    VITAMIN_GAME_PRODUCTS,
    VITAMIN_GAME_SELECTION_SIZE,
    VITAMIN_GAME_VITAMINS,
    VITAMIN_LABELS,
    VITAMIN_SHORT_LABELS,
)


def serialize_snake_food(food_item):
    return {
        'code': food_item['code'],
        'label': food_item['label'],
        'emoji': food_item['emoji'],
        'kind': food_item['kind'],
        'macro': food_item['macro'],
        'calories': food_item['calories'],
        'protein': food_item['protein'],
        'fat': food_item['fat'],
        'carb': food_item['carb'],
        'color': food_item['color'],
        'description': food_item['description'],
    }


def serialize_snake_level(level, include_config=False):
    data = {
        'id': level.id,
        'code': level.code,
        'title': level.title,
        'difficulty': level.difficulty,
        'difficulty_label': level.get_difficulty_display(),
        'meal_type': level.meal_type,
        'meal_type_label': level.get_meal_type_display(),
        'sort_order': level.sort_order,
        'target_calories': level.target_calories,
        'min_calories': level.min_calories,
        'max_calories': level.max_calories,
        'target_protein_percent': level.target_protein_percent,
        'min_protein_percent': level.min_protein_percent,
        'max_protein_percent': level.max_protein_percent,
        'target_fat_percent': level.target_fat_percent,
        'min_fat_percent': level.min_fat_percent,
        'max_fat_percent': level.max_fat_percent,
        'target_carb_percent': level.target_carb_percent,
        'min_carb_percent': level.min_carb_percent,
        'max_carb_percent': level.max_carb_percent,
        'time_limit_seconds': level.time_limit_seconds,
        'initial_speed': float(level.initial_speed),
        'speed_step': float(level.speed_step),
        'is_active': level.is_active,
    }

    if include_config:
        data['board_config'] = SNAKE_BOARD_CONFIG
        data['foods'] = [serialize_snake_food(food_item) for food_item in SNAKE_FOOD_ITEMS]

    return data


def serialize_snake_attempt(attempt):
    return {
        'id': attempt.id,
        'level_id': attempt.level_id,
        'level_title': attempt.level.title,
        'meal_type_label': attempt.level.get_meal_type_display(),
        'finished_at': attempt.finished_at.isoformat(),
        'duration_seconds': attempt.duration_seconds,
        'time_remaining_seconds': max(attempt.level.time_limit_seconds - attempt.duration_seconds, 0),
        'is_win': attempt.is_win,
        'lose_reason': attempt.lose_reason,
        'lose_reason_label': LOSE_REASON_LABELS.get(attempt.lose_reason, ''),
        'total_calories': attempt.total_calories,
        'total_protein': float(attempt.total_protein),
        'total_fat': float(attempt.total_fat),
        'total_carb': float(attempt.total_carb),
        'protein_percent': float(attempt.protein_percent),
        'fat_percent': float(attempt.fat_percent),
        'carb_percent': float(attempt.carb_percent),
        'score': attempt.score,
    }


def serialize_snake_stats(stats):
    if not stats:
        return {
            'total_attempts': 0,
            'total_wins': 0,
            'win_rate': 0,
            'best_results': {
                'level_1': 0,
                'level_2': 0,
                'level_3': 0,
            },
        }

    win_rate = round((stats.total_wins / stats.total_attempts) * 100) if stats.total_attempts else 0

    return {
        'total_attempts': stats.total_attempts,
        'total_wins': stats.total_wins,
        'win_rate': win_rate,
        'best_results': {
            'level_1': stats.best_result_level_1,
            'level_2': stats.best_result_level_2,
            'level_3': stats.best_result_level_3,
        },
    }


def serialize_vitamin_product(product):
    return {
        'code': product['code'],
        'label': product['label'],
        'emoji': product['emoji'],
        'vitamin_code': product['vitamin_code'],
        'vitamin_label': VITAMIN_LABELS.get(product['vitamin_code'], product['vitamin_code']),
        'vitamin_short_label': VITAMIN_SHORT_LABELS.get(product['vitamin_code'], product['vitamin_code']),
        'boost': product['boost'],
        'strength': product['strength'],
        'description': product['description'],
    }


def serialize_vitamin_level(level, include_products=False):
    data = {
        'id': level.id,
        'code': level.code,
        'title': level.title,
        'time_limit_seconds': level.time_limit_seconds,
        'start_value': level.start_value,
        'normal_min_value': level.normal_min_value,
        'normal_max_value': level.normal_max_value,
        'min_critical_value': level.min_critical_value,
        'max_critical_value': level.max_critical_value,
        'drain_per_second': float(level.drain_per_second),
        'selection_size': VITAMIN_GAME_SELECTION_SIZE,
        'default_selected_vitamins': list(VITAMIN_GAME_DEFAULT_SELECTION),
        'vitamins': [
            {
                'code': vitamin['code'],
                'label': vitamin['label'],
                'display_name': vitamin['display_name'],
                'short_label': vitamin['short_label'],
            }
            for vitamin in VITAMIN_GAME_VITAMINS
        ],
    }

    if include_products:
        data['products'] = [serialize_vitamin_product(product) for product in VITAMIN_GAME_PRODUCTS]

    return data


def serialize_vitamin_attempt(attempt):
    return {
        'id': attempt.id,
        'level_id': attempt.level_id,
        'level_title': attempt.level.title,
        'finished_at': attempt.finished_at.isoformat(),
        'duration_seconds': attempt.duration_seconds,
        'is_win': attempt.is_win,
        'lose_reason': attempt.lose_reason,
        'lose_reason_label': VITAMIN_GAME_LOSE_REASON_LABELS.get(attempt.lose_reason, ''),
        'selected_vitamins': list(attempt.selected_vitamin_codes),
        'vitamin_values': {
            'vitamin_a': float(attempt.vitamin_a),
            'vitamin_b': float(attempt.vitamin_b),
            'vitamin_c': float(attempt.vitamin_c),
            'vitamin_d': float(attempt.vitamin_d),
            'vitamin_e': float(attempt.vitamin_e),
            'vitamin_k': float(attempt.vitamin_k),
        },
    }
