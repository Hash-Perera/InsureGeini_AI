from YoloV8Detector import YoloV8Detector
from AiPipeline import AiPipeline

#instantiate models
detector = YoloV8Detector()


#loading models
detector_path = '../AI_Modles/YoloV8Detection.pt'
detector.load_model(detector_path)
#instsantiate pipeline components


#Create pipleine
pipeline = AiPipeline(detector)

#process an image
image_path = "C:/Users/user/Desktop/SLIIT/Year 4 Semester 1/Demo Images/detectionTest1.jpg"
pipeline.process_image(image_path)