from classes import Scene

first = Scene(
    id_='first',
    header='Pig',
    text='Pig says "Oink, give me your money!"',
    image='boar.jpeg',
    exits=[
        ('Give the pig money', ('give', 'invdict.get("Money", 0) >= 10')),
        ('Give the pig money', ('gave', '"money-given" in mods')),
        ('Pray', ('pray', 'True')),
        ('Fight the pig', ('game_over', '"money-given" not in mods')),
        ('No way, piggy. (pat the pig)', ('pat', '"money-given" not in mods')),
        ('Hello, piggy. (pat the pig)', ('pat', '"money-given" in mods')),
        ('Approach the strange man on the right', ('hoofd', '"money-given" in mods and "hoofd-met" not in mods')),
        ('Approach Hoofd', ('hoofd_0', '"hoofd-met" in mods')),
    ],
    if_texts=[
        ('You gave the pig your money. It seems happy.', '"money-given" in mods'),
    ],
    speaker='Pig',
    if_speakers=[
        ('', '"money-given" in mods'),
    ]
)

pat = Scene(
    id_='pat',
    header='Pat the pig',
    text='You pat the pig. It says "Oink, oink, oink. Money."',
    exits=[
        ('Back', ('first', 'True'))
    ],
    if_texts=[
        ('You pat the rich pig. It seems happy.', '"money-given" in mods'),
    ]
)

game_over = Scene(
    id_='over',
    header='Game Over',
    text='You died.',
    exits=[
        ('Pig is unavoidable', ('SYS.RESTART', 'player.previous.id_ == "first"')),
        ('Sorry, gods', ('SYS.RESTART', 'player.previous.id_ == "pray"')),
        ('Hoofd sees lies', ('SYS.RESTART', 'player.previous.id_ == "hoofd_0"')),
    ]
)

give = Scene(
    id_='give',
    header='Give the pig money',
    text='You give the pig your money. It says "Thank you!"',
    exits=[
        ('Back', ('first', 'True')),
    ],
    on_enter=[
        (('modifiers', 'add', 'money-given'), 'invdict.get("Money", 0) >= 10 and "money-given" not in mods'),
        (('inventory', 'remove-all', 'Money'), 'invdict.get("Money", 0) >= 10')
    ],
    if_texts=[
        ('You have no money to give. Pig is unhappy.', 'invdict.get("Money", 0) == 0'),
        ('Not enough money to give. Pig is unhappy.', 'invdict.get("Money", 0) < 10'),
    ]
)

gave = Scene(
    id_='gave',
    header='Already gave the pig money',
    text='You already gave the pig your money. It seems happy.',
    exits=[
        ('Back', ('first', 'True')),
    ]
)

pray = Scene(
    id_='pray',
    header='Pray',
    text='You pray. Unexpectedly, a gold coin falls from the sky.',
    exits=[
        ('Pray more', ('pray', 'True')),
        ('Back', ('first', 'True')),
    ],
    on_enter=[
        (('inventory', 'add', 'Money'), 'invdict.get("Money", 0) < 10'),
        (('modifiers', 'add', 'overpray'), 'invdict.get("Money", 0) >= 10 or "money-given" in mods'),
        (('game', 'notify', 'Goodbye.'), 'modsdict.get("overpray", 0) > 3'),
        (('game', 'goto', 'game_over'), 'modsdict.get("overpray", 0) > 3'),
    ],
    if_texts=[
        ('You have enough money. Do not pray more.', 'invdict.get("Money", 0) >= 10 or "money-given" in mods'),
        ('Please, stop. You have enough money.', 'modsdict.get("overpray", 0) > 1'),
    ]
)

hoofd = Scene(
    id_='hoofd',
    header='Strange man on the right',
    image='hoofd.jpg',
    text='You approach the strange man. Speak to him or go back?',
    exits=[
        ('Speak to the strange man', ('hoofd_0', 'True')),
        ('Back', ('first', 'True')),
    ]
)

hoofd_0 = Scene(
    id_='hoofd_0',
    header='Hoofd, the pilots\' chief',
    image='hoofd.jpg',
    text='Hoofd says: "I am the chief of the pilots, but all my pilots are dead. I need a pilot. Are you a pilot?"',
    exits=[
        ('Yes, I am a pilot', ('game_over', 'True')),
        ('No, I am not a pilot', ('hoofd_1', 'True')),
    ],
    speaker='Hoofd, the pilots\' chief',
    on_enter=[
        (('modifiers', 'add', 'hoofd-met'), 'True'),
    ]
)

hoofd_1 = Scene(
    id_='hoofd_1',
    header='Hoofd, the pilots\' chief',
    image='hoofd.jpg',
    text='Hoofd says: "You are not a pilot? Then you are not needed here. Go away."',
    exits=[
        ('Back', ('first', 'True')),
    ],
    speaker='Hoofd, the pilots\' chief',
)


GLOBAL_ADDITIONS = [
    ('Money suffucient to give to the pig.', 'invdict.get("Money", 0) >= 10 and player.current.id_ != "give"'),
]

GLOBAL_IMAGES = []

START = 'Start'
LOAD = 'Load'
SAVE = 'Save'
LOAD_SHORT = 'L'
SAVE_SHORT = 'S'
CREDITS = 'Credits'
EXIT = 'Exit'
LANGUAGE = 'Language'
SAVED = 'Saved'
LOADED = 'Loaded'
RESTART_NEEDED = 'Some changes will take effect only after restarting the game.'
