from observer import Publisher
from typing import Union
from exceptions import *


class ViewModel(Publisher):
    _message_type = _message = _level = _buttons = None

    def __init__(self, model):
        super().__init__()
        self._model = model
        self._session = True

        self._buttonsDict = {
            'load': {
                'load_game': lambda: self._load_game(),
                'new_game': lambda: self._new_game(),
                'exit_game': lambda: self._exit_game(),
            },
            'controls': {
                'left': lambda: self._move_to('left'),
                'up': lambda: self._move_to('up'),
                'right': lambda: self._move_to('right'),
                'down': lambda: self._move_to('down'),
                # 'main_menu': None,
                'main_menu': lambda: self.game_start(),
            },
        }

    def game_start(self):
        self._level = self._buttons = None
        self._message_type = 'message'
        self._message = '\t\t\tПриветствую!\n' \
                        '\tЭто игра "Лабиринт" и вам нужно помочь Шарику найти косточку'
        self.notify()
        input()

        self._main_menu()

        if self._session:
            self._message = '\tВыберите в какую сторону пойти'
            buttons = self._create_buttons(self._buttonsDict['controls'])
            while self._session:
                self._buttonsDict['controls'][self._try_user_choice(buttons)]()
                self.notify()

    def _main_menu(self):
        try:
            open('save.pickle', 'rb')  # existing save check

            self._message = '\n\tНачать новую игру или загрузить сохранение?'
            buttons = self._create_buttons(self._buttonsDict['load'])
            self._buttonsDict['load'][self._try_user_choice(buttons)]()

        except FileNotFoundError:
            self._new_game()

        if self._session:
            self._level = self._model.level

    def _new_game(self):
        self._message = '\t\tДля начала давайте выберем сложность:'
        buttons = self._create_buttons(self._model.levels)
        difficulty = self._try_user_choice(buttons)

        self._message = '\t\tВыберите желаемый уровень:'
        buttons = self._create_buttons(self._model.levels[difficulty])
        level = self._try_user_choice(buttons)

        self._model.new_game(difficulty, level)

    def _try_user_choice(self, collection: dict) -> Union[int, str]:
        try:
            return collection[int(input('Введите индекс кнопки:\n'))]
        except ValueError:
            return self._try_user_choice(collection)
        except KeyError:
            return self._try_user_choice(collection)

    def _create_buttons(self, collection: dict):
        buttons = {
            index: button
            for index, button
            in enumerate(collection)
            if collection[button]
        }

        self._buttons = ''
        for index, button in buttons.items():
            self._buttons += f'\t\t{index}: {button}'
        self.notify()

        return buttons

    def _load_game(self):
        self._model.load_game()

    def _exit_game(self):
        self._session = self._level = self._buttons = None
        self._message = 'До встречи, Шарик будет ждать тебя!'

    def _move_to(self, side):
        try:
            self._model.move_to(side)
        except HittingTheWallError:

            self._main_menu()

        except WrongPathError:

            self._main_menu()

        except BackStepError:

            self._main_menu()

        except Congratulations:

            self._main_menu()

    def notify(self):
        for subscriber in self._subscribers:
            subscriber.update(self._message_type, self._message, self._level, self._buttons)
