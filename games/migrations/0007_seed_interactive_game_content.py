from django.db import migrations


CALORIE_PRODUCTS = [
    {
        'name': 'Овсяная каша',
        'calories': 88,
        'description': 'Тёплая овсяная каша без сахара.',
    },
    {
        'name': 'Молоко',
        'calories': 52,
        'description': 'Молоко средней жирности.',
    },
    {
        'name': 'Яблоко',
        'calories': 52,
        'description': 'Свежее яблоко.',
    },
    {
        'name': 'Цельнозерновой хлеб',
        'calories': 265,
        'description': 'Хлеб из цельнозерновой муки.',
    },
    {
        'name': 'Куриная грудка',
        'calories': 165,
        'description': 'Запечённая куриная грудка.',
    },
    {
        'name': 'Рис',
        'calories': 130,
        'description': 'Отварной рис.',
    },
    {
        'name': 'Помидоры',
        'calories': 18,
        'description': 'Свежие помидоры.',
    },
    {
        'name': 'Огурцы',
        'calories': 15,
        'description': 'Свежие огурцы.',
    },
]


MENU_PRODUCTS = [
    {
        'name': '🍪 Печенье сдобное',
        'calories': 400,
        'description': 'Продукт для игры (калорийность 400 ккал/100г)',
    },
    {
        'name': '🍯 Мёд',
        'calories': 300,
        'description': 'Продукт для игры (калорийность 300 ккал/100г)',
    },
    {
        'name': '🥣 Каша овсяная',
        'calories': 68,
        'description': 'Овсяная каша для игрового уровня.',
    },
    {
        'name': '🥛 Молоко коровье',
        'calories': 64,
        'description': 'Молоко для игрового уровня.',
    },
    {
        'name': '🧈 Масло сливочное',
        'calories': 717,
        'description': 'Сливочное масло для игрового уровня.',
    },
    {
        'name': '🍎 Яблоко',
        'calories': 52,
        'description': 'Яблоко для игрового уровня.',
    },
    {
        'name': '🍰 Торт',
        'calories': 350,
        'description': 'Продукт для игры (калорийность 350 ккал/100г)',
    },
    {
        'name': '🍟 Картофель фри',
        'calories': 365,
        'description': 'Продукт для игры (калорийность 365 ккал/100г)',
    },
    {
        'name': '🧀 Сыр твёрдый',
        'calories': 400,
        'description': 'Продукт для игры (калорийность 400 ккал/100г)',
    },
    {
        'name': '🍞 Хлеб белый',
        'calories': 265,
        'description': 'Белый хлеб для игрового уровня.',
    },
    {
        'name': '🍗 Курица вареная',
        'calories': 165,
        'description': 'Курица для игрового уровня.',
    },
    {
        'name': '🍅 Помидоры',
        'calories': 18,
        'description': 'Помидоры для игрового уровня.',
    },
    {
        'name': '🥒 Огурцы свежие',
        'calories': 16,
        'description': 'Огурцы для игрового уровня.',
    },
    {
        'name': '🍕 Пицца',
        'calories': 280,
        'description': 'Продукт для игры (калорийность 280 ккал/100г)',
    },
    {
        'name': '🌮 Бутерброд с колбасой',
        'calories': 320,
        'description': 'Продукт для игры (калорийность 320 ккал/100г)',
    },
    {
        'name': '🍰 Двойной торт',
        'calories': 400,
        'description': 'Продукт для игры (калорийность 400 ккал/100г)',
    },
    {
        'name': '🍚 Рис вареный',
        'calories': 130,
        'description': 'Рис для игрового уровня.',
    },
]


MENU_LEVELS = [
    {
        'title': '🟢 Лёгкий завтрак',
        'difficulty': 'easy',
        'description': 'Завтрак 300-330 ккал',
        'target_calories': 310,
        'min_calories': 290,
        'max_calories': 330,
        'product_names': [
            '🍪 Печенье сдобное',
            '🍯 Мёд',
            '🥣 Каша овсяная',
            '🥛 Молоко коровье',
            '🧈 Масло сливочное',
            '🍎 Яблоко',
        ],
    },
    {
        'title': '🟡 Сытный завтрак',
        'difficulty': 'medium',
        'description': 'Завтрак 400-450 ккал',
        'target_calories': 420,
        'min_calories': 400,
        'max_calories': 450,
        'product_names': [
            '🍰 Торт',
            '🍟 Картофель фри',
            '🧀 Сыр твёрдый',
            '🍞 Хлеб белый',
            '🍗 Курица вареная',
            '🍅 Помидоры',
            '🥒 Огурцы свежие',
        ],
    },
    {
        'title': '🔴 Обеденный комбо',
        'difficulty': 'hard',
        'description': 'Обед 700-750 ккал',
        'target_calories': 720,
        'min_calories': 700,
        'max_calories': 750,
        'product_names': [
            '🍕 Пицца',
            '🌮 Бутерброд с колбасой',
            '🍰 Двойной торт',
            '🍞 Хлеб белый',
            '🍗 Курица вареная',
            '🍚 Рис вареный',
            '🍅 Помидоры',
            '🥒 Огурцы свежие',
        ],
    },
]


CALORIE_QUESTIONS = [
    {
        'difficulty': 'easy',
        'products_list': [
            {'name': 'Яблоко', 'quantity': '100 г'},
            {'name': 'Молоко', 'quantity': '200 мл'},
        ],
        'correct_answer': 156,
        'option1': 132,
        'option2': 184,
        'option3': 210,
    },
    {
        'difficulty': 'easy',
        'products_list': [
            {'name': 'Цельнозерновой хлеб', 'quantity': '60 г'},
            {'name': 'Помидоры', 'quantity': '100 г'},
        ],
        'correct_answer': 177,
        'option1': 149,
        'option2': 201,
        'option3': 228,
    },
    {
        'difficulty': 'easy',
        'products_list': [
            {'name': 'Овсяная каша', 'quantity': '180 г'},
            {'name': 'Яблоко', 'quantity': '130 г'},
        ],
        'correct_answer': 226,
        'option1': 198,
        'option2': 246,
        'option3': 270,
    },
    {
        'difficulty': 'easy',
        'products_list': [
            {'name': 'Куриная грудка', 'quantity': '80 г'},
            {'name': 'Огурцы', 'quantity': '100 г'},
        ],
        'correct_answer': 147,
        'option1': 121,
        'option2': 171,
        'option3': 194,
    },
    {
        'difficulty': 'easy',
        'products_list': [
            {'name': 'Рис', 'quantity': '100 г'},
            {'name': 'Помидоры', 'quantity': '100 г'},
            {'name': 'Огурцы', 'quantity': '100 г'},
        ],
        'correct_answer': 163,
        'option1': 139,
        'option2': 188,
        'option3': 214,
    },
    {
        'difficulty': 'medium',
        'products_list': [
            {'name': 'Овсяная каша', 'quantity': '200 г'},
            {'name': 'Молоко', 'quantity': '200 мл'},
            {'name': 'Яблоко', 'quantity': '150 г'},
        ],
        'correct_answer': 358,
        'option1': 332,
        'option2': 384,
        'option3': 408,
        'option4': 436,
    },
    {
        'difficulty': 'medium',
        'products_list': [
            {'name': 'Куриная грудка', 'quantity': '120 г'},
            {'name': 'Рис', 'quantity': '150 г'},
            {'name': 'Огурцы', 'quantity': '150 г'},
        ],
        'correct_answer': 416,
        'option1': 389,
        'option2': 444,
        'option3': 468,
        'option4': 492,
    },
    {
        'difficulty': 'medium',
        'products_list': [
            {'name': 'Цельнозерновой хлеб', 'quantity': '70 г'},
            {'name': 'Яблоко', 'quantity': '150 г'},
            {'name': 'Молоко', 'quantity': '200 мл'},
        ],
        'correct_answer': 368,
        'option1': 340,
        'option2': 392,
        'option3': 421,
        'option4': 446,
    },
    {
        'difficulty': 'medium',
        'products_list': [
            {'name': 'Куриная грудка', 'quantity': '120 г'},
            {'name': 'Цельнозерновой хлеб', 'quantity': '70 г'},
            {'name': 'Помидоры', 'quantity': '150 г'},
        ],
        'correct_answer': 411,
        'option1': 383,
        'option2': 436,
        'option3': 459,
        'option4': 486,
    },
    {
        'difficulty': 'medium',
        'products_list': [
            {'name': 'Овсяная каша', 'quantity': '200 г'},
            {'name': 'Рис', 'quantity': '150 г'},
            {'name': 'Помидоры', 'quantity': '150 г'},
        ],
        'correct_answer': 398,
        'option1': 372,
        'option2': 424,
        'option3': 448,
        'option4': 472,
    },
    {
        'difficulty': 'hard',
        'products_list': [
            {'name': 'Куриная грудка', 'quantity': '130 г'},
            {'name': 'Рис', 'quantity': '155 г'},
            {'name': 'Цельнозерновой хлеб', 'quantity': '100 г'},
        ],
        'correct_answer': 681,
        'option1': 653,
        'option2': 706,
        'option3': 728,
        'option4': 754,
        'option5': 779,
    },
    {
        'difficulty': 'hard',
        'products_list': [
            {'name': 'Овсяная каша', 'quantity': '250 г'},
            {'name': 'Молоко', 'quantity': '250 мл'},
            {'name': 'Цельнозерновой хлеб', 'quantity': '100 г'},
            {'name': 'Яблоко', 'quantity': '200 г'},
        ],
        'correct_answer': 719,
        'option1': 692,
        'option2': 744,
        'option3': 768,
        'option4': 793,
        'option5': 816,
    },
    {
        'difficulty': 'hard',
        'products_list': [
            {'name': 'Куриная грудка', 'quantity': '130 г'},
            {'name': 'Рис', 'quantity': '155 г'},
            {'name': 'Помидоры', 'quantity': '200 г'},
            {'name': 'Огурцы', 'quantity': '200 г'},
        ],
        'correct_answer': 482,
        'option1': 456,
        'option2': 507,
        'option3': 531,
        'option4': 558,
        'option5': 584,
    },
    {
        'difficulty': 'hard',
        'products_list': [
            {'name': 'Цельнозерновой хлеб', 'quantity': '100 г'},
            {'name': 'Молоко', 'quantity': '250 мл'},
            {'name': 'Яблоко', 'quantity': '200 г'},
            {'name': 'Огурцы', 'quantity': '200 г'},
        ],
        'correct_answer': 529,
        'option1': 503,
        'option2': 554,
        'option3': 579,
        'option4': 603,
        'option5': 628,
    },
    {
        'difficulty': 'hard',
        'products_list': [
            {'name': 'Овсяная каша', 'quantity': '250 г'},
            {'name': 'Куриная грудка', 'quantity': '130 г'},
            {'name': 'Рис', 'quantity': '155 г'},
        ],
        'correct_answer': 636,
        'option1': 609,
        'option2': 662,
        'option3': 688,
        'option4': 711,
        'option5': 736,
    },
]


def seed_interactive_content(apps, schema_editor):
    Product = apps.get_model('games', 'Product')
    GameLevel = apps.get_model('games', 'GameLevel')
    CalorieCounterQuestion = apps.get_model('games', 'CalorieCounterQuestion')

    products_by_name = {}
    for item in CALORIE_PRODUCTS + MENU_PRODUCTS:
        product, _ = Product.objects.update_or_create(
            name=item['name'],
            defaults={
                'calories': item['calories'],
                'description': item['description'],
            },
        )
        products_by_name[item['name']] = product

    for item in MENU_LEVELS:
        level, _ = GameLevel.objects.update_or_create(
            title=item['title'],
            difficulty=item['difficulty'],
            defaults={
                'description': item['description'],
                'target_calories': item['target_calories'],
                'min_calories': item['min_calories'],
                'max_calories': item['max_calories'],
            },
        )
        level_products = [products_by_name[name] for name in item['product_names']]
        level.products.set(level_products)

    for item in CALORIE_QUESTIONS:
        lookup = {
            'difficulty': item['difficulty'],
            'correct_answer': item['correct_answer'],
            'products_list': item['products_list'],
        }
        defaults = {
            'option1': item['option1'],
            'option2': item['option2'],
            'option3': item['option3'],
            'option4': item.get('option4'),
            'option5': item.get('option5'),
        }
        CalorieCounterQuestion.objects.update_or_create(**lookup, defaults=defaults)


def unseed_interactive_content(apps, schema_editor):
    Product = apps.get_model('games', 'Product')
    GameLevel = apps.get_model('games', 'GameLevel')
    CalorieCounterQuestion = apps.get_model('games', 'CalorieCounterQuestion')

    GameLevel.objects.filter(
        title__in=[item['title'] for item in MENU_LEVELS]
    ).delete()
    CalorieCounterQuestion.objects.filter(
        correct_answer__in=[item['correct_answer'] for item in CALORIE_QUESTIONS],
        difficulty__in=[item['difficulty'] for item in CALORIE_QUESTIONS],
    ).delete()
    Product.objects.filter(
        name__in=[item['name'] for item in CALORIE_PRODUCTS + MENU_PRODUCTS]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0006_vitamin_game_dynamic_selection'),
    ]

    operations = [
        migrations.RunPython(seed_interactive_content, unseed_interactive_content),
    ]
