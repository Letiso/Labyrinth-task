# Exceptions
class Error(Exception):
    _error = None

    def __init__(self) -> None:
        self._name: str = 'Шарик'

    def __str__(self) -> str:
        return self._error


class HittingTheWallError(Error):
    def __init__(self) -> None:
        super().__init__()
        self._error: str = f"{self._name} ударился о стену"


class WrongPathError(Error):
    def __init__(self) -> None:
        super().__init__()
        self._error: str = f"{self._name} заблудился"


class BackStepError(Error):
    def __init__(self) -> None:
        super().__init__()
        self._error: str = f"{self._name} струсил и убежал"


class Congratulations(Error):
    def __init__(self) -> None:
        super().__init__()
        self._error: str = f"{self._name} нашел косточку"


class ExitGame(Exception): pass
