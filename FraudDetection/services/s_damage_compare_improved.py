from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch
import requests
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor

# Load CLIP model and processor only once
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
model.eval()

def download_image(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content)).convert("RGB")
    except Exception as e:
        raise ValueError(f"Failed to fetch image from {image_url}: {str(e)}")

def compute_clip_embeddings(image_urls):
    # Download images in parallel
    with ThreadPoolExecutor() as executor:
        images = list(executor.map(download_image, image_urls))

    # Batch process images for embedding
    inputs = processor(images=images, return_tensors="pt", padding=True)
    with torch.no_grad():
        embeddings = model.get_image_features(**inputs)
    return embeddings

def damage_compare_improved(image_urls_1, image_urls_2):
    try:
        # Compute all embeddings once
        embeddings_1 = compute_clip_embeddings(image_urls_1)
        embeddings_2 = compute_clip_embeddings(image_urls_2)

        # Normalize embeddings to improve cosine similarity results
        embeddings_1 = torch.nn.functional.normalize(embeddings_1, p=2, dim=1)
        embeddings_2 = torch.nn.functional.normalize(embeddings_2, p=2, dim=1)

        # Prepare results
        results = []

        for idx1, emb1 in enumerate(embeddings_1):
            for idx2, emb2 in enumerate(embeddings_2):
                similarity = torch.nn.functional.cosine_similarity(
                    emb1.unsqueeze(0), emb2.unsqueeze(0)
                ).item()

                message = (
                    "Images represent the same damage (possible fraud)."
                    if similarity > 0.89 else
                    "Images represent different damages."
                )

                results.append({
                    "image_url_1": image_urls_1[idx1],
                    "image_url_2": image_urls_2[idx2],
                    "similarity_score": round(similarity, 4),
                    "message": message
                })

        return {
            "status": True,
            "error": None,
            "results": results
        }

    except Exception as e:
        return {
            "status": False,
            "error": str(e),
            "results": None
        }
