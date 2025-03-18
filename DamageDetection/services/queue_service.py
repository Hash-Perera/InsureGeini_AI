
from services.damage_detector import damage_Detector
import aio_pika
import asyncio
import json
from dotenv import load_dotenv
import os
from services.database import update_claim_status_end, update_claim_status_start

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME")

async def consume_and_forward():
    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            damage_queue = await channel.declare_queue("damage_detection_queue", durable=True)

            async for message in damage_queue:
                async with message.process():
                    try:
                        data = json.loads(message.body)
                        claimId = data.get('claimId')

                        print(f"🔍 Processing damage detection for: {claimId}")

                        if not claimId:
                            print("⚠️ Missing claimId in message. Skipping.")
                            continue

                        # Update the claim status to 'Fraud Detection Started'
                        await update_claim_status_start(claimId)

                        result = await damage_Detector(claimId)
                        
                        if not result:
                            print(f"⚠️ Damage detection failed for claimId: {claimId}")
                            continue

                        
                        # Update claim status in the database
                        await update_claim_status_end(claimId)

                     

                        exchange = await channel.get_exchange("insure_geini_exchange")

                        # Publish the result to `fraud_queue` in the exchange
                        await exchange.publish(
                            aio_pika.Message(body=json.dumps({"claimId": claimId}).encode("utf-8")),
                            routing_key="fraud.key",  # Routing key for policy queue
                        )

                        print(f"📤 Sent to fraud_queue: {claimId}")

                    except Exception as e:
                        print(f"❌ Error processing message: {e}")
                        continue  # Ensure the loop continues even if an error occurs

    except Exception as e:
        print(f"❌ Critical Error in consume_and_forward: {e}")

async def start_damage_consumer():
    asyncio.create_task(consume_and_forward())
