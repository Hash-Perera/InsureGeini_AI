from abc import ABC, abstractmethod
class BaseModel(ABC):
    
    @abstractmethod
    def load_model(self,path):
        pass

    @abstractmethod
    def predict(self,image):
        pass