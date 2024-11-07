from classes import Scene

first = Scene(
    id_='first',
    header='Свинья',
    text='Свинья говорит "Хрю, дай мне свои деньги!"',
    image='boar.jpeg',
    exits=[
        ('Дать свинье денег', ('give', 'invdict.get("Money", 0) >= 10')),
        ('Дать свинье денег', ('gave', '"money-given" in mods')),
        ('Молиться', ('pray', 'True')),
        ('Биться', ('game_over', '"money-given" not in mods')),
        ('Без шансов, свинюшка. (похлопать свинью)', ('pat', '"money-given" not in mods')),
        ('Привет, свинюшка. (похлопать свинью)', ('pat', '"money-given" in mods')),
        ('Подойти к странному мужчине справа', ('hoofd', '"money-given" in mods and "hoofd-met" not in mods')),
        ('Подойти к Хувду', ('hoofd_0', '"hoofd-met" in mods')),
    ],
    if_texts=[
        ('Ты дал свинье денег. Похоже, она счастлива.', '"money-given" in mods'),
    ],
    speaker='Свинья',
    if_speakers=[
        ('', '"money-given" in mods'),
    ]
)

pat = Scene(
    id_='pat',
    header='Хлопать свинью',
    text='Ты похлопываешь свинью. Она говорит "Хрю-хрю-хрю. Деньги."',
    exits=[
        ('Назад', ('first', 'True'))
    ],
    if_texts=[
        ('Ты похлопываешь богатую свинью. Похоже, она счастлива.', '"money-given" in mods'),
    ]
)

game_over = Scene(
    id_='game_over',
    header='Игра окончена',
    text='Ты умер.',
    exits=[
        ('Свинья неизбежна', ('SYS.RESTART', 'player.previous.id_ == "first"')),
        ('Простите, боги', ('SYS.RESTART', 'player.previous.id_ == "pray"')),
        ('Хувд чувствует ложь', ('SYS.RESTART', 'player.previous.id_ == "hoofd_0"')),
    ]
)

give = Scene(
    id_='give',
    header='Дать деньги свинье',
    text='Ты даёшь свинье деньги. Она благодарит тебя.',
    exits=[
        ('Назад', ('first', 'True')),
    ],
    on_enter=[
        (('modifiers', 'add', 'money-given'), 'invdict.get("Money", 0) >= 10 and "money-given" not in mods'),
        (('inventory', 'remove-all', 'Money'), 'invdict.get("Money", 0) >= 10')
    ],
    if_texts=[
        ('У тебя нет денег. Свинья недовольна.', 'invdict.get("Money", 0) == 0'),
        ('Денег недостаточно. Свинья недовольна.', 'invdict.get("Money", 0) < 10'),
    ]
)

gave = Scene(
    id_='gave',
    header='Уже дал свинье деньги',
    text='Ты уже дал свинье деньги. Похоже, она счастлива.',
    exits=[
        ('Назад', ('first', 'True')),
    ]
)

pray = Scene(
    id_='pray',
    header='Молиться',
    text='Ты молишься. Неожиданно, с неба падает монета.',
    exits=[
        ('Молиться снова', ('pray', 'True')),
        ('Назад', ('first', 'True')),
    ],
    on_enter=[
        (('inventory', 'add', 'Money'), 'invdict.get("Money", 0) < 10'),
        (('modifiers', 'add', 'overpray'), 'invdict.get("Money", 0) >= 10 or "money-given" in mods'),
        (('game', 'notify', 'Прощай.'), 'modsdict.get("overpray", 0) > 3'),
        (('game', 'goto', 'game_over'), 'modsdict.get("overpray", 0) > 3'),
    ],
    if_texts=[
        ('Хватит молиться, денег уже достаточно.', 'invdict.get("Money", 0) >= 10 or "money-given" in mods'),
        ('Пожалуйста, хватит.', 'modsdict.get("overpray", 0) > 1'),
    ]
)

hoofd = Scene(
    id_='hoofd',
    header='Странный мужчина справа',
    image='hoofd.jpg',
    text='Ты подошёл к странному мужчине. Заговорить с ним или пойти назад?',
    exits=[
        ('Подойти', ('hoofd_0', 'True')),
        ('Назад', ('first', 'True')),
    ]
)

hoofd_0 = Scene(
    id_='hoofd_0',
    header='Хувд, начальник пилотов',
    image='hoofd.jpg',
    text='Хувд говорит: "Я — начальник пилотов, но все мои пилоты мертвы. Мне нужен пилот. Ты пилот?"',
    exits=[
        ('Да', ('game_over', 'True')),
        ('Нет', ('hoofd_1', 'True')),
    ],
    speaker='Хувд, начальник пилотов',
    on_enter=[
        (('modifiers', 'add', 'hoofd-met'), 'True'),
    ]
)

hoofd_1 = Scene(
    id_='hoofd_1',
    header='Хувд, начальник пилотов',
    image='hoofd.jpg',
    text='Хувд говорит: "Ты не пилот? Тогда ты мне не нужен. Поди прочь."',
    exits=[
        ('Назад', ('first', 'True')),
    ],
    speaker='Хувд, начальник пилотов',
)

GLOBAL_ADDITIONS = [
    ('Денег уже достаточно.', 'invdict.get("Money", 0) >= 10 and player.current.id_ != "give"'),
]

GLOBAL_IMAGES = []

START = 'Начать'
LOAD = 'Загрузить'
SAVE = 'Сохранить'
LOAD_SHORT = 'З'
SAVE_SHORT = 'С'
CREDITS = 'Титры'
EXIT = 'Выход'
LANGUAGE = 'Язык'
SAVED = 'Сохранено'
LOADED = 'Загружено'
RESTART_NEEDED = 'Некоторые изменения вступят в силу только после перезапуска игры.'
