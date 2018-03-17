from abc import ABC, abstractmethod

class AbstractPlugin(ABC):
    
    @abstractmethod
    def doIt(self,args=None):
        pass