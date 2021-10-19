from abc import ABC, abstractmethod


class Publisher:
    def __init__(self):
        self._subscribers = []

    def subscribe(self, subscriber):
        self._subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        del (stack := self._subscribers)[stack.index(subscriber)]

    @abstractmethod
    def notify(self): pass


class Subscriber(ABC):
    @abstractmethod
    def update(self, *args): pass
