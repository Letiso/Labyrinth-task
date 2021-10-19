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
                'main_menu': lambda: self.game_start()
            },
        }

    def game_start(self):
        self._message_type = 'message'
        # todo check for existing save
        self.new_game()

        controls = {
            index: button
            for index, button
            in enumerate(self._buttonsDict['controls'])
        }
        self._message = '\tВыберите в какую сторону пойти'

        self._buttons = ''
        for index, button in controls.items():
            self._buttons += f'\t\t{index}: {button}'
        self.notify()

        while True:
            # todo implement movement engine
            self._buttonsDict['controls'][self._user_choice(controls)]()
            self.notify()

    def new_game(self):
        difficulty = self._select_difficulty()
        level = self._select_level(difficulty)

        self._model.new_game(difficulty, level)

    def _select_difficulty(self):
        difficulties = {
            index: difficulty
            for index, difficulty
            in enumerate(self._model.levels)
            if self._model.levels[difficulty]
        }

        self._message = '\t\t\tПриветствую!\n' \
                        '\tЭто игра "Лабиринт" и вам нужно помочь Шарику найти косточку\n' \
                        '\t\tДля начала давайте выберем сложность:'

        self._buttons = ''
        for index, button in difficulties.items():
            self._buttons += f'\t\t{index}: {button}'
        self.notify()

        return self._user_choice(difficulties)

    def _select_level(self, difficulty):
        levels = {
            index: level
            for index, level
            in enumerate(self._model.levels[difficulty])
        }

        self._message = '\t\tВыберите желаемый уровень:'

        self._buttons = ''
        for index, button in levels.items():
            self._buttons += f'\t\t{index}: {button}'
        self.notify()

        return self._user_choice(levels)

    def _user_choice(self, collection: dict):
        try:
            return collection[int(input('Введите индекс кнопки:\n'))]
        except ValueError or IndexError:
            self._user_choice(collection)

    def load_game(self): pass

    def move_to(self, side):
        # try:
        self._model.move_to(side)

    def notify(self):
        for subscriber in self._subscribers:
            subscriber.update(self._message_type, self._message, self._model.level, self._buttons)

    def update(self, *args): pass





