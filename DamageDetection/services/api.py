from fastapi import FastAPI
from pipeline_builder import AIModelPipelineBuilder
from inference.ModelFactory import ModelFactory
from utils.PreProcess import PreProcess
from utils.PostProcess import PostProcess
import gc

app = FastAPI()

@app.get("/")
async def check():
    return {"message": "FastAPI Active"}

loaded_models = {
    "detector": ModelFactory.create_model("YoloV8Detector", "../AI_Modles/YoloV8Detection.pt"),
    "segmenter": ModelFactory.create_model("YoloV8Segmenter", "../AI_Modles/YoloV8Segmentation.pt"),
    "classifire": ModelFactory.create_model("VggClassifire", "../AI_Modles/Vgg16Classification.h5")
}

#Maybe add a director to build the pipeline
def get_pipeline():
    return (
        AIModelPipelineBuilder(list(loaded_models.values()))
        .set_preprocessor(PreProcess()) 
        .set_postprocessor(PostProcess()) 
        .build()
    )

@app.post("/predict")
async def predict():
    #Incude db calls to retrive the image url
    #Most probably the object id will be sent
    pipeline = get_pipeline()
    image_path = "C:/Users/user/Desktop/SLIIT/Year 4 Semester 1/Demo Images/detectionTest1.jpg"
    result = pipeline.process_image(image_path)

    # Destroying the pipeline object after processing
    del pipeline
    gc.collect()

    return {"message": "Damage Detection Completed", "result": result}