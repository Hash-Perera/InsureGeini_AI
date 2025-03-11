from AiPipeline import AiPipeline
from utils.PreProcess import PreProcess
from utils.PostProcess import PostProcess

class AIModelPipelineBuilder:

    def __init__(self, models):
        self.models = models
        self.preprocessor = None
        self.postprocessor = None

    def set_preprocessor(self, preprocessor):
        self.preprocessor = preprocessor
        return self
    
    def set_postprocessor(self, postprocessor):
        self.postprocessor = postprocessor
        return self
    
    def build(self):
        return AiPipeline(models=self.models, preprocessor=self.preprocessor, postprocessor=self.postprocessor)