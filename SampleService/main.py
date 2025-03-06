import os
import asyncio
from contextlib import asynccontextmanager
import aio_pika
import json
from fastapi import FastAPI
from dotenv import load_dotenv 

load_dotenv()
# RabbitMQ connection settings
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
QUEUE_NAME = os.getenv("QUEUE_NAME")

# Define the async function before using it
async def consume_policy_queue():
    """
    Consumes messages from `policy_queue` and processes them.
    """
    try:
        # Connect to RabbitMQ
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()

            # Declare the queue (ensure it exists)
            queue = await channel.declare_queue(QUEUE_NAME, durable=True)

            async for message in queue:
                async with message.process():
                    # Decode message
                    data = json.loads(message.body)
                    print(f"🟢 Received policy message: {data}")

                    # Simulate policy validation process
                    await asyncio.sleep(100)
                    print(f"✅ Policy validation completed for claim {data['claimId']}")

    except Exception as e:
        print(f"❌ Error consuming messages: {e}")

# Define lifespan AFTER the function is defined
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start consuming messages when the app starts
    task = asyncio.create_task(consume_policy_queue())
    yield  # This allows the FastAPI app to start
    # Cleanup if necessary
    task.cancel()

# Initialize FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

@app.get("/")
def healthCheck():
    print('🟢 Sample server is running!')
    return {"status": "Hello! Sample server is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
    # uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
