from observer import Subscriber
from os import system as bash
from platform import system
from exceptions import ExitGame


def underline_creator(method):
    underlines_count = 13

    underlines = {
        'message': '______',
        'success': '++++++',
        'error': '******',
        'loading': ' ---  ',

        'level': '<><><>',
        'buttons': '------',
    }
    for underline in list(underlines):
        underlines[underline] *= underlines_count

    def wrapper(_type, div):
        return method(underlines[_type], div)
    return wrapper


def terminal_or_command_line(method):
    command = 'cls' if system().split('-')[0].lower() == 'windows' else 'clear'

    def wrapper(self, message_type, message, level, buttons):
        bash(command)
        method(self, message_type, message, level, buttons)
    return wrapper


class View(Subscriber):
    def __init__(self, view_model):
        self._view_model = view_model
        self._view_model.subscribe(self)

    def game_start(self):
        try:
            self._view_model.game_start()
        except ExitGame:
            pass

    @staticmethod
    @underline_creator
    def render(underline, div):
        if not div: return
        print(underline)
        print(div)
        print(underline)

    @terminal_or_command_line
    def update(self, message_type, message, level, buttons):
        for _type, div in zip((message_type, 'level', 'buttons'),
                              (message, level, buttons)):
            self.render(_type, div)
