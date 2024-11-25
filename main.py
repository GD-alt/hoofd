import tomli_w
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen, ModalScreen
from textual.widget import Widget
from textual.widgets import Footer, Label, Button
from pathlib import Path
import random
from dataclasses import dataclass

from textual.reactive import reactive

from classes import Player, Scene
from utils import reduce, image_to_block_art

import tomllib
import bson

import scenes

from meval import meval

from rich.markup import escape

CONFIG = tomllib.loads(Path('config.toml').read_text('utf-8'))

COLOR = CONFIG['color']
BACKGROUND = CONFIG['background']
UTILISE_INVENTORY = CONFIG['utilise_inventory']
UTILISE_SAVELOAD = CONFIG['utilise_saveload']
GAME_NAME = CONFIG['name']
CREDITS = CONFIG['credits']


@dataclass
class SceneCollection:
    RESTART: Scene


SYSTEM_SCENES = SceneCollection(
    RESTART=Scene(
        id_='RESTART',
        header='RESTART',
        text='RESTART',
        exits=[],
        on_enter=[
            (('game', 'restart', ''), 'True')
        ]
    )
)

COLORS = {
    'back': BACKGROUND,
    'text': COLOR,
    'img': COLOR
}

LANGUAGES = CONFIG['languages']


class ImageBar(Widget):
    image = reactive('', recompose=True)

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label(
                self.image,
            ),
            classes='center',
            id='image'
        )


class MainText(Widget):
    text = reactive('', recompose=True)
    inventory = reactive('', recompose=True)
    speaker = reactive('', recompose=True)

    def compose(self) -> ComposeResult:
        text = self.text

        if self.speaker:
            text = f'[underline2]{self.speaker}[/]\n\n{text}'

        text_widget = Label(
            text,
            classes='text width75 center height100',
            id='text'
        )

        if UTILISE_INVENTORY:
            yield Horizontal(
                text_widget,
                Label(
                    self.inventory,
                    classes='text width25 center height100',
                    id='inventory'
                ),
                Button(id='x', classes='no-display')
            )
        else:
            yield Horizontal(
                text_widget,
                Button(id='x', classes='no-display')
            )


class CreditsScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Button(
            CREDITS,
            classes='center height100',
            id='pop-credits'
        )
        yield Button(id='x', classes='no-display')


class LangScreen(ModalScreen[str]):
    """Screen to allow user to choose his language."""
    def __init__(self, languages: list[str]):
        super().__init__()
        self.languages = languages

    def compose(self) -> ComposeResult:
        yield Vertical(
            *(
                Button(
                    lang,
                    id=f'lang_{lang}',
                ) for lang in self.languages
            ),
            classes='height100 center'
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        lang = event.button.id.split('_')[1]
        config = tomllib.loads(Path('config.toml').read_text('utf-8'))
        config['language'] = lang
        Path('config.toml').write_text(tomli_w.dumps(config))
        self.notify(eval(f'scenes.scenes_{lang}.RESTART_NEEDED'))
        self.dismiss(lang)


class QuestApp(App):
    """TUI Quest."""

    colors = COLORS

    CSS = """
    Screen {
        layout: vertical;
    }

    Footer {
        display: none;
    }
    
    Widget {
        border-title-align: center;
        border-title-color: """ + colors['text'] + """;
        border-title-background: """ + colors['back'] + """;
    }
    
    Toast {
        background: """ + colors['back'] + """;
        color: """ + colors['text'] + """;
        border: heavy """ + colors['text'] + """;
    }

    .text {
        align: center middle;
        text-align: center;
        color:""" + colors['text'] + """;
        text-style: bold;
    }

    Label#image {
        text-style: none;
    }
    
    .center {
        align: center middle;
        padding: 1;
        border: heavy """ + colors['text'] + """;
        width: 100%;
        color: """ + colors['text'] + """;
        text-align: center;
    }
    
    .height25 {
        height: 25%;
    }
    
    .height15 {
        height: 15%;
    }
    
    .height60 {
        height: 60%;
    }
    
    Button {
        border: heavy """ + colors['text'] + """;
        background: """ + colors['back'] + """;
        margin: 1;
        color: """ + colors['text'] + """;
        text-align: center;
    }
    
    .width75 {
        width: 75%;
    }
    
    .width25 {
        width: 25%;
    }
    
    .width80 {
        width: 80%;
    }
    
    .width20 {
        width: 20%;
    }
    
    .height100 {
        height: 100%;
    }
    
    .toptext {
        align: center top;
    }
    
    .no-padding {
        padding: 0;
    }
    
    .margin0 {
        margin: 0;
    }
    
    .no-border {
        border: none;
    }
    
    .no-display {
        display: none;
    }
    
    ImageBar {
        color: """ + colors['img'] + """;
    }
    """

    player = Player()
    player.history = []
    modifiers = []
    variables = {}

    def __init__(self):
        super().__init__()

        self.languages = LANGUAGES
        config = tomllib.loads(Path('config.toml').read_text('utf-8'))
        self.language = config['language']

    def modifiers_dict(self):
        """
        Returns the modifiers as a dictionary.
        :return: Dict[str, int]
        """
        if not self.modifiers:
            return {}

        result = {}
        for item in self.modifiers:
            if item in result:
                result[item] += 1
            else:
                result[item] = 1

        return result

    NOTIFICATION_TIMEOUT = 2

    def on_mount(self) -> None:
        self.screen.styles.background = self.colors['back']
        self.screen.styles.border = ('heavy', self.colors['text'])
        self.screen.styles.align = ('center', 'middle')

    async def destroy(self) -> None:
        buttons = self.query(Button)

        for b in buttons:
            await b.remove()

        try:
            image_bar = self.query_one(ImageBar)
            await image_bar.remove()
        except Exception:
            pass

        try:
            name = self.query_one(Label)
            await name.remove()
        except Exception:
            pass

        await self.query_one('#main-buttons').remove()

    async def destroy_game_screen(self):
        try:
            image_bar = self.query_one(ImageBar)
            await image_bar.remove()
        except Exception:
            pass

        try:
            main_text = self.query_one(MainText)
            await main_text.remove()
        except Exception:
            pass

        try:
            buttons = self.query_one('#buttons')
            await buttons.remove()
        except Exception:
            pass

        try:
            save_load = self.query_one('#save-load')
            await save_load.remove()
        except Exception:
            pass

        try:
            bsl_bar = self.query_one('#bsl-bar')
            await bsl_bar.remove()
        except Exception:
            pass

    async def compose_game_screen(self, screen_id: str = 'first'):
        random_number = random.randint(0, 100)

        self.player.current = await meval(
            f'scenes.scenes_{self.language}.{screen_id}'
            if screen_id[0] != '!' else screen_id[1:],
            globals(),
            scenes=scenes,
            player=self.player,
            random=random,
            SYS=SYSTEM_SCENES
        )

        my_vars = eval(f'scenes.scenes_{self.language}.MY_VARS')

        for var, formula in my_vars.items():
            self.variables[var] = await meval(
                formula,
                globals(),
                player=self.player,
                mods=self.modifiers,
                modsdict=self.modifiers_dict(),
                vars=self.variables,
                scenes=scenes,
                inventory=self.player.inventory,
                invdict=self.player.inventory_dict(),
                random=random,
                rnum=random_number,
                SYS=SYSTEM_SCENES
            )

        image_bar = ImageBar(classes='height60', id='image-bar')

        await self.mount(image_bar)

        main_text = MainText(classes='height25')

        text = self.player.current.text

        for t, cond in self.player.current.if_texts:
            if await meval(
                    cond,
                    globals(),
                    player=self.player,
                    mods=self.modifiers,
                    modsdict=self.modifiers_dict(),
                    vars=self.variables,
                    scenes=scenes,
                    inventory=self.player.inventory,
                    invdict=self.player.inventory_dict(),
                    random=random,
                    rnum=random_number,
                    SYS=SYSTEM_SCENES,
                    MY=my_vars
            ):
                text = t

        text += '\n'

        for t, cond in self.player.current.if_text_additions:
            if await meval(
                    cond,
                    globals(),
                    player=self.player,
                    mods=self.modifiers,
                    modsdict=self.modifiers_dict(),
                    vars=self.variables,
                    scenes=scenes,
                    inventory=self.player.inventory,
                    invdict=self.player.inventory_dict(),
                    random=random,
                    rnum=random_number,
                    SYS=SYSTEM_SCENES,
                    MY=my_vars
            ):
                text += '\n' + t

        for t, cond in eval(f'scenes.scenes_{self.language}.GLOBAL_ADDITIONS'):
            if await meval(
                    cond,
                    globals(),
                    player=self.player,
                    mods=self.modifiers,
                    modsdict=self.modifiers_dict(),
                    vars=self.variables,
                    scenes=scenes,
                    inventory=self.player.inventory,
                    invdict=self.player.inventory_dict(),
                    random=random,
                    rnum=random_number,
                    SYS=SYSTEM_SCENES,
                    MY=my_vars
            ):
                text += '\n' + t

        img = self.player.current.image

        for t, cond in self.player.current.if_images:
            if await meval(
                    cond,
                    globals(),
                    player=self.player,
                    mods=self.modifiers,
                    modsdict=self.modifiers_dict(),
                    vars=self.variables,
                    scenes=scenes,
                    inventory=self.player.inventory,
                    invdict=self.player.inventory_dict(),
                    random=random,
                    rnum=random_number,
                    SYS=SYSTEM_SCENES,
                    MY=my_vars
            ):
                img = t

        for t, cond in eval(f'scenes.scenes_{self.language}.GLOBAL_IMAGES'):
            if await meval(
                    cond,
                    globals(),
                    player=self.player,
                    mods=self.modifiers,
                    modsdict=self.modifiers_dict(),
                    vars=self.variables,
                    scenes=scenes,
                    inventory=self.player.inventory,
                    invdict=self.player.inventory_dict(),
                    random=random,
                    rnum=random_number,
                    SYS=SYSTEM_SCENES,
                    MY=my_vars
            ):
                img = t

        image_bar.image = image_to_block_art(
            reduce(Path('assets') / Path(img), 400)
        ) if self.player.current.image else ''

        speaker = self.player.current.speaker

        for t, cond in self.player.current.if_speakers:
            if await meval(
                cond,
                globals(),
                player=self.player,
                mods=self.modifiers,
                modsdict=self.modifiers_dict(),
                vars=self.variables,
                scenes=scenes,
                inventory=self.player.inventory,
                invdict=self.player.inventory_dict(),
                random=random,
                rnum=random_number,
                SYS=SYSTEM_SCENES,
                MY=my_vars
            ):
                speaker = t

        items_loctable = eval(f'scenes.scenes_{self.language}.ITEMS')
        main_text.inventory = '\n'.join(
            [
                f'{items_loctable[k]} x{v}'
                for k, v in
                self.player.inventory_dict().items()
            ]
        ) if self.player.inventory_dict() else eval(f'scenes.scenes_{self.language}.EMPTY')

        if self.player.current.sanitize:
            text = escape(text)

        if self.player.current.enable_formatting:
            text = text.format(
                player=self.player,
                mods=self.modifiers,
                modsdict=self.modifiers_dict(),
                vars=self.variables,
                scenes=scenes,
                inventory=self.player.inventory,
                invdict=self.player.inventory_dict(),
                random=random,
                rnum=random_number,
                SYS=SYSTEM_SCENES,
                MY=my_vars
            )

        main_text.text = text
        main_text.speaker = speaker

        await self.mount(main_text)

        if UTILISE_INVENTORY:
            main_text.inventory = self.player.inventory_with_count()

        choices = [
            Button(
                k.format(
                    player=self.player,
                    mods=self.modifiers,
                    modsdict=self.modifiers_dict(),
                    vars=self.variables,
                    scenes=scenes,
                    inventory=self.player.inventory,
                    invdict=self.player.inventory_dict(),
                    random=random,
                    rnum=random_number,
                    SYS=SYSTEM_SCENES,
                    MY=my_vars
                ) if self.player.current.enable_formatting else k,
                id=f'button{i}'
            ) for i, (k, (v, cond)) in enumerate(self.player.current.exits)
            if await meval(
                cond,
                globals(),
                player=self.player,
                mods=self.modifiers,
                modsdict=self.modifiers_dict(),
                vars=self.variables,
                scenes=scenes,
                inventory=self.player.inventory,
                invdict=self.player.inventory_dict(),
                random=random,
                rnum=random_number,
                SYS=SYSTEM_SCENES,
                MY=my_vars
            )
        ]

        if UTILISE_SAVELOAD:
            await self.mount(
                Horizontal(
                    Horizontal(
                        *choices,
                        classes='center width80',
                        id='buttons'
                    ),
                    Vertical(
                        Button(eval(f'scenes.scenes_{self.language}.SAVE_SHORT'), id='save', classes='margin0'),
                        Button(eval(f'scenes.scenes_{self.language}.LOAD_SHORT'), id='load', classes='margin0'),
                        classes='center width20 no-padding',
                        id='save-load'
                    ),
                    classes='height15',
                    id='bsl-bar'
                )
            )
        else:
            await self.mount(
                Horizontal(
                    *choices,
                    classes='center height15',
                    id='buttons'
                )
            )

    def compose(self) -> ComposeResult:
        banner = ImageBar(classes='height60', id='image-bar')

        for file in Path('assets').rglob('*'):
            if file.is_file() and file.suffix in ['.png', '.jpg', '.jpeg'] and file.name.split('.')[0] == 'banner':
                banner.image = image_to_block_art(
                    reduce(file, 400)
                )

        if banner.image:
            yield banner

        if GAME_NAME:
            yield Label(
                GAME_NAME,
                classes='center height15',
            )

        children = [
            Button(
                eval(f'scenes.scenes_{self.language}.START'),
                classes='margin0',
                id='start',
            )
        ]

        if UTILISE_SAVELOAD:
            children.append(
                Button(
                    eval(f'scenes.scenes_{self.language}.LOAD'),
                    classes='margin0',
                    id='load-mainscreen',
                )
            )

        if CREDITS:
            children.append(
                Button(
                    eval(f'scenes.scenes_{self.language}.CREDITS'),
                    classes='margin0',
                    id='credits',
                )
            )

        if len(self.languages) > 1:
            children.append(
                Button(
                    eval(f'scenes.scenes_{self.language}.LANGUAGE'),
                    classes='margin0',
                    id='lang',
                )
            )

        children.append(
            Button(
                eval(f'scenes.scenes_{self.language}.EXIT'),
                classes='margin0',
                id='exit',
            )
        )

        yield Horizontal(
            *children,
            classes='center height15 no-border',
            id='main-buttons'
        )

        nd = Button(id='x', classes='no-display')
        yield nd
        nd.focus()

        self.player.current = eval(f'scenes.scenes_{self.language}.first')

        yield Footer()

        return

    @work
    async def on_button_pressed(self, event: Button.Pressed):
        button = event.button
        random_number = random.randint(0, 100)

        if button.id == 'exit':
            exit(0)

        if button.id == 'credits':
            await self.push_screen(CreditsScreen())
            self.set_focus(self.query_one('.no-display'))
            return

        if button.id == 'pop-credits':
            await self.pop_screen()
            self.set_focus(self.query_one('.no-display'))
            return

        if button.id == 'start':
            await self.destroy()
            await self.compose_game_screen()
            self.set_focus(self.query_one('.no-display'))
            return

        if button.id == 'save':
            data = {
                'current': self.player.current.id_,
                'inventory': self.player.inventory,
                'previous': self.player.previous.id_ if self.player.previous else '',
                'modifiers': self.modifiers,
                'variables': self.variables,
                'history': [item.__dict__ for item in self.player.history]
            }

            data_dumped = bson.dumps(data)
            Path('save.json').write_bytes(data_dumped)

            self.notify(await meval(f'scenes.scenes_{self.language}.SAVED', globals(), scenes=scenes))
            self.set_focus(self.query_one('.no-display'))
            return

        if button.id == 'load-mainscreen':
            data = bson.loads(Path('save.json').read_bytes())

            self.player.current = await meval(
                f'scenes.scenes_{self.language}.{data["current"]}',
                globals(),
                scenes=scenes,
                player=self.player,
                random=random,
            )

            self.player.inventory = data['inventory']

            self.player.previous = await meval(
                f'scenes.scenes_{self.language}.{data["previous"]}',
                globals(),
                scenes=scenes,
            ) if data['previous'] else None

            self.modifiers = data['modifiers']
            self.variables = data['variables']

            self.history = [Scene(**item) for item in data['history']]

            await self.destroy()
            await self.compose_game_screen(data['current'])
            self.set_focus(self.query_one('.no-display'))
            self.notify(await meval(f'scenes.scenes_{self.language}.LOADED', globals(), scenes=scenes))
            return

        if button.id == 'load':
            data = bson.loads(Path('save.json').read_bytes())

            self.player.current = await meval(
                f'scenes.scenes_{self.language}.{data["current"]}',
                globals(),
                scenes=scenes,
                player=self.player,
                random=random,
            )

            self.player.inventory = data['inventory']

            self.player.previous = await meval(
                f'scenes.scenes_{self.language}.{data["previous"]}',
                globals(),
                scenes=scenes,
            ) if data['previous'] else None

            self.modifiers = data['modifiers']
            self.variables = data['variables']

            self.history = [Scene(**item) for item in data['history']]

            items_loctable = eval(f'scenes.scenes_{self.language}.ITEMS')
            self.query_one(MainText).inventory = '\n'.join(
                [
                    f'{items_loctable[k]} x{v}'
                    for k, v in
                    self.player.inventory_dict().items()
                ]
            ) if self.player.inventory_dict() else eval(f'scenes.scenes_{self.language}.EMPTY')

            await self.destroy_game_screen()
            await self.compose_game_screen(data['current'])
            self.set_focus(self.query_one('.no-display'))
            self.notify('Loaded!')
            return

        if button.id == 'lang':
            lang = await self.push_screen_wait(
                LangScreen(languages=self.languages),
            )
            self.language = lang

            config = tomllib.loads(Path('config.toml').read_text('utf-8'))
            config['language'] = lang
            Path('config.toml').write_text(tomli_w.dumps(config))

            return

        if button.id.startswith('lang_'):
            return

        choice = list(self.player.current.exits)[int(button.id[6:])]
        self.player.previous = self.player.current

        if choice[1][0] == 'EXIT':
            exit(0)

        self.player.current = await meval(
            f'scenes.scenes_{self.language}.{choice[1][0]}'
            if choice[1][0][0] != '!' else choice[1][0][1:],
            globals(),
            scenes=scenes,
            player=self.player,
            random=random,
            SYS=SYSTEM_SCENES
        )

        my_vars = eval(f'scenes.scenes_{self.language}.MY_VARS')

        for var, formula in my_vars.items():
            self.variables[var] = await meval(
                formula,
                globals(),
                player=self.player,
                mods=self.modifiers,
                modsdict=self.modifiers_dict(),
                vars=self.variables,
                scenes=scenes,
                inventory=self.player.inventory,
                invdict=self.player.inventory_dict(),
                random=random,
                rnum=random_number,
                SYS=SYSTEM_SCENES
            )

        self.set_focus(self.query_one('.no-display'))

        text = self.player.current.text

        for t, cond in self.player.current.if_texts:
            if await meval(
                    cond,
                    globals(),
                    player=self.player,
                    mods=self.modifiers,
                    modsdict=self.modifiers_dict(),
                    vars=self.variables,
                    scenes=scenes,
                    inventory=self.player.inventory,
                    invdict=self.player.inventory_dict(),
                    random=random,
                    rnum=random_number,
                    SYS=SYSTEM_SCENES,
                    MY=my_vars
            ):
                text = t

        text += '\n'

        for t, cond in self.player.current.if_text_additions:
            if await meval(
                    cond,
                    globals(),
                    player=self.player,
                    mods=self.modifiers,
                    modsdict=self.modifiers_dict(),
                    vars=self.variables,
                    scenes=scenes,
                    inventory=self.player.inventory,
                    invdict=self.player.inventory_dict(),
                    random=random,
                    rnum=random_number,
                    SYS=SYSTEM_SCENES,
                    MY=my_vars
            ):
                text += '\n' + t

        for t, cond in eval(f'scenes.scenes_{self.language}.GLOBAL_ADDITIONS'):
            if await meval(
                    cond,
                    globals(),
                    player=self.player,
                    mods=self.modifiers,
                    modsdict=self.modifiers_dict(),
                    vars=self.variables,
                    scenes=scenes,
                    inventory=self.player.inventory,
                    invdict=self.player.inventory_dict(),
                    random=random,
                    rnum=random_number,
                    SYS=SYSTEM_SCENES,
                    MY=my_vars
            ):
                text += '\n' + t

        img = self.player.current.image

        for t, cond in self.player.current.if_images:
            if await meval(
                    cond,
                    globals(),
                    player=self.player,
                    mods=self.modifiers,
                    modsdict=self.modifiers_dict(),
                    vars=self.variables,
                    scenes=scenes,
                    inventory=self.player.inventory,
                    invdict=self.player.inventory_dict(),
                    random=random,
                    rnum=random_number,
                    SYS=SYSTEM_SCENES,
                    MY=my_vars
            ):
                img = t

        for t, cond in eval(f'scenes.scenes_{self.language}.GLOBAL_IMAGES'):
            if await meval(
                    cond,
                    globals(),
                    player=self.player,
                    mods=self.modifiers,
                    modsdict=self.modifiers_dict(),
                    vars=self.variables,
                    scenes=scenes,
                    inventory=self.player.inventory,
                    invdict=self.player.inventory_dict(),
                    random=random,
                    rnum=random_number,
                    SYS=SYSTEM_SCENES,
                    MY=my_vars
            ):
                img = t

        self.query_one(ImageBar).image = image_to_block_art(
            reduce(Path('assets') / Path(img), 400)
        ) if self.player.current.image else ''

        main_text = self.query_one(MainText)

        speaker = self.player.current.speaker

        for t, cond in self.player.current.if_speakers:
            if await meval(
                cond,
                globals(),
                player=self.player,
                mods=self.modifiers,
                modsdict=self.modifiers_dict(),
                vars=self.variables,
                scenes=scenes,
                inventory=self.player.inventory,
                invdict=self.player.inventory_dict(),
                random=random,
                rnum=random_number,
                SYS=SYSTEM_SCENES,
                MY=my_vars
            ):
                speaker = t

        if self.player.current.sanitize:
            text = escape(text)

        if self.player.current.enable_formatting:
            text = text.format(
                player=self.player,
                mods=self.modifiers,
                modsdict=self.modifiers_dict(),
                vars=self.variables,
                scenes=scenes,
                inventory=self.player.inventory,
                invdict=self.player.inventory_dict(),
                random=random,
                rnum=random_number,
                SYS=SYSTEM_SCENES,
                MY=my_vars
            )

        main_text.text = text
        main_text.speaker = speaker

        for action, cond in self.player.current.on_enter:
            if await meval(
                    cond,
                    globals(),
                    player=self.player,
                    mods=self.modifiers,
                    modsdict=self.modifiers_dict(),
                    vars=self.variables,
                    scenes=scenes,
                    inventory=self.player.inventory,
                    invdict=self.player.inventory_dict(),
                    random=random,
                    rnum=random_number,
                    SYS=SYSTEM_SCENES,
                    MY=my_vars,
            ):
                target, action_type, item = action

                if target == 'inventory':
                    if action_type == 'add':
                        self.player.inventory.append(item)
                    if action_type == 'add-many':
                        self.player.inventory.extend([item[0] for _ in range(int(item[1]))])
                    elif action_type == 'remove':
                        self.player.inventory.remove(item)
                    elif action_type == 'remove-all':
                        self.player.inventory = [i for i in self.player.inventory if i != item]
                    elif action_type == 'clear':
                        self.player.inventory = []

                elif target == 'modifiers':
                    if action_type == 'add':
                        self.modifiers.append(item)
                    elif action_type == 'add-many':
                        self.modifiers.extend([item for _ in range(int(item[1]))])
                    elif action_type == 'remove':
                        self.modifiers.remove(item)
                    elif action_type == 'remove-all':
                        self.modifiers = [i for i in self.modifiers if i != item]
                    elif action_type == 'clear':
                        self.modifiers = []

                elif target == 'variables':
                    if action_type == 'add':
                        self.variables[item[0]] = item[1]
                    elif action_type == 'remove':
                        del self.variables[item[0]]
                    elif action_type == 'clear':
                        self.variables = {}
                    elif action_type == 'update':
                        self.variables[item[0]] = item[1]
                    elif action_type == 'inc':
                        self.variables[item[0]] += item[1]
                    elif action_type == 'dec':
                        self.variables[item[0]] -= item[1]
                    elif action_type == 'set':
                        self.variables[item[0]] = await meval(
                            item[1],
                            globals(),
                            player=self.player,
                            mods=self.modifiers,
                            modsdict=self.modifiers_dict(),
                            vars=self.variables,
                            scenes=scenes,
                            inventory=self.player.inventory,
                            invdict=self.player.inventory_dict(),
                            random=random,
                            rnum=random_number
                        )

                elif target == 'game':
                    if action_type == 'exit':
                        exit()

                    elif action_type == 'goto':
                        await self.destroy_game_screen()
                        await self.compose_game_screen(item)
                        self.set_focus(self.query_one('.no-display'))
                        return

                    elif action_type == 'restart':
                        self.player = Player()
                        self.player.history = []
                        self.player.current = await meval(
                            f'scenes.scenes_{self.language}.first',
                            globals(),
                            scenes=scenes,
                            player=self.player,
                            random=random,
                        )
                        await self.destroy_game_screen()
                        await self.compose_game_screen()
                        self.modifiers = []
                        self.variables = {}
                        self.set_focus(self.query_one('.no-display'))
                        return

                    elif action_type == 'destroy':
                        await self.destroy_game_screen()
                        return

                    elif action_type == 'load':
                        data = bson.loads(Path('save.json').read_bytes())

                        self.player.current = await meval(
                            f'scenes.scenes_{self.language}.{data["current"]}',
                            globals(),
                            scenes=scenes,
                            player=self.player,
                            random=random,
                        )

                        self.player.inventory = data['inventory']

                        self.player.previous = await meval(
                            f'scenes.{data["previous"]}',
                            globals(),
                            scenes=scenes,
                        ) if data['previous'] else None

                        self.modifiers = data['modifiers']
                        self.variables = data['variables']

                        self.history = [Scene(**item) for item in data['history']]

                        await self.destroy_game_screen()
                        await self.compose_game_screen(data['current'])

                        self.set_focus(self.query_one('.no-display'))

                        if item != 'silent':
                            self.notify('Loaded!')

                        return

                    elif action_type == 'save':
                        data = {
                            'current': self.player.current.id_,
                            'inventory': self.player.inventory,
                            'previous': self.player.previous.id_ if self.player.previous else '',
                            'modifiers': self.modifiers,
                            'variables': self.variables,
                            'history': [item.__dict__ for item in self.history]
                        }

                        data_dumped = bson.dumps(data)
                        Path('save.json').write_bytes(data_dumped)

                        if item != 'silent':
                            self.notify('Saved!')

                        self.set_focus(self.query_one('.no-display'))
                        return

                    elif action_type == 'notify':
                        self.notify(item if isinstance(item, str) else ' '.join(item))

        items_loctable = eval(f'scenes.scenes_{self.language}.ITEMS')
        self.query_one(MainText).inventory = '\n'.join(
            [
                f'{items_loctable[k]} x{v}'
                for k, v in
                self.player.inventory_dict().items()
            ]
        ) if self.player.inventory_dict() else eval(f'scenes.scenes_{self.language}.EMPTY')

        buttons = self.query(Button)

        for b in buttons:
            if b.id.startswith('button'):
                await b.remove()

        choices = [
            Button(
                k.format(
                    player=self.player,
                    mods=self.modifiers,
                    modsdict=self.modifiers_dict(),
                    vars=self.variables,
                    scenes=scenes,
                    inventory=self.player.inventory,
                    invdict=self.player.inventory_dict(),
                    random=random,
                    rnum=random_number,
                    SYS=SYSTEM_SCENES,
                    MY=my_vars
                ) if self.player.current.enable_formatting else k,
                id=f'button{i}'
            ) for i, (k, (v, cond)) in enumerate(self.player.current.exits)
            if await meval(
                cond,
                globals(),
                player=self.player,
                mods=self.modifiers,
                modsdict=self.modifiers_dict(),
                vars=self.variables,
                scenes=scenes,
                inventory=self.player.inventory,
                invdict=self.player.inventory_dict(),
                random=random,
                rnum=random_number,
                SYS=SYSTEM_SCENES,
                MY=my_vars
            )
        ]

        button_bar = self.query_one('#buttons')
        await button_bar.mount(*choices)

        self.player.history.append(self.player.current)

        self.refresh()


if __name__ == "__main__":
    app = QuestApp()
    app.run()
