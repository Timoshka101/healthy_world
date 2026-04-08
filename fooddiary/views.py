from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Food, DiaryEntry, UserSettings
from datetime import datetime, timedelta
from django.db.models import Sum
import json

@login_required
def fooddiary_home(request):
    selected_date_str = request.GET.get('date', datetime.today().strftime('%Y-%m-%d'))
    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    formatted_date = selected_date.strftime('%d.%m.%Y')

    diary_entries = DiaryEntry.objects.filter(user=request.user, date=selected_date)

    total_nutrition = {'calories': 0, 'protein': 0, 'fat': 0, 'carbohydrate': 0}
    for entry in diary_entries:
        nutrition = entry.calculate_nutrition()
        for key in total_nutrition:
            total_nutrition[key] += nutrition[key]

    user_settings, created = UserSettings.objects.get_or_create(user=request.user)
    if created:
        user_settings.gender = 'male'
        user_settings.birth_date = datetime(1990, 1, 1).date()
        user_settings.height_cm = 170
        user_settings.weight_kg = 70
        user_settings.activity_level = 'sedentary'
        user_settings.goal = 'maintain'
        user_settings.save()

    target_macros = user_settings.calculate_targets()
    target_calories = target_macros['calories']

    # Вычисляем проценты заранее
    progress_percentages = {
        'calories': (total_nutrition['calories'] / target_calories * 100) if target_calories > 0 else 0,
        'protein': (total_nutrition['protein'] / target_macros['protein'] * 100) if target_macros['protein'] > 0 else 0,
        'fat': (total_nutrition['fat'] / target_macros['fat'] * 100) if target_macros['fat'] > 0 else 0,
        'carbohydrate': (total_nutrition['carbohydrate'] / target_macros['carbohydrate'] * 100) if target_macros['carbohydrate'] > 0 else 0,
    }

    context = {
        'formatted_date': formatted_date,
        'selected_date': selected_date,
        'diary_entries': diary_entries,
        'total_nutrition': total_nutrition,
        'target_calories': target_calories,
        'target_macros': target_macros,
        'progress_percentages': progress_percentages,
    }
    return render(request, 'fooddiary/dnevnik_pitaniya.html', context)

@login_required
def search_foods(request):
    query = request.GET.get('q', '')
    foods = Food.objects.filter(name__icontains=query)[:10]
    results = [
        {'id': food.id, 'name': food.name, 'calories': food.calories_per_100g}
        for food in foods
    ]
    return JsonResponse({'results': results})

@login_required
def add_food_to_diary(request):
    if request.method == 'POST':
        food_id = request.POST.get('food_id')
        quantity = float(request.POST.get('quantity'))
        date_str = request.POST.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        food = get_object_or_404(Food, id=food_id)
        DiaryEntry.objects.create(
            user=request.user,
            food=food,
            quantity_grams=quantity,
            date=date
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def create_food(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        calories = float(request.POST.get('calories'))
        protein = float(request.POST.get('protein'))
        fat = float(request.POST.get('fat'))
        carbohydrate = float(request.POST.get('carbohydrate'))

        Food.objects.create(
            name=name,
            calories_per_100g=calories,
            protein_per_100g=protein,
            fat_per_100g=fat,
            carbohydrate_per_100g=carbohydrate
        )
        return JsonResponse({'status': 'success'})
    return render(request, 'fooddiary/modals/create_food_modal.html')

@login_required
def user_settings(request):
    settings = get_object_or_404(UserSettings, user=request.user)
    if request.method == 'POST':
        settings.gender = request.POST.get('gender')
        settings.birth_date = datetime.strptime(request.POST.get('birth_date'), '%Y-%m-%d').date()
        settings.height_cm = int(request.POST.get('height'))
        settings.weight_kg = float(request.POST.get('weight'))
        settings.activity_level = request.POST.get('activity_level')
        settings.goal = request.POST.get('goal')
        settings.save()
        return redirect('fooddiary:fooddiary_home')
    return render(request, 'fooddiary/modals/user_settings_modal.html', {'settings': settings})

@login_required
def delete_entry(request, entry_id):
    entry = get_object_or_404(DiaryEntry, id=entry_id, user=request.user)
    entry.delete()
    return JsonResponse({'status': 'success'})