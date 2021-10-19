from observer import Subscriber


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


class View(Subscriber):
    def __init__(self, view_model):
        self._view_model = view_model
        self._view_model.subscribe(self)

    def game_start(self):
        self._view_model.game_start()

    @staticmethod
    @underline_creator
    def render(underline, div):
        if not div: return
        print(underline)
        print(div)
        print(underline)

    def update(self, message_type, message, level, buttons):
        for _type, div in zip((message_type, 'level', 'buttons'),
                              (message, level, buttons)):
            self.render(_type, div)
