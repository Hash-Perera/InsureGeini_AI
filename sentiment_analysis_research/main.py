from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from helper import preprocessing, vectorizer_tfidf, get_prediction, get_prediction_c

# Initialize FastAPI app
app = FastAPI()

# Define request model
class FeedbackRequest(BaseModel):
    feedback: str


@app.get("/")
async def healthcheck():
    """
    Healthcheck endpoint.
    """
    return "Sentiment Analysis API is running CI/CD Tested!"

@app.post("/feedback")
async def predict_sentiment(request: FeedbackRequest):
    """
    Predict sentiment from feedback.
    """
    try:
        # Preprocess and vectorize the input feedback
        preprocessed_feedback = preprocessing(request.feedback)
        vectorized_feedback = vectorizer_tfidf(preprocessed_feedback)
        prediction = get_prediction(vectorized_feedback)
        return {"prediction": prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/category")
async def predict_category(request: FeedbackRequest):
    """
    Predict category from feedback.
    """
    try:
        # Preprocess and vectorize the input feedback
        preprocessed_feedback = preprocessing(request.feedback)
        vectorized_feedback = vectorizer_tfidf(preprocessed_feedback)
        prediction = get_prediction_c(vectorized_feedback)
        return {"prediction": prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI server using uvicorn (if required as standalone)
# uvicorn app:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
    # uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)