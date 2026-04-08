import json
from datetime import timedelta

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .forms import SnakeGameResultForm, VitaminGameResultForm
from .models import (
    SnakeGameAttempt,
    SnakeGameLevel,
    SnakeGameUserStats,
    VitaminGameAttempt,
    VitaminGameLevel,
)
from .serializers import (
    serialize_snake_attempt,
    serialize_snake_level,
    serialize_snake_stats,
    serialize_vitamin_attempt,
    serialize_vitamin_level,
)
from .snake_services import (
    calculate_macro_percentages,
    calculate_snake_score,
    refresh_snake_user_stats,
    to_decimal,
)
from .vitamin_game_config import VITAMIN_GAME_DEFAULT_LEVEL
from .vitamin_game_config import VITAMIN_CODE_SET


def _json_auth_required(request):
    if request.user.is_authenticated:
        return None

    return JsonResponse(
        {'detail': 'Для сохранения результатов нужно войти в систему.'},
        status=401,
    )


def _ranges_match(level, total_calories, protein_percent, fat_percent, carb_percent):
    calories_ok = level.min_calories <= total_calories <= level.max_calories
    protein_ok = level.min_protein_percent <= float(protein_percent) <= level.max_protein_percent
    fat_ok = level.min_fat_percent <= float(fat_percent) <= level.max_fat_percent
    carb_ok = level.min_carb_percent <= float(carb_percent) <= level.max_carb_percent
    return calories_ok and protein_ok and fat_ok and carb_ok


def _derive_lose_reason(level, provided_reason, total_calories, protein_percent, fat_percent, carb_percent):
    if total_calories > level.max_calories:
        return 'calorie_overflow'
    if total_calories < level.min_calories:
        return 'not_enough_calories'

    if provided_reason in {
        'wall_collision',
        'self_collision',
        'chemical_wall_collision',
        'chemical_self_collision',
    }:
        return provided_reason

    if not (
        level.min_protein_percent <= float(protein_percent) <= level.max_protein_percent
        and level.min_fat_percent <= float(fat_percent) <= level.max_fat_percent
        and level.min_carb_percent <= float(carb_percent) <= level.max_carb_percent
    ):
        return 'macro_balance_failed'

    return provided_reason or 'macro_balance_failed'


def _get_or_create_vitamin_level():
    level_defaults = {
        key: value
        for key, value in VITAMIN_GAME_DEFAULT_LEVEL.items()
        if key != 'code'
    }
    level_defaults['is_active'] = True

    level, _ = VitaminGameLevel.objects.update_or_create(
        code=VITAMIN_GAME_DEFAULT_LEVEL['code'],
        defaults=level_defaults,
    )
    return level


def _derive_vitamin_lose_reason(level, vitamin_values, selected_vitamins):
    for vitamin_code in selected_vitamins:
        value = float(vitamin_values.get(vitamin_code, 0))
        if value < level.min_critical_value:
            return f'{vitamin_code}_low'

    for vitamin_code in selected_vitamins:
        value = float(vitamin_values.get(vitamin_code, 0))
        if value > level.max_critical_value:
            return f'{vitamin_code}_high'

    return ''


@require_GET
def snake_levels_api(request):
    levels = SnakeGameLevel.objects.filter(is_active=True).order_by('sort_order', 'id')
    return JsonResponse(
        {'levels': [serialize_snake_level(level) for level in levels]},
    )


@require_GET
def snake_level_detail_api(request, level_id):
    level = get_object_or_404(SnakeGameLevel.objects.filter(is_active=True), id=level_id)
    return JsonResponse({'level': serialize_snake_level(level, include_config=True)})


@require_POST
def snake_result_api(request):
    auth_error = _json_auth_required(request)
    if auth_error:
        return auth_error

    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Некорректный JSON.'}, status=400)

    form = SnakeGameResultForm(payload)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)

    cleaned_data = form.cleaned_data
    level = get_object_or_404(SnakeGameLevel.objects.filter(is_active=True), id=cleaned_data['level_id'])

    total_protein = to_decimal(cleaned_data['total_protein'])
    total_fat = to_decimal(cleaned_data['total_fat'])
    total_carb = to_decimal(cleaned_data['total_carb'])
    total_calories = cleaned_data['total_calories']
    duration_seconds = cleaned_data['duration_seconds']

    percentages = calculate_macro_percentages(total_protein, total_fat, total_carb)
    is_valid_win = _ranges_match(
        level,
        total_calories,
        percentages['protein_percent'],
        percentages['fat_percent'],
        percentages['carb_percent'],
    )

    is_win = bool(cleaned_data['is_win']) and is_valid_win
    lose_reason = '' if is_win else _derive_lose_reason(
        level,
        cleaned_data.get('lose_reason'),
        total_calories,
        percentages['protein_percent'],
        percentages['fat_percent'],
        percentages['carb_percent'],
    )

    score = calculate_snake_score(
        level=level,
        is_win=is_win,
        total_calories=total_calories,
        protein_percent=percentages['protein_percent'],
        fat_percent=percentages['fat_percent'],
        carb_percent=percentages['carb_percent'],
        duration_seconds=duration_seconds,
    )

    finished_at = timezone.now()
    started_at = cleaned_data.get('started_at') or (finished_at - timedelta(seconds=duration_seconds))
    if timezone.is_naive(started_at):
        started_at = timezone.make_aware(started_at, timezone.get_current_timezone())

    attempt = SnakeGameAttempt.objects.create(
        user=request.user,
        level=level,
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=duration_seconds,
        is_win=is_win,
        lose_reason=lose_reason,
        total_calories=total_calories,
        total_protein=total_protein,
        total_fat=total_fat,
        total_carb=total_carb,
        protein_percent=percentages['protein_percent'],
        fat_percent=percentages['fat_percent'],
        carb_percent=percentages['carb_percent'],
        score=score,
    )

    stats = refresh_snake_user_stats(request.user)

    return JsonResponse(
        {
            'attempt': serialize_snake_attempt(attempt),
            'stats': serialize_snake_stats(stats),
        },
        status=201,
    )


@require_GET
def snake_history_api(request):
    auth_error = _json_auth_required(request)
    if auth_error:
        return auth_error

    attempts = SnakeGameAttempt.objects.filter(user=request.user).select_related('level')[:12]
    stats = SnakeGameUserStats.objects.filter(user=request.user).first()

    return JsonResponse(
        {
            'attempts': [serialize_snake_attempt(attempt) for attempt in attempts],
            'stats': serialize_snake_stats(stats),
        }
    )


@require_GET
def vitamin_game_config_api(request):
    level = _get_or_create_vitamin_level()
    return JsonResponse({'level': serialize_vitamin_level(level, include_products=True)})


@require_POST
def vitamin_game_result_api(request):
    auth_error = _json_auth_required(request)
    if auth_error:
        return auth_error

    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Некорректный JSON.'}, status=400)

    form = VitaminGameResultForm(payload)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)

    cleaned_data = form.cleaned_data
    level = get_object_or_404(VitaminGameLevel.objects.filter(is_active=True), id=cleaned_data['level_id'])

    duration_seconds = cleaned_data['duration_seconds']
    selected_vitamins = cleaned_data['selected_vitamins']
    vitamin_values = {
        vitamin_code: to_decimal(cleaned_data.get(vitamin_code, 0))
        for vitamin_code in VITAMIN_CODE_SET
    }

    detected_lose_reason = _derive_vitamin_lose_reason(
        level,
        vitamin_values=vitamin_values,
        selected_vitamins=selected_vitamins,
    )
    is_win = bool(cleaned_data['is_win']) and not detected_lose_reason
    lose_reason = '' if is_win else (
        detected_lose_reason or cleaned_data.get('lose_reason', '')
    )

    finished_at = timezone.now()
    started_at = cleaned_data.get('started_at') or (finished_at - timedelta(seconds=duration_seconds))
    if timezone.is_naive(started_at):
        started_at = timezone.make_aware(started_at, timezone.get_current_timezone())

    attempt = VitaminGameAttempt.objects.create(
        user=request.user,
        level=level,
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=duration_seconds,
        is_win=is_win,
        lose_reason=lose_reason,
        selected_vitamins=selected_vitamins,
        vitamin_a=vitamin_values['vitamin_a'],
        vitamin_b=vitamin_values['vitamin_b'],
        vitamin_c=vitamin_values['vitamin_c'],
        vitamin_d=vitamin_values['vitamin_d'],
        vitamin_e=vitamin_values['vitamin_e'],
        vitamin_k=vitamin_values['vitamin_k'],
    )

    return JsonResponse({'attempt': serialize_vitamin_attempt(attempt)}, status=201)
