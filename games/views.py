from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Case, IntegerField, Max, Value, When
from django.urls import reverse
import random

from .models import (
    CalorieCounterQuestion,
    GameLevel,
    Product,
    SnakeGameAttempt,
    SnakeGameUserStats,
    UserGameResult,
    VitaminGameAttempt,
)
from .forms import MenuBuilderForm, CalorieCounterAnswerForm
from .serializers import serialize_snake_stats


def format_difficulty(difficulty):
    """Преобразует сложность в красивый формат с эмодзи и цветными бейджами"""
    if not difficulty:
        return '-'
    
    difficulty_map = {
        'easy': ('🟢 Лёгкий уровень', 'success', 'Легко'),
        'medium': ('🟡 Средний уровень', 'warning', 'Средне'),
        'hard': ('🔴 Сложный уровень', 'danger', 'Сложно'),
    }
    
    if difficulty not in difficulty_map:
        return difficulty
    
    emoji_text, badge_color, label = difficulty_map[difficulty]
    # Возвращаем кортеж для использования в шаблоне
    return {
        'emoji_text': emoji_text,
        'badge_color': badge_color,
        'label': label,
    }


def games_home(request):
    """Главная страница раздела игр с основной игрой 'Змейка'."""
    context = {
        'user_stats': None,
        'snake_stats': None,
        'vitamin_stats': None,
        'snake_frontend_config': {
            'api': {
                'levels': reverse('snake_levels_api'),
                'history': reverse('snake_history_api'),
                'result': reverse('snake_result_api'),
                'vitamin_config': reverse('vitamin_game_config_api'),
                'vitamin_result': reverse('vitamin_game_result_api'),
            },
            'user': {
                'is_authenticated': request.user.is_authenticated,
                'username': request.user.username if request.user.is_authenticated else '',
            },
        },
    }
    
    if request.user.is_authenticated:
        menu_results = UserGameResult.objects.filter(
            user=request.user,
            game_type='menu_builder'
        )
        calorie_results = UserGameResult.objects.filter(
            user=request.user,
            game_type='calorie_counter'
        )
        snake_attempts = SnakeGameAttempt.objects.filter(user=request.user)
        vitamin_attempts = VitaminGameAttempt.objects.filter(user=request.user)
        snake_stats = SnakeGameUserStats.objects.filter(user=request.user).first()
        vitamin_total = vitamin_attempts.count()
        vitamin_wins = vitamin_attempts.filter(is_win=True).count()
        vitamin_best_duration = vitamin_attempts.aggregate(best=Max('duration_seconds'))['best'] or 0
        
        context['user_stats'] = {
            'snake_wins': snake_attempts.filter(is_win=True).count(),
            'snake_total': snake_attempts.count(),
            'vitamin_wins': vitamin_wins,
            'vitamin_total': vitamin_total,
            'menu_wins': menu_results.filter(is_won=True).count(),
            'menu_total': menu_results.count(),
            'calorie_wins': calorie_results.filter(is_won=True).count(),
            'calorie_total': calorie_results.count(),
        }
        context['snake_stats'] = serialize_snake_stats(snake_stats)
        context['vitamin_stats'] = {
            'total_attempts': vitamin_total,
            'total_wins': vitamin_wins,
            'win_rate': int(round((vitamin_wins / vitamin_total) * 100)) if vitamin_total else 0,
            'best_duration': vitamin_best_duration,
        }
    
    return render(request, 'games/games_home.html', context)


@login_required(login_url='users:login')
def menu_builder_levels(request):
    """Выбор уровня сложности для игры 'Собери здоровое меню'"""
    levels = GameLevel.objects.order_by(
        Case(
            When(difficulty='easy', then=Value(1)),
            When(difficulty='medium', then=Value(2)),
            When(difficulty='hard', then=Value(3)),
            default=Value(99),
            output_field=IntegerField(),
        ),
        'id',
    )
    
    context = {
        'levels': levels,
        'game_type': 'menu_builder'
    }
    
    return render(request, 'games/menu_builder_levels.html', context)


@login_required(login_url='users:login')
def menu_builder_game(request, level_id):
    """Игра 'Собери здоровое меню'"""
    level = get_object_or_404(GameLevel, id=level_id)
    products = level.products.all()
    
    if request.method == 'POST':
        selected_product_ids = request.POST.getlist('products')
        selected_products = Product.objects.filter(id__in=selected_product_ids)
        
        # Подсчитываем общую калорийность. В базе `Product.calories` считается как ккал на 100 г.
        import re

        # Функция для извлечения граммовки из названия продукта
        def _parse_grams_from_name(name):
            if not name:
                return None
            m = re.search(r"(\d+)\s?г", name)
            if m:
                try:
                    return int(m.group(1))
                except:
                    return None
            # Частные случаи: "2 ломтика" и т.д.
            if '2 лом' in name.lower() or '2 ломтика' in name.lower():
                return 60
            if '1 шт' in name.lower() or '1 шт' in name.lower():
                return 60
            return None

        # Граммовки по умолчанию зависят от уровня
        if level.difficulty == 'easy':
            # Лёгкий завтрак: маленькие порции (290-330 ккал)
            default_grams_map = {
                'каша': 180,
                'молоко': 180,
                'яблоко': 130,
                'хлеб': 50,
                'курица': 80,
                'рис': 100,
                'помидоры': 100,
                'огурцы': 100,
            }
        elif level.difficulty == 'medium':
            # Сытный завтрак: средние порции (400-450 ккал)
            default_grams_map = {
                'каша': 200,
                'молоко': 200,
                'яблоко': 150,
                'хлеб': 70,
                'курица': 120,
                'рис': 150,
                'помидоры': 150,
                'огурцы': 150,
            }
        else:
            # Обеденный комбо: большие порции (700-750 ккал)
            default_grams_map = {
                'каша': 250,
                'молоко': 250,
                'яблоко': 200,
                'хлеб': 100,
                'курица': 130,
                'рис': 155,
                'помидоры': 200,
                'огурцы': 200,
            }

        total_calories = 0
        for p in selected_products:
            grams = _parse_grams_from_name(p.name)
            
            # Если граммовка не найдена в названии, ищем по ключевым словам
            if not grams:
                product_name_lower = p.name.lower()
                for key, default_g in default_grams_map.items():
                    if key in product_name_lower:
                        grams = default_g
                        break
            
            if grams:
                total_calories += int(round(p.calories * grams / 100.0))
            else:
                # Если граммовка всё ещё не найдена, используем 100г по умолчанию
                total_calories += int(round(p.calories * 100 / 100.0))
        
        # Проверяем, уложились ли в диапазон
        is_won = level.min_calories <= total_calories <= level.max_calories
        
        # Вычисляем очки
        score = 0
        if is_won:
            # Чем ближе к целевому значению, тем больше очков
            diff = abs(total_calories - level.target_calories)
            max_diff = level.max_calories - level.target_calories
            if max_diff > 0:
                score = max(0, 100 - int((diff / max_diff) * 100))
            else:
                score = 100
        
        # Сохраняем результат
        result = UserGameResult.objects.create(
            user=request.user,
            game_type='menu_builder',
            level=level,
            total_calories=total_calories,
            is_won=is_won,
            score=score
        )
        
        context = {
            'level': level,
            'result': result,
            'total_calories': total_calories,
            'selected_products': selected_products,
        }
        
        return render(request, 'games/menu_builder_result.html', context)
    
    # Подготавливаем информацию о граммовках и калории для каждого продукта
    if level.difficulty == 'easy':
        default_grams_map = {
            'каша': 180, 'молоко': 180, 'яблоко': 130, 'хлеб': 50,
            'курица': 80, 'рис': 100, 'помидоры': 100, 'огурцы': 100,
        }
    elif level.difficulty == 'medium':
        default_grams_map = {
            'каша': 200, 'молоко': 200, 'яблоко': 150, 'хлеб': 70,
            'курица': 120, 'рис': 150, 'помидоры': 150, 'огурцы': 150,
        }
    else:
        default_grams_map = {
            'каша': 250, 'молоко': 250, 'яблоко': 200, 'хлеб': 100,
            'курица': 130, 'рис': 155, 'помидоры': 200, 'огурцы': 200,
        }
    
    # Для каждого продукта рассчитываем его вклад в калории
    products_with_calories = []
    for p in products:
        grams = None
        product_name_lower = p.name.lower()
        for key, default_g in default_grams_map.items():
            if key in product_name_lower:
                grams = default_g
                break
        if not grams:
            grams = 100
        
        calculated_calories = int(round(p.calories * grams / 100.0))
        products_with_calories.append({
            'product': p,
            'grams': grams,
            'calculated_calories': calculated_calories,
        })
    
    context = {
        'level': level,
        'products': products,
        'products_with_calories': products_with_calories,
        'form': MenuBuilderForm(initial={'products': products})
    }
    
    return render(request, 'games/menu_builder_game.html', context)


@login_required(login_url='users:login')
def calorie_counter_levels(request):
    """Выбор сложности для игры 'Подсчитай калории'"""
    difficulties = [
        ('easy', 'Легко'),
        ('medium', 'Средне'),
        ('hard', 'Сложно'),
    ]
    
    context = {
        'difficulties': difficulties,
        'game_type': 'calorie_counter'
    }
    
    return render(request, 'games/calorie_counter_levels.html', context)


@login_required(login_url='users:login')
def calorie_counter_game(request, difficulty='medium'):
    """Игра 'Подсчитай калории'"""
    # Получаем вопросы выбранной сложности
    questions = list(CalorieCounterQuestion.objects.filter(difficulty=difficulty))
    
    if not questions:
        # Если вопросов нет, создаем сообщение об ошибке
        context = {'error': 'Вопросы для этого уровня сложности еще не созданы'}
        return render(request, 'games/calorie_counter_game.html', context)
    
    # Если это первый запрос, инициализируем сессию
    if 'current_question_index' not in request.session or request.session.get('game_difficulty') != difficulty:
        request.session['current_question_index'] = 0
        request.session['game_difficulty'] = difficulty
        request.session['correct_answers'] = 0
        request.session['total_questions'] = min(5, len(questions))  # 5 вопросов за раунд
        request.session['game_questions'] = [q.id for q in random.sample(questions, request.session['total_questions'])]
        # Инициализация для хранения отображённых вариантов и ответов
        request.session['displayed_choices'] = []
        request.session['answers'] = []
    
    current_index = request.session.get('current_question_index', 0)
    game_questions = request.session.get('game_questions', [])
    total_questions = request.session.get('total_questions', 0)
    
    # Проверяем, завершена ли игра
    if current_index >= total_questions:
        # Игра завершена, сохраняем результат
        correct_answers = request.session.get('correct_answers', 0)
        score = int((correct_answers / total_questions) * 100)
        is_won = correct_answers >= total_questions * 0.6  # Победа при 60%+ правильных ответов

        result = UserGameResult.objects.create(
            user=request.user,
            game_type='calorie_counter',
            is_won=is_won,
            difficulty=difficulty,
            score=score
        )

        # Получаем подробности ответов и очищаем сессионные данные
        answers = request.session.get('answers', [])

        for k in ['current_question_index', 'game_difficulty', 'correct_answers', 'total_questions', 'game_questions', 'displayed_choices', 'answers']:
            if k in request.session:
                del request.session[k]

        context = {
            'result': result,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'difficulty': difficulty,
            'answers': answers,
        }

        return render(request, 'games/calorie_counter_result.html', context)
    
    # Получаем текущий вопрос
    current_question_id = game_questions[current_index]
    question = get_object_or_404(CalorieCounterQuestion, id=current_question_id)

    # Подготовка подсказок по калориям на 100г для каждого продукта в вопросе
    def _parse_grams(s):
        import re
        if not s:
            return None
        m = re.search(r"(\d+)", s)
        if m:
            try:
                return int(m.group(1))
            except:
                return None
        return None

    product_hints = []
    all_products = list(Product.objects.all())
    for pinfo in question.products_list:
        display_name = pinfo.get('name', '')
        quantity = pinfo.get('quantity', '')

        # Убираем эмодзи и лишние пробелы для сравнения
        import re
        raw = re.sub(r"^[^\wА-Яа-яЁё]+", "", display_name).strip()
        raw_lower = raw.lower()

        matched = None
        for prod in all_products:
            prod_name_norm = prod.name.lower()
            if raw_lower in prod_name_norm or prod_name_norm in raw_lower:
                matched = prod
                break

        # В БД Product.calories уже в kcal/100g
        per100 = matched.calories if matched else None

        product_hints.append({
            'display_name': display_name,
            'quantity': quantity,
            'per_100': per100,
        })
    
    if request.method == 'POST':
        form = CalorieCounterAnswerForm(question, request.POST)
        if form.is_valid():
            answer = int(form.cleaned_data['answer'])

            # Получаем отображённые варианты для этого вопроса (если были сохранены)
            try:
                displayed = request.session.get('displayed_choices', [])[current_index]
            except Exception:
                displayed = None

            # Собираем подробности по продуктам и считаем итоговую калорийность по базе
            def _parse_grams(s):
                import re
                if not s:
                    return None
                m = re.search(r"(\d+)", s)
                if m:
                    try:
                        return int(m.group(1))
                    except:
                        return None
                return None

            product_details = []
            all_products = list(Product.objects.all())
            computed_total = 0
            import re
            for pinfo in question.products_list:
                display_name = pinfo.get('name', '')
                quantity = pinfo.get('quantity', '')

                raw = re.sub(r"^[^\wА-Яа-яЁё]+", "", display_name).strip()
                raw_lower = raw.lower()

                matched = None
                for prod in all_products:
                    prod_name_norm = prod.name.lower()
                    if raw_lower in prod_name_norm or prod_name_norm in raw_lower:
                        matched = prod
                        break

                grams = _parse_grams(quantity)
                # В БД Product.calories уже в kcal/100g
                per100 = matched.calories if matched else None

                calc = None
                if per100 and grams:
                    calc = int(round(per100 * grams / 100.0))
                    computed_total += calc

                product_details.append({
                    'display_name': display_name,
                    'quantity': quantity,
                    'per_100': per100,
                    'calc': calc,
                })

            # Сохраняем запись об ответе
            ans_record = {
                'question_id': question.id,
                'products': product_details,
                'displayed_choices': displayed,
                'selected': answer,
                'correct': question.correct_answer,
                'computed_total': computed_total,
            }
            answers = request.session.get('answers', [])
            answers.append(ans_record)
            request.session['answers'] = answers

            # Проверяем правильность ответа
            if answer == question.correct_answer:
                request.session['correct_answers'] = request.session.get('correct_answers', 0) + 1

            # Переходим к следующему вопросу
            request.session['current_question_index'] = current_index + 1

            return redirect('calorie_counter_game', difficulty=difficulty)
    else:
        form = CalorieCounterAnswerForm(question)
        # Сохраняем отображённые варианты для текущего вопроса в сессии
        try:
            displayed = form.fields['answer'].choices
        except Exception:
            displayed = None
        dc = request.session.get('displayed_choices', [])
        if len(dc) <= current_index:
            dc.extend([None] * (current_index - len(dc) + 1))
        dc[current_index] = displayed
        request.session['displayed_choices'] = dc

    context = {
        'question': question,
        'form': form,
        'current_question': current_index + 1,
        'total_questions': total_questions,
        'difficulty': difficulty,
        'product_hints': product_hints,
    }

    return render(request, 'games/calorie_counter_game.html', context)


@login_required(login_url='users:login')
def user_statistics(request):
    """Страница со статистикой пользователя"""
    menu_qs = UserGameResult.objects.filter(
        user=request.user,
        game_type='menu_builder'
    )
    calorie_qs = UserGameResult.objects.filter(
        user=request.user,
        game_type='calorie_counter'
    )
    snake_qs = SnakeGameAttempt.objects.filter(user=request.user).select_related('level')
    vitamin_qs = VitaminGameAttempt.objects.filter(user=request.user).select_related('level')

    menu_total = menu_qs.count()
    menu_wins = menu_qs.filter(is_won=True).count()
    menu_winrate = int(round((menu_wins / menu_total) * 100)) if menu_total > 0 else 0
    menu_avg_score = int(round(menu_qs.aggregate(avg=Avg('score'))['avg'] or 0))

    calorie_total = calorie_qs.count()
    calorie_wins = calorie_qs.filter(is_won=True).count()
    calorie_winrate = int(round((calorie_wins / calorie_total) * 100)) if calorie_total > 0 else 0
    calorie_avg_score = int(round(calorie_qs.aggregate(avg=Avg('score'))['avg'] or 0))

    snake_total = snake_qs.count()
    snake_wins = snake_qs.filter(is_win=True).count()
    snake_winrate = int(round((snake_wins / snake_total) * 100)) if snake_total > 0 else 0
    snake_avg_score = int(round(snake_qs.aggregate(avg=Avg('score'))['avg'] or 0))

    vitamin_total = vitamin_qs.count()
    vitamin_wins = vitamin_qs.filter(is_win=True).count()
    vitamin_winrate = int(round((vitamin_wins / vitamin_total) * 100)) if vitamin_total > 0 else 0
    vitamin_avg_duration = int(round(vitamin_qs.aggregate(avg=Avg('duration_seconds'))['avg'] or 0))

    menu_results = menu_qs.order_by('-completed_at')[:10]
    calorie_results = calorie_qs.order_by('-completed_at')[:10]
    snake_results = snake_qs.order_by('-finished_at')[:10]
    vitamin_results = vitamin_qs.order_by('-finished_at')[:10]

    for result in calorie_results:
        result.formatted_difficulty = format_difficulty(result.difficulty)

    context = {
        'snake_results': snake_results,
        'snake_total': snake_total,
        'snake_wins': snake_wins,
        'snake_winrate': snake_winrate,
        'snake_avg_score': snake_avg_score,
        'vitamin_results': vitamin_results,
        'vitamin_total': vitamin_total,
        'vitamin_wins': vitamin_wins,
        'vitamin_winrate': vitamin_winrate,
        'vitamin_avg_duration': vitamin_avg_duration,
        'menu_results': menu_results,
        'calorie_results': calorie_results,
        'menu_total': menu_total,
        'menu_wins': menu_wins,
        'menu_winrate': menu_winrate,
        'menu_avg_score': menu_avg_score,
        'calorie_total': calorie_total,
        'calorie_wins': calorie_wins,
        'calorie_winrate': calorie_winrate,
        'calorie_avg_score': calorie_avg_score,
    }

    return render(request, 'games/user_statistics.html', context)
