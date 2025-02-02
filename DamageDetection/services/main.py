from YoloV8Detector import YoloV8Detector
from YoloV8Segmenter import YoloV8Segmenter
from AiPipeline import AiPipeline

#instantiate models
detector = YoloV8Detector()
segmenter = YoloV8Segmenter()


#loading models
detector_path = '../AI_Modles/YoloV8Detection.pt'
detector.load_model(detector_path)

segmenter.load_model('../AI_Modles/YoloV8Segmentation.pt')
#instsantiate pipeline components


#Create pipleine
pipeline = AiPipeline(detector,segmenter)


#process an image
image_path = "C:/Users/user/Desktop/SLIIT/Year 4 Semester 1/Demo Images/detectionTest1.jpg"
pipeline.process_image(image_path)