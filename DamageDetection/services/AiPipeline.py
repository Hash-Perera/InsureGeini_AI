#Add code for the ochastrator to manage and controll everything an the sequence
#Call all the methods from here only
#bring all objects here in the init method
#methods in this class will be called in the main.py
class AiPipeline:
    
    #change individual model instantiation for dynamic later
    def __init__(self,detector):
        self.detector = detector

    
    def process_image(self,image_path):
        #preprocess

        #Running inference
        #Make this dynamic later
        detection_results = self.detector.predict(image_path)
        print(detection_results)

        #Post process