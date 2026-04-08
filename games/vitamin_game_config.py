VITAMIN_GAME_DEFAULT_LEVEL = {
    'code': 'vitamin-balance',
    'title': 'Баланс витаминов',
    'time_limit_seconds': 30,
    'start_value': 55,
    'normal_min_value': 40,
    'normal_max_value': 70,
    'min_critical_value': 20,
    'max_critical_value': 90,
    'drain_per_second': 5.60,
}


VITAMIN_GAME_VITAMINS = [
    {
        'code': 'vitamin_a',
        'label': 'Витамин A',
        'display_name': 'Витамин A',
        'short_label': 'A',
    },
    {
        'code': 'vitamin_c',
        'label': 'Витамин C',
        'display_name': 'Витамин C',
        'short_label': 'C',
    },
    {
        'code': 'vitamin_d',
        'label': 'Витамин D',
        'display_name': 'Витамин D',
        'short_label': 'D',
    },
    {
        'code': 'vitamin_e',
        'label': 'Витамин E',
        'display_name': 'Витамин E',
        'short_label': 'E',
    },
    {
        'code': 'vitamin_k',
        'label': 'Витамин K',
        'display_name': 'Витамин K',
        'short_label': 'K',
    },
    {
        'code': 'vitamin_b',
        'label': 'Витамин B',
        'display_name': 'Витамин B',
        'short_label': 'B',
    },
]

VITAMIN_GAME_DEFAULT_SELECTION = ['vitamin_a', 'vitamin_c', 'vitamin_d']
VITAMIN_GAME_SELECTION_SIZE = 3

VITAMIN_LABELS = {
    vitamin['code']: vitamin['display_name']
    for vitamin in VITAMIN_GAME_VITAMINS
}
VITAMIN_SHORT_LABELS = {
    vitamin['code']: vitamin['short_label']
    for vitamin in VITAMIN_GAME_VITAMINS
}
VITAMIN_CODE_SET = {vitamin['code'] for vitamin in VITAMIN_GAME_VITAMINS}


VITAMIN_GAME_PRODUCTS = [
    {
        'code': 'butter',
        'label': 'Сливочное масло',
        'emoji': '🧈',
        'vitamin_code': 'vitamin_a',
        'boost': 15,
        'strength': 'strong',
        'description': 'Сильно поднимает витамин A.',
    },
    {
        'code': 'carrot',
        'label': 'Морковь',
        'emoji': '🥕',
        'vitamin_code': 'vitamin_a',
        'boost': 8,
        'strength': 'light',
        'description': 'Мягко поднимает витамин A.',
    },
    {
        'code': 'pepper',
        'label': 'Болгарский перец',
        'emoji': '🫑',
        'vitamin_code': 'vitamin_c',
        'boost': 15,
        'strength': 'strong',
        'description': 'Сильно поднимает витамин C.',
    },
    {
        'code': 'orange',
        'label': 'Апельсин',
        'emoji': '🍊',
        'vitamin_code': 'vitamin_c',
        'boost': 8,
        'strength': 'light',
        'description': 'Мягко поднимает витамин C.',
    },
    {
        'code': 'salmon',
        'label': 'Лосось',
        'emoji': '🐟',
        'vitamin_code': 'vitamin_d',
        'boost': 15,
        'strength': 'strong',
        'description': 'Сильно поднимает витамин D.',
    },
    {
        'code': 'egg',
        'label': 'Яйцо',
        'emoji': '🥚',
        'vitamin_code': 'vitamin_d',
        'boost': 8,
        'strength': 'light',
        'description': 'Мягко поднимает витамин D.',
    },
    {
        'code': 'seeds',
        'label': 'Семечки',
        'emoji': '🌻',
        'vitamin_code': 'vitamin_e',
        'boost': 15,
        'strength': 'strong',
        'description': 'Сильно поднимает витамин E.',
    },
    {
        'code': 'avocado',
        'label': 'Авокадо',
        'emoji': '🥑',
        'vitamin_code': 'vitamin_e',
        'boost': 8,
        'strength': 'light',
        'description': 'Мягко поднимает витамин E.',
    },
    {
        'code': 'spinach',
        'label': 'Шпинат',
        'emoji': '🥬',
        'vitamin_code': 'vitamin_k',
        'boost': 15,
        'strength': 'strong',
        'description': 'Сильно поднимает витамин K.',
    },
    {
        'code': 'broccoli',
        'label': 'Брокколи',
        'emoji': '🥦',
        'vitamin_code': 'vitamin_k',
        'boost': 8,
        'strength': 'light',
        'description': 'Мягко поднимает витамин K.',
    },
    {
        'code': 'wholegrain_bread',
        'label': 'Цельнозерновой хлеб',
        'emoji': '🍞',
        'vitamin_code': 'vitamin_b',
        'boost': 15,
        'strength': 'strong',
        'description': 'Сильно поднимает витамин B.',
    },
    {
        'code': 'banana',
        'label': 'Банан',
        'emoji': '🍌',
        'vitamin_code': 'vitamin_b',
        'boost': 8,
        'strength': 'light',
        'description': 'Мягко поднимает витамин B.',
    },
]


VITAMIN_GAME_LOSE_REASON_LABELS = {
    'vitamin_a_low': 'Авитаминоз по витамину A',
    'vitamin_c_low': 'Авитаминоз по витамину C',
    'vitamin_d_low': 'Авитаминоз по витамину D',
    'vitamin_e_low': 'Авитаминоз по витамину E',
    'vitamin_k_low': 'Авитаминоз по витамину K',
    'vitamin_b_low': 'Авитаминоз по витамину B',
    'vitamin_a_high': 'Гипервитаминоз по витамину A',
    'vitamin_c_high': 'Гипервитаминоз по витамину C',
    'vitamin_d_high': 'Гипервитаминоз по витамину D',
    'vitamin_e_high': 'Гипервитаминоз по витамину E',
    'vitamin_k_high': 'Гипервитаминоз по витамину K',
    'vitamin_b_high': 'Гипервитаминоз по витамину B',
}
