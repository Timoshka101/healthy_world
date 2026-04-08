# fooddiary/forms.py
from decimal import Decimal
from django import forms
from django.forms import inlineformset_factory
from .models import Food, Recipe, DiaryEntry, RecipeIngredient, UserSettings, MEAL_CHOICES, ACTIVITY_LEVEL_CHOICES, GOAL_CHOICES
from django.contrib.auth.models import User # Предполагаем, что User находится в django.contrib.auth.models


class CreateFoodForm(forms.ModelForm):
    """Форма для создания нового продукта."""
    class Meta:
        model = Food
        fields = ['name', 'calories_per_100g', 'protein_per_100g', 'fat_per_100g', 'carbohydrate_per_100g']
        labels = {
            'name': 'Название продукта',
            'calories_per_100g': 'Калории на 100г',
            'protein_per_100g': 'Белки на 100г',
            'fat_per_100g': 'Жиры на 100г',
            'carbohydrate_per_100g': 'Углеводы на 100г',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название продукта'}),
            'calories_per_100g': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ккал на 100г', 'step': '0.01'}),
            'protein_per_100g': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Граммы белка на 100г', 'step': '0.01'}),
            'fat_per_100g': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Граммы жиров на 100г', 'step': '0.01'}),
            'carbohydrate_per_100g': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Граммы углеводов на 100г', 'step': '0.01'}),
        }

class AddFoodToDiaryForm(forms.Form):
    """Форма для добавления продукта в дневник питания."""
    food_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.DecimalField(
        max_digits=7, decimal_places=2,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Количество в граммах'}),
        label="Количество (г)"
    )
    meal_type = forms.ChoiceField(
        choices=MEAL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Прием пищи"
    )
    # date будет передаваться через URL или скрытое поле в шаблоне, или дефолтное значение в view
    # date = forms.DateField(widget=forms.HiddenInput()) # Если нужно передавать явно из формы

class RecipeIngredientForm(forms.ModelForm):
    """Форма для отдельного ингредиента при создании рациона."""
    class Meta:
        model = Food
        fields = [] # Мы не хотим редактировать Food напрямую здесь
        # Добавим кастомные поля для выбора Food и quantity
    
    food = forms.ModelChoiceField(
        queryset=Food.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'form-select food-select-in-recipe'}),
        label="Продукт",
        required=False # Ингредиенты могут быть пустыми в formset
    )
    quantity_grams = forms.DecimalField(
        max_digits=7, decimal_places=2,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={'class': 'form-control quantity-input-in-recipe', 'placeholder': 'Граммы'}),
        label="Количество (г)",
        required=False
    )
    meal_type_in_recipe = forms.ChoiceField(
        choices=MEAL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select meal-type-select-in-recipe'}),
        label="Прием пищи",
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        food = cleaned_data.get('food')
        quantity_grams = cleaned_data.get('quantity_grams')

        # Если выбран продукт, но количество не указано, или наоборот
        if food and not quantity_grams:
            self.add_error('quantity_grams', 'Укажите количество для продукта.')
        elif not food and quantity_grams:
            self.add_error('food', 'Выберите продукт для указанного количества.')
        
        return cleaned_data

# Использование formset для динамического добавления ингредиентов в рацион
# Мы создадим динамическую форму для RecipeIngredient, но в шаблоне будем использовать JS для добавления полей.
# Для создания формы рациона с возможностью добавления продуктов на Завтрак, Обед, Ужин
# мы можем использовать Django Formsets. Это удобный способ обрабатывать несколько форм одного типа.

# Создаем базовый класс формы для ингредиента рациона, который будет использоваться в formset
class BaseRecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ['food', 'quantity_grams', 'meal_type_in_recipe']
        widgets = {
            'food': forms.Select(attrs={'class': 'form-select recipe-ingredient-food', 'data-live-search': 'true'}),
            'quantity_grams': forms.NumberInput(attrs={'class': 'form-control recipe-ingredient-quantity', 'placeholder': 'Количество (г)', 'step': '0.01'}),
            'meal_type_in_recipe': forms.Select(attrs={'class': 'form-select recipe-ingredient-meal-type'})
        }
        labels = {
            'food': 'Продукт',
            'quantity_grams': 'Количество (г)',
            'meal_type_in_recipe': 'Прием пищи',
        }


# Создаем formset для RecipeIngredient
# extra=0 означает, что изначально не будет показано пустых форм
# can_delete=True позволяет удалять существующие ингредиенты
RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=BaseRecipeIngredientForm,
    extra=1, # Сколько пустых форм показывать изначально
    can_delete=True
)


class CreateRecipeForm(forms.ModelForm):
    """Основная форма для создания рациона."""
    class Meta:
        model = Recipe
        fields = ['name']
        labels = {
            'name': 'Название рациона',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название рациона'}),
        }

class UserSettingsForm(forms.ModelForm):
    """Форма для настроек пользователя."""
    class Meta:
        model = UserSettings
        fields = ['gender', 'date_of_birth', 'height_cm', 'weight_kg', 'activity_level', 'goal']
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'height_cm': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Например, 175'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Например, 70.5', 'step': '0.01'}),
            'activity_level': forms.Select(attrs={'class': 'form-select'}),
            'goal': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'gender': 'Пол',
            'date_of_birth': 'Дата рождения',
            'height_cm': 'Рост (см)',
            'weight_kg': 'Вес (кг)',
            'activity_level': 'Уровень активности',
            'goal': 'Цель',
        }