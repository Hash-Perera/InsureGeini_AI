from fastapi import FastAPI


app = FastAPI()

@app.get("/")
async def ping():
    return "Hello, I am alive!"

@app.get("/array")
async def arrayOutput():
    return [
        {'Hashan': '1'},
    ]
