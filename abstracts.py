import abc
# compatible with Python 2 *and* 3
# https://stackoverflow.com/questions/35673474/using-abc-abcmeta-in-a-way-it-is-compatible-both-with-python-2-7-and-python-3-5
ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})

class Scene(ABC):
    @abc.abstractmethod
    def render(self):
        pass

    @abc.abstractmethod
    def moveCameraBy(self, x, y):
        pass

class Threadable(ABC):
    @abc.abstractmethod
    def run(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass
