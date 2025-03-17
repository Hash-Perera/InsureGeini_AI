from bson import ObjectId
from fastapi import FastAPI
from crud.claim import get_claim
from helpers.util import download_audio_file, extract_metadata_from_audio_file_url

app = FastAPI(
    title="Claims Processing API",
    description="API for processing insurance claims",
    version="1.0.0",
)


async def main(claim_id: str | ObjectId) -> dict:
    if not ObjectId.is_valid(claim_id):
        return {"error": "Invalid claim_id"}

    claim_record: dict = await get_claim(claim_id)
    audio_file_url: str = claim_record.get("audio")
    audio_file_metadata: dict = await extract_metadata_from_audio_file_url(
        audio_file_url
    )
    audio_file_saved_path: str | None = await download_audio_file(
        audio_file_metadata,
        f"./temp/{audio_file_metadata.get('user_id')}/{audio_file_metadata.get('claim_number')}/{audio_file_metadata.get('audio_file_name')}",
    )
    if audio_file_saved_path is None:
        return {"error": "Failed to download audio file"}
    
    

@app.get("/", response_model=None)
async def read_root(claim_id: str = "67d5ac786c933d00f0f95d49") -> dict:
    await main(claim_id)
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
