from abc import ABC, abstractmethod


class InputHandler(ABC):
    """
    Abstract base class for handling input to the system
    Contains thread-like functionality
    """

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass
