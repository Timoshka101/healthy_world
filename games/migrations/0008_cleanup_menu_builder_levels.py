from django.db import migrations


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


def cleanup_menu_builder_levels(apps, schema_editor):
    Product = apps.get_model('games', 'Product')
    GameLevel = apps.get_model('games', 'GameLevel')
    UserGameResult = apps.get_model('games', 'UserGameResult')

    products_by_name = {}
    for item in MENU_PRODUCTS:
        product, _ = Product.objects.update_or_create(
            name=item['name'],
            defaults={
                'calories': item['calories'],
                'description': item['description'],
            },
        )
        products_by_name[item['name']] = product

    canonical_by_difficulty = {}
    canonical_ids = []

    for item in MENU_LEVELS:
        existing = GameLevel.objects.filter(
            title=item['title'],
            difficulty=item['difficulty'],
        ).order_by('id').first()

        if existing is None:
            existing = GameLevel.objects.create(
                title=item['title'],
                difficulty=item['difficulty'],
                description=item['description'],
                target_calories=item['target_calories'],
                min_calories=item['min_calories'],
                max_calories=item['max_calories'],
            )
        else:
            existing.description = item['description']
            existing.target_calories = item['target_calories']
            existing.min_calories = item['min_calories']
            existing.max_calories = item['max_calories']
            existing.save(
                update_fields=[
                    'description',
                    'target_calories',
                    'min_calories',
                    'max_calories',
                ]
            )

        existing.products.set([products_by_name[name] for name in item['product_names']])
        canonical_by_difficulty[item['difficulty']] = existing
        canonical_ids.append(existing.id)

    obsolete_levels = list(
        GameLevel.objects.exclude(id__in=canonical_ids).filter(
            difficulty__in=canonical_by_difficulty.keys()
        )
    )

    for level in obsolete_levels:
        replacement = canonical_by_difficulty.get(level.difficulty)
        if replacement is not None:
            UserGameResult.objects.filter(level_id=level.id).update(level_id=replacement.id)

    if obsolete_levels:
        GameLevel.objects.filter(id__in=[level.id for level in obsolete_levels]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0007_seed_interactive_game_content'),
    ]

    operations = [
        migrations.RunPython(cleanup_menu_builder_levels, migrations.RunPython.noop),
    ]
