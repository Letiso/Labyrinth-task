from abc import ABC, abstractmethod
from typing import Optional
from copy import deepcopy
from exceptions import *
import pickle


# Cells abstract class
class Cell(ABC):
    _show = None

    @property
    def show(self):
        return self._show

    @abstractmethod
    def __str__(self) -> str: pass


# Walls base class
class Wall:
    def __init__(self, show: int) -> None:
        self._show: int = show

    def __radd__(self, player: 'Player') -> Optional[bool]:
        if not self._show: return True
        else:
            raise HittingTheWallError()


# Walls
class VerticalWall(Cell, Wall):
    def __str__(self) -> str:
        return ' ' if not self._show else '|'


class HorizontalWall(Cell, Wall):
    def __str__(self) -> str:
        return '  ' if not self._show else '——'


class AdjacentWall(Cell):
    _views: dict = {
        'lurd': '+',

        '_u__': '|',
        '_u_d': '|',
        '___d': '|',

        'l_r_': '—',
        'l___': '—',
        '__r_': '—',

        '____': ' ',

        'lu__': '┘',
        '_ur_': '└',

        'l__d': '┐',
        '__rd': '┌',

        'lur_': '┴',
        'l_rd': '┬',

        '_urd': '├',
        'lu_d': '┤',

    }

    _view = None

    def init(self, key: str):
        self._show = True
        self._view = self._views[key]

    def __str__(self) -> str:
        return ' ' if not self._show else self._view


class StartAndFinish(Cell):
    def __init__(self, cell_type: str):
        self._type: str = cell_type

    def __str__(self):
        return ' '

    def __radd__(self, player: 'Player'):
        match self._type:
            case 'Start': raise BackStepError()
            case 'Finish': raise Congratulations()


# Path cells
class Path(Cell):
    _status: str = None
    _right_path: bool = None

    def set_right_path(self):
        self._right_path = True

    def set_status(self, status: str):
        self._status = status

    def __str__(self) -> str:
        # return '  ' if not self._right_path else '++'
        return '  '

    def __radd__(self, player: 'Player') -> bool:
        if not self._right_path:
            raise WrongPathError()
        else:
            match self._status:
                case None: return True
                case 'SavePoint': raise BackStepError()


class Player(Cell):
    _currentPathCell: Path = None
    current_pos = {
        'x': 0,
        'y': 0
    }

    @property
    def path(self):
        return self._currentPathCell

    @path.setter
    def path(self, new_path: Path):
        self._currentPathCell = new_path

    def __str__(self) -> str:
        return '<>'


# Map
class Level:
    def __init__(self, level_generator: dict) -> None:
        self._matrix = []
        self._generate_matrix(level_generator['walls'])
        self._configure_adjacent_walls()
        self._right_path_init(level_generator['path'])

    @property
    def matrix(self):
        return self._matrix

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

    def _configure_adjacent_walls(self):
        for y, string in enumerate(self._matrix):
            if y % 2 == 0:
                for x, wall in enumerate(string):
                    if isinstance(wall, AdjacentWall):
                        key = str()
                        for side in 'l', 'u', 'r', 'd':
                            side_x, side_y = (1 if side == 'r'
                                              else - 1 if side == 'l'
                                              else 0,

                                              -1 if side == 'u'
                                              else 1 if side == 'd'
                                              else 0)
                            try:
                                side_x, side_y = side_x + x, side_y + y
                                if side_x == -1 or side_y == -1: raise IndexError

                                if self._matrix[side_y][side_x].show:
                                    key += side
                                else:
                                    key += '_'
                            except IndexError:
                                key += '_'
                        wall.init(key)

    def _right_path_init(self, path_code: tuple):
        for string_code, string in zip(path_code, [string for y, string
                                                   in enumerate(self._matrix)
                                                   if y % 2 != 0]):
            for mode, path in zip(string_code, [cell for cell in string
                                                if isinstance(cell, Path)]):
                if int(mode): path.set_right_path()

    def start_and_finish_init(self, player: Player):
        for y, string in enumerate(self._matrix):
            if y % 2 != 0 and str(string[0]) == ' ':
                string[0] = StartAndFinish('Start')
                player.path = string[1]
                string[1] = player

                player.current_pos['x'] = 1
                player.current_pos['y'] = y
                break

        for y, string in enumerate(self._matrix):
            if y % 2 != 0 and str(string[-1]) == ' ':
                string[-1] = StartAndFinish('Finish')
                break

    def __str__(self) -> str:
        result = str()
        for string in self._matrix:
            result += '\t' * 3
            for cell in [str(cell) for cell in string]:
                result += cell
            result += '\n'
        return result


class Save:
    def __init__(self, level: Level, player: Player):
        self._level = level
        self._player = player

    def load(self):
        return self._level, self._player


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
    _level = _player = None

    @property
    def levels(self) -> dict:
        return deepcopy(self._levels)

    @property
    def level(self):
        return self._level

    def new_game(self, difficulty: str, level: str) -> None:
        self._level = Level(self._levels[difficulty][level])
        self._player = Player()
        self._level.start_and_finish_init(self._player)
        self._save_game()

    def _save_game(self):
        memento = Save(self._level, self._player)
        with open('save.pickle', 'wb') as save:
            pickle.dump(memento, save)

    def load_game(self):
        with open('save.pickle', 'rb') as save:
            self._level, self._player = pickle.load(save).load()

    def move_to(self, side: str):
        x, y = self._player.current_pos['x'], self._player.current_pos['y']
        side_x, side_y = (1 if side == 'right'
                          else - 1 if side == 'left'
                          else 0,

                          -1 if side == 'up'
                          else 1 if side == 'down'
                          else 0)

        """checking wall transparency"""
        # noinspection PyUnresolvedReferences
        if self._player + self._level.matrix[y + side_y][x + side_x]:

            """checking right path"""
            # noinspection PyUnresolvedReferences
            if self._player + self._level.matrix[(side_y := y + side_y * 2)][(side_x := x + side_x * 2)]:
                """player movement"""
                self._player.current_pos['x'] = side_x
                self._player.current_pos['y'] = side_y

                self._level.matrix[y][x] = self._player.path
                self._player.path = self._level.matrix[side_y][side_x]
                self._level.matrix[side_y][side_x] = self._player

                self._save_game()
