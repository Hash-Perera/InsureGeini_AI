#Add code for the ochastrator to manage and controll everything an the sequence
#Call all the methods from here only
#bring all objects here in the init method
#methods in this class will be called in the main.py

import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate

class AiPipeline:
    
    #change individual model instantiation for dynamic later
    def __init__(self,models,preprocessor,postprocessor):
        self.models = models
        self.preprocessor = preprocessor
        self.postprocessor = postprocessor

    
    def process_image(self,image_path):
        #preprocess
        preprocessed_image = self.preprocessor.preprocess(image_path)

        #Running inference

        results = {}


        for model in self.models:
            model_name = model.__class__.__name__
            # Add else if statement for detection model to extract the bounding box coordinates crop the images
            if model_name == "VggClassifire":
                results[model_name] = model.predict(preprocessed_image["tensorflow"])
                cropped_images = self.preprocessor.preprocess_cropped_images(image_path, results["YoloV8Detector"])
                severity_results = []
                count = 0
                for image_array, part_label, cropped_part in cropped_images:
                    count += 1
                    result = model.predict(image_array)
                    severity_results.append((str(count)+" "+part_label, result["class_name"]))
                # print(severity_results)
                results["PartSeverity"] = severity_results
            else:
                results[model_name] = model.predict(image_path)


        # print(results)
        #Post process
        postprocessed_results = self.postprocessor.match_damage_to_part(results["YoloV8Detector"],results["YoloV8Segmenter"])
        
        #Final result
        final_result = self.postprocessor.create_vector(results["PartSeverity"],postprocessed_results)

        #To be removed

        # Convert list values in 'damageType' column to comma-separated strings
        for entry in final_result:
            entry['damageType'] = ', '.join(entry['damageType'])

        # Create a tabulated format for display
        table = tabulate(final_result, headers="keys", tablefmt="grid")

        # Print the formatted table
        print(table)