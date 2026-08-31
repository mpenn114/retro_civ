from abc import ABC, abstractmethod
from pygame.event import Event
class BaseEvent(ABC):

    def __init__(self):
        """
        Define the base class for an event
        """
    @abstractmethod
    def handle(self, event:Event):
        """
        Handle the event associated with the class
        """
        raise NotImplementedError("Subclasses must implement this method")