from abc import ABC, abstractmethod

class Scene(ABC):
    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def moveCameraBy(self, x, y):
        pass

class Threadable(ABC):
    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def stop(self):
        pass
