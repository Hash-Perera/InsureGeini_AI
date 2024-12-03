from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

def damage_compare(image_path_1, image_path_2):
    try:
        # Load CLIP model
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        def compute_clip_embedding(image_path):
            try:
                image = Image.open(image_path)
                inputs = processor(images=image, return_tensors="pt")
                outputs = model.get_image_features(**inputs)
                return outputs
            except Exception as e:
                raise ValueError(f"Failed to process image at {image_path}: {str(e)}")

        def compare_images_clip(image_path1, image_path2):
            try:
                embedding1 = compute_clip_embedding(image_path1)
                embedding2 = compute_clip_embedding(image_path2)

                similarity = torch.nn.functional.cosine_similarity(embedding1, embedding2)
                return similarity.item()
            except Exception as e:
                raise ValueError(f"Error comparing images: {str(e)}")

        # Compare the two images
        similarity_score = compare_images_clip(image_path_1, image_path_2)

        # Define result based on similarity threshold
        if similarity_score > 0.89:
            message = "Images represent the same damage (possible fraud)."
        else:
            message = "Images represent different damages."

        # Return success response
        return {
            "status": True,
            "error": None,
            "similarity_score": similarity_score,
            "message": message
        }

    except Exception as e:
        # Handle any unexpected errors
        return {
            "status": False,
            "error": str(e),
            "similarity_score": None,
            "message": None
        }
