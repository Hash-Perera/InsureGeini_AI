from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch
import requests
from io import BytesIO

def damage_compare(image_urls_1, image_urls_2):
    try:
        # Load CLIP model
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        def compute_clip_embedding(image_url):
            try:
                # Fetch the image from the URL
                response = requests.get(image_url)
                response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
                image = Image.open(BytesIO(response.content))
                inputs = processor(images=image, return_tensors="pt")
                outputs = model.get_image_features(**inputs)
                return outputs
            except Exception as e:
                raise ValueError(f"Failed to process image from URL {image_url}: {str(e)}")

        def compare_images_clip(image_url1, image_url2):
            try:
                embedding1 = compute_clip_embedding(image_url1)
                embedding2 = compute_clip_embedding(image_url2)

                similarity = torch.nn.functional.cosine_similarity(embedding1, embedding2)
                return similarity.item()
            except Exception as e:
                raise ValueError(f"Error comparing images: {str(e)}")

        # Initialize a list to store the results
        results = []

        # Compare each image in the first array with each image in the second array
        for image_url_1 in image_urls_1:
            for image_url_2 in image_urls_2:
                similarity_score = compare_images_clip(image_url_1, image_url_2)

                # Define result based on similarity threshold
                if similarity_score > 0.89:
                    message = "Images represent the same damage (possible fraud)."
                else:
                    message = "Images represent different damages."

                # Append the result to the list
                results.append({
                    "image_url_1": image_url_1,
                    "image_url_2": image_url_2,
                    "similarity_score": similarity_score,
                    "message": message
                })

        # Return success response with all results
        return {
            "status": True,
            "error": None,
            "results": results
        }

    except Exception as e:
        # Handle any unexpected errors
        return {
            "status": False,
            "error": str(e),
            "results": None
        }


