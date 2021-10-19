from model import Core
from view import View
from view_model import ViewModel


def client_code(view):
    view.game_start()


if __name__ == '__main__':
    core = Core()
    viewModel = ViewModel(core)
    first_view = View(viewModel)

    client_code(first_view)
