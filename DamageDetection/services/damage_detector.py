
from bson import ObjectId
from services.pipeline_builder import AIModelPipelineBuilder
from services.inference.ModelFactory import ModelFactory
from services.utils.PreProcess import PreProcess
from services.utils.PostProcess import PostProcess
from services.DB_models.detection_model import DetectionModel
from services.DTO.DetectionRequest import DetectionRequest
from services.database import db
from services.utils.aws import download_image_from_s3, get_image_from_s3
import gc
from PIL import Image
import io

loaded_models = {
    "detector": ModelFactory.create_model("YoloV8Detector", "./AI_Modles/YoloV8Detection.pt"),
    "segmenter": ModelFactory.create_model("YoloV8Segmenter", "./AI_Modles/YoloV8Segmentation.pt"),
    "classifire": ModelFactory.create_model("VggClassifire", "./AI_Modles/Vgg16Classification.h5")
}

#Maybe add a director to build the pipeline
def get_pipeline():
    return (
        AIModelPipelineBuilder(list(loaded_models.values()))
        .set_preprocessor(PreProcess()) 
        .set_postprocessor(PostProcess()) 
        .build()
    )


async def damage_Detector(claimId):
    try:
        # Step 1: Fetch claim data
        try:
            claim = await db.claims.find_one(
                {"_id": ObjectId(claimId)},
                {"damageImages": 1, "obdCodes": 1, "_id": 0}
            )
            if not claim:
                print(f"[ERROR] Claim not found for ID: {claimId}")
                return {"status": "error", "message": "Claim not found."}
        except Exception as db_error:
            print(f"[CRITICAL] Failed to retrieve claim data: {db_error}")
            return {"status": "error", "message": "Database query failed."}

        # Step 2: Extract and validate OBD codes
        try:
            obd_codes = claim.get("obdCodes", "")
            obd_codes_list = obd_codes.split(",") if obd_codes else []
        except Exception as code_error:
            print(f"[ERROR] Failed to process OBD codes: {code_error}")
            obd_codes_list = []

        # Step 3: Extract and load image
        try:
            image_urls = claim.get("damageImages", [])
            if not image_urls:
                print("[ERROR] No damage images found in claim.")
                return {"status": "error", "message": "No damage images provided."}

            img_url = image_urls[0]
            image = get_image_from_s3(img_url)
        except Exception as image_error:
            print(f"[ERROR] Failed to load damage image from S3: {image_error}")
            return {"status": "error", "message": "Image loading failed."}

        # Step 4: Create and use AI pipeline
        try:
            pipeline = get_pipeline()
            result = await pipeline.process_image(image, obd_codes_list, claimId)

            print(result)

            if result is None or not isinstance(result, list):
                print(f"[FATAL] process_image() returned invalid result.")
                return {"status": "error", "message": "Image processing failed."}
        except Exception as pipeline_error:
            print(f"[CRITICAL] Pipeline processing failed: {pipeline_error}")
            return {"status": "error", "message": "AI pipeline execution failed."}

        # Step 5: Structure detection documents
        detection_docs = []
        try:
            for d in result:
                detection_docs.append(
                    DetectionModel(
                        claimId=ObjectId(claimId),
                        part=d.get("part", "Unknown"),
                        damageType=d.get("damageType", []),
                        severity=d.get("severity", "Unknown"),
                        obd_code=d.get("obd_code", False),
                        internal=d.get("internal", "Not detected"),
                        decision=d.get("decision", "Null"),
                        reason=d.get("reason", "Unknown"),
                        image_url=d.get("image_url", ""),
                        cost=d.get("cost", 0),
                        flag=d.get("flag", "-")
                    ).model_dump(exclude_unset=True)
                )
        except Exception as doc_error:
            print(f"[ERROR] Failed to build detection document: {doc_error}")
            return {"status": "error", "message": "Failed to structure result."}

        # Step 6: Insert results to database
        try:
            inserted_results = await db.detections.insert_many(detection_docs)
            print(f"[INFO] Inserted detection results: {inserted_results.inserted_ids}")
        except Exception as insert_error:
            print(f"[ERROR] Failed to insert detections: {insert_error}")
            return {"status": "error", "message": "Failed to store results."}

        # Step 7: Cleanup
        del pipeline
        gc.collect()

        return {"status": "success", "message": "Damage Detection Completed"}

    except Exception as e:
        print(f"[FATAL] damage_Detector crashed: {e}")
        return {"status": "error", "message": "Unexpected server error during damage detection."}
