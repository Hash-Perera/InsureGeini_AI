import aio_pika
import asyncio
import json
from dotenv import load_dotenv
import os

load_dotenv()

RABBITMQ_URL =  os.getenv("RABBITMQ_URL")
EXCHANGE_NAME =  os.getenv("EXCHANGE_NAME")

async def consume_and_forward():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()

        # Declare queues (ensure they exist)
        fraud_queue = await channel.declare_queue("fraud_detection_queue", durable=True)
      
        async for message in fraud_queue:
            async with message.process():
                data = json.loads(message.body)
                print(f"🟢 Received from fraud_detection_queue: {data}")

                # Simulate processing
                await asyncio.sleep(100)
                processed_data = {
                    "claimId": data["claimId"],
                    "status": "Fraud Check Completed",
                }
                print(f"✅ Fraud processing completed for: {data['claimId']}")

                exchange = await channel.get_exchange("insure_geini_exchange")

                # Publish the result to `policy_queue` in the exchange
                await exchange.publish(
                    aio_pika.Message(body=json.dumps(processed_data).encode("utf-8")),
                    routing_key="policy.key",  # Routing key for policy queue
                )
                print(f"📤 Sent to policy_queue: {processed_data}")


async def start_fraud_consumer():
    asyncio.create_task(consume_and_forward())

