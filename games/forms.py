from django import forms
from .models import Product, GameLevel, SnakeGameAttempt, VitaminGameAttempt
from .vitamin_game_config import VITAMIN_CODE_SET, VITAMIN_GAME_SELECTION_SIZE


class MenuBuilderForm(forms.Form):
    """Форма для выбора продуктов в игре 'Собери здоровое меню'"""
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Выберите продукты"
    )


class CalorieCounterAnswerForm(forms.Form):
    """Форма для ответов в игре 'Подсчитай калории'"""
    ANSWER_CHOICES = []
    
    answer = forms.ChoiceField(
        widget=forms.RadioSelect,
        label="Выберите правильное количество калорий",
        required=True
    )
    
    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [
            (question.correct_answer, f"{question.correct_answer} ккал"),
            (question.option1, f"{question.option1} ккал"),
            (question.option2, f"{question.option2} ккал"),
            (question.option3, f"{question.option3} ккал"),
        ]
        
        # Добавляем option4 и option5, если они есть
        if question.option4:
            choices.append((question.option4, f"{question.option4} ккал"))
        if question.option5:
            choices.append((question.option5, f"{question.option5} ккал"))
        
        # Перемешиваем варианты ответов
        import random
        random.shuffle(choices)
        self.fields['answer'].choices = choices


class SnakeGameResultForm(forms.Form):
    """Валидирует результат прохождения игры 'Змейка' из frontend."""

    level_id = forms.IntegerField(min_value=1)
    is_win = forms.BooleanField(required=False)
    lose_reason = forms.ChoiceField(
        required=False,
        choices=[('', '---------')] + SnakeGameAttempt.LOSE_REASON_CHOICES,
    )
    total_calories = forms.IntegerField(min_value=0)
    total_protein = forms.FloatField(min_value=0)
    total_fat = forms.FloatField(min_value=0)
    total_carb = forms.FloatField(min_value=0)
    protein_percent = forms.FloatField(min_value=0, max_value=100, required=False)
    fat_percent = forms.FloatField(min_value=0, max_value=100, required=False)
    carb_percent = forms.FloatField(min_value=0, max_value=100, required=False)
    duration_seconds = forms.IntegerField(min_value=0)
    started_at = forms.DateTimeField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        is_win = cleaned_data.get('is_win')
        lose_reason = cleaned_data.get('lose_reason')

        if is_win and lose_reason:
            self.add_error('lose_reason', 'У победной попытки не может быть причины поражения.')

        if not is_win and not lose_reason:
            self.add_error('lose_reason', 'Укажите причину поражения.')

        return cleaned_data


class VitaminGameResultForm(forms.Form):
    """Валидирует результат прохождения игры 'Баланс витаминов'."""

    level_id = forms.IntegerField(min_value=1)
    is_win = forms.BooleanField(required=False)
    lose_reason = forms.ChoiceField(
        required=False,
        choices=[('', '---------')] + VitaminGameAttempt.LOSE_REASON_CHOICES,
    )
    selected_vitamins = forms.JSONField()
    vitamin_a = forms.FloatField(min_value=0, max_value=100, required=False)
    vitamin_b = forms.FloatField(min_value=0, max_value=100, required=False)
    vitamin_c = forms.FloatField(min_value=0, max_value=100, required=False)
    vitamin_d = forms.FloatField(min_value=0, max_value=100, required=False)
    vitamin_e = forms.FloatField(min_value=0, max_value=100, required=False)
    vitamin_k = forms.FloatField(min_value=0, max_value=100, required=False)
    duration_seconds = forms.IntegerField(min_value=0)
    started_at = forms.DateTimeField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        is_win = cleaned_data.get('is_win')
        lose_reason = cleaned_data.get('lose_reason')
        selected_vitamins = cleaned_data.get('selected_vitamins') or []

        if is_win and lose_reason:
            self.add_error('lose_reason', 'У победной попытки не может быть причины поражения.')

        if not is_win and not lose_reason:
            self.add_error('lose_reason', 'Укажите причину поражения.')

        if not isinstance(selected_vitamins, list):
            self.add_error('selected_vitamins', 'Выбор витаминов должен передаваться списком.')
            return cleaned_data

        cleaned_codes = []
        for code in selected_vitamins:
            if code not in VITAMIN_CODE_SET:
                self.add_error('selected_vitamins', 'Передан неизвестный витамин.')
                return cleaned_data
            if code not in cleaned_codes:
                cleaned_codes.append(code)

        if len(cleaned_codes) != VITAMIN_GAME_SELECTION_SIZE:
            self.add_error(
                'selected_vitamins',
                f'Нужно выбрать ровно {VITAMIN_GAME_SELECTION_SIZE} витамина.',
            )
            return cleaned_data

        cleaned_data['selected_vitamins'] = cleaned_codes

        for vitamin_code in VITAMIN_CODE_SET:
            cleaned_data[vitamin_code] = cleaned_data.get(vitamin_code, 0) or 0

        return cleaned_data
