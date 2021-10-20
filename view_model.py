from observer import Publisher
from exceptions import *


class ViewModel(Publisher):
    _message_type = _message = _buttons = None

    def __init__(self, model):
        super().__init__()
        self._model = model

        self._buttonsDict = {
            'load': {
                'new_game': lambda: self.new_game(),
                'load_game': lambda: self.load_game()
            },
            'controls': {
                'left': lambda: self.move_to('left'),
                'up': lambda: self.move_to('up'),
                'right': lambda: self.move_to('right'),
                'down': lambda: self.move_to('down'),
                'main_menu': None
            },
        }

    def game_start(self):
        self._message_type = 'message'
        self._message = '\t\t\tПриветствую!\n' \
                        '\tЭто игра "Лабиринт" и вам нужно помочь Шарику найти косточку'
        self.notify()
        input()
        self._new_or_load()

        self._message = '\tВыберите в какую сторону пойти'
        buttons = self._create_buttons(self._buttonsDict['controls'])
        while True:
            # todo implement movement engine
            self._buttonsDict['controls'][self._try_user_choice(buttons)]()
            self.notify()

    def _new_or_load(self):
        try:
            open('save.pickle', 'rb')  # existing save check

            self._message = '\n\tНачать новую игру или загрузить сохранение?'
            buttons = self._create_buttons(self._buttonsDict['load'])
            self._buttonsDict['load'][self._try_user_choice(buttons)]()

        except FileNotFoundError:
            self.new_game()

    def new_game(self):
        self._message = '\t\tДля начала давайте выберем сложность:'
        buttons = self._create_buttons(self._model.levels)
        difficulty = self._try_user_choice(buttons)

        self._message = '\t\tВыберите желаемый уровень:'
        buttons = self._create_buttons(self._model.levels[difficulty])
        level = self._try_user_choice(buttons)

        self._model.new_game(difficulty, level)

    def _try_user_choice(self, collection: dict):
        try:
            return collection[int(input('Введите индекс кнопки:\n'))]
        except ValueError or IndexError:
            self._try_user_choice(collection)

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

    def load_game(self):
        self._model.load_game()

    def move_to(self, side):
        # todo implement exceptions handling
        self._model.move_to(side)

    def notify(self):
        for subscriber in self._subscribers:
            subscriber.update(self._message_type, self._message, self._model.level, self._buttons)
