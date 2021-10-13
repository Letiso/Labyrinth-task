import json
from copy import deepcopy
from abc import ABC, abstractmethod
from errors import *


# Walls abstract class
class Wall:
    def __init__(self, show: int) -> None:
        self._show: int = show

    @abstractmethod
    def __str__(self) -> str: pass

    def __radd__(self, player: 'Player') -> None:

        # TODO Make a transfer to the next cell in the desired direction, if the wall is transparent
        if not self._show: pass

        else:
            raise HittingTheWallError()


class VerticalWall(Wall):
    def __str__(self) -> str:
        return ' ' if not self._show else '|'


class HorizontalWall(Wall):
    def __str__(self) -> str:
        return '  ' if not self._show else '——'


class AdjacentWall:
    def __init__(self):
        self._show = self._view = None

    def init(self, view: str):
        self._show = True
        self._view = view

    def __str__(self) -> str:
        return ' ' if not self._show else self._view


# Cells abstract class
class Cell(ABC):
    @abstractmethod
    def __str__(self) -> str: pass


# Cell types
class Path(Cell):
    _status: str = None
    _right_path: bool = None

    def set_right_path(self):
        self._right_path = True

    def set_status(self, status: str):
        self._status = status

    def __str__(self) -> str:
        return '  ' if not self._right_path else '++'
        # return '  '

    def __radd__(self, player: 'Player') -> bool:
        if not self._right_path:
            raise WrongPathError()
        else:
            match self._status:
                case 'SavePoint': raise BackStepError()
                case 'Finish': raise Congratulations()

                # todo Make swapping between player cell and path cell
                case None: return True


class Player(Cell):
    def __init__(self) -> None: pass

    def __str__(self) -> str:
        return '<>'


# Map
class Level:
    _player: Player = None
    _adjacent_walls_symbols = {
        'ulrd': '+',

        'u___': '|',
        'u__d': '|',
        '___d': '|',

        '_lr_': '—',
        '_l__': '—',
        '__r_': '—',

        '____': ' ',

        'ul__': '┘',
        'u_r_': '└',

        '_l_d': '┐',
        '__rd': '┌',

        'ulr_': '┴',
        '_lrd': '┬',

        'u_rd': '├',
        'ul_d': '┤',

    }

    def __init__(self, level_generator: dict) -> None:
        self._matrix = []
        self._generate_matrix(level_generator['walls'])
        # self._configure_adjacent_walls()
        self._right_path_init(level_generator['path'])

    def _generate_matrix(self, walls_code: tuple):
        for y, string in enumerate(walls_code):
            result = []
            if y % 2 == 0:
                for code in string:
                    result += [AdjacentWall(), HorizontalWall(int(code))]
                result.append(AdjacentWall())
            else:
                for code in string[:-1]:
                    result += [VerticalWall(int(code)), Path()]
                result.append(VerticalWall(int(string[-1])))
            self._matrix.append(result)

    # TODO make adjacent walls init initialisation
    # def _configure_adjacent_walls(self):
    #     current_pos = {
    #         'x': 0,
    #         'y': 0
    #     }
    #     last_available_pos = {
    #         'x': len(self._matrix[-1]),
    #         'y': len(self._matrix)
    #     }
    #
    #     adjacent_walls_property: list = []
    #     while current_pos['y'] != last_available_pos['y']:
    #         adjacent_walls_string = []
    #
    #         current_pos['x'] = 0
    #
    #         if current_pos['y']:
    #             string = self._upper_side_check(current_pos, last_available_pos['x'])
    #             adjacent_walls_string.append(string)
    #         else:
    #             adjacent_walls_string.append([None for x, wall in enumerate(self._matrix[0])
    #                                           if x % 2 == 0])
    #
    #         for side in - 1, + 1:
    #             string = self._middle_side_check(current_pos, last_available_pos['x'])
    #             adjacent_walls_string.append(string)
    #
    #         if current_pos['y'] != last_available_pos['y']:
    #             self._lower_side_check(current_pos, last_available_pos['x'])
    #         else:
    #             adjacent_walls_string.append([None for x, wall in enumerate(self._matrix[-1])
    #                                           if x % 2 == 0])
    #
    #         codes = [(up, left, right, down)
    #                  for up, left, right, down in adjacent_walls_string]
    #         adjacent_walls_property.append(codes)
    #
    #         current_pos['y'] += 1
    #
    #
    # def _upper_side_check(self, current_pos, last_x):
    #     upper_side = []
    #     while current_pos['x'] <= last_x:
    #         pass
    #     return upper_side
    #
    # def _middle_side_check(self, current_pos, last_x):
    #     middle_side = []
    #     while current_pos['x'] <= last_x:
    #         pass
    #     return middle_side
    #
    # def _lower_side_check(self, current_pos, last_x):
    #     lower_side = []
    #     while current_pos['x'] <= last_x:
    #         pass
    #     return lower_side

    def _right_path_init(self, path_code: tuple):
        for string_code, string in zip(path_code, [string for y, string
                                                   in enumerate(self._matrix)
                                                   if y % 2 != 0]):
            for mode, path in zip(string_code, [cell for cell in string
                                                if isinstance(cell, Path)]):
                if int(mode): path.set_right_path()

    # TODO add player placing at level matrix

    def __str__(self) -> str:
        result = str()
        for string in self._matrix:
            result += '\t' * 5
            for cell in [str(cell) for cell in string]:
                result += cell
            result += '\n'
        return result


# Game
class Core:
    _levels: dict = {
        'easy': {
            'level 1': {
                'walls': (
                    ('1', '1', '1', '1', '1', '1', '1', '1', '1'),
                    ('0', '0', '1', '0', '0', '1', '0', '1', '0', '1'),
                    ('1', '0', '0', '1', '1', '0', '0', '1', '0'),
                    ('1', '0', '1', '0', '1', '0', '1', '0', '0', '1'),
                    ('0', '1', '1', '0', '0', '0', '1', '1', '1'),
                    ('1', '0', '0', '0', '0', '1', '1', '0', '0', '1'),
                    ('1', '0', '1', '1', '0', '0', '1', '1', '0'),
                    ('1', '1', '1', '0', '0', '1', '0', '0', '0', '1'),
                    ('0', '0', '0', '1', '0', '1', '1', '1', '1'),
                    ('1', '0', '1', '1', '1', '0', '0', '0', '0', '1'),
                    ('1', '1', '0', '0', '1', '0', '1', '1', '0'),
                    ('1', '0', '0', '1', '1', '1', '0', '1', '0', '1'),
                    ('0', '1', '1', '0', '0', '1', '0', '0', '1'),
                    ('1', '1', '0', '0', '1', '0', '0', '1', '0', '1'),
                    ('0', '0', '1', '1', '0', '1', '1', '0', '0'),
                    ('1', '1', '1', '0', '1', '1', '1', '0', '1', '1'),
                    ('0', '0', '1', '0', '0', '0', '0', '1', '0'),
                    ('1', '1', '0', '1', '1', '1', '0', '0', '1', '1'),
                    ('0', '1', '0', '0', '0', '1', '1', '0', '1'),
                    ('1', '0', '0', '0', '1', '0', '0', '1', '0', '0'),
                    ('1', '1', '1', '1', '1', '1', '1', '1', '1')
                ),
                'path': (
                    ('1', '1', '0', '0', '0', '0', '0', '0', '0'),
                    ('1', '1', '0', '0', '0', '0', '0', '0', '0'),
                    ('1', '1', '1', '1', '1', '0', '0', '0', '0'),
                    ('0', '0', '0', '0', '1', '0', '0', '0', '0'),
                    ('0', '0', '0', '0', '1', '1', '1', '1', '1'),
                    ('0', '0', '0', '0', '0', '0', '0', '1', '1'),
                    ('0', '0', '0', '0', '0', '0', '0', '1', '0'),
                    ('0', '0', '0', '0', '0', '0', '1', '1', '0'),
                    ('0', '0', '0', '0', '0', '0', '1', '1', '0'),
                    ('0', '0', '0', '0', '0', '0', '0', '1', '1')
                )
            },

        },
        'medium': {},
        'hard': {}
    }

    def __init__(self, difficulty: str, level: str) -> None:
        self._level = Level(self._levels[difficulty][level])
        self.player1 = Player()

    @property
    def levels(self) -> dict:
        return deepcopy(self._levels)


if __name__ == '__main__':
    game = Core('easy', 'level 1')

    print(game._level)