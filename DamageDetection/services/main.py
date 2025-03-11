from inference.YoloV8Detector import YoloV8Detector
from inference.YoloV8Segmenter import YoloV8Segmenter
from inference.VggClassifire import VggClassifire
from inference.ModelFactory import ModelFactory
from utils.PreProcess import PreProcess
from utils.PostProcess import PostProcess
from AiPipeline import AiPipeline

#instantiate models
# detector = YoloV8Detector()
# segmenter = YoloV8Segmenter()
# classifire = VggClassifire()


#loading models
# detector.load_model('../AI_Modles/YoloV8Detection.pt')

# segmenter.load_model('../AI_Modles/YoloV8Segmentation.pt')

# classifire.load_model('../AI_Modles/Vgg16Classification.h5')

detector = ModelFactory.create_model("YoloV8Detector", "../AI_Modles/YoloV8Detection.pt")
segmenter = ModelFactory.create_model("YoloV8Segmenter", "../AI_Modles/YoloV8Segmentation.pt")
classifire = ModelFactory.create_model("VggClassifire", "../AI_Modles/Vgg16Classification.h5")


#instsantiate pipeline components
preprocessor = PreProcess()
postprocessor = PostProcess()


#Create pipleine
pipeline = AiPipeline(models=[detector,segmenter,classifire], preprocessor=preprocessor, postprocessor=postprocessor)


#process an image
image_path = "C:/Users/user/Desktop/SLIIT/Year 4 Semester 1/Demo Images/detectionTest1.jpg"
pipeline.process_image(image_path)