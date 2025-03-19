# import aio_pika
# import asyncio
# import json
# from dotenv import load_dotenv
# import os
# from services.z_detector import excute_fraud_detector
# from database import insert_to_fraud_collection, update_claim_status

# load_dotenv()

# RABBITMQ_URL =  os.getenv("RABBITMQ_URL")
# EXCHANGE_NAME =  os.getenv("EXCHANGE_NAME")

# async def consume_and_forward():
#     connection = await aio_pika.connect_robust(RABBITMQ_URL)
#     async with connection:
#         channel = await connection.channel()

#         # Declare queues (ensure they exist)
#         fraud_queue = await channel.declare_queue("fraud_detection_queue", durable=True)
      
#         async for message in fraud_queue:
#             async with message.process():



#                 data = json.loads(message.body)
#                 claimId = data['claimId']
               
#                 print(f"🔍 Processing fraud detection for: {claimId}")

#                 result = await excute_fraud_detector(claimId);
#                 new_fraud_record = await insert_to_fraud_collection(result, claimId)
#                 # Update claim status in the database
#                 await update_claim_status(claimId)

#                 print(f"📝 Inserted to fraud collection: {new_fraud_record}")

#                 exchange = await channel.get_exchange("insure_geini_exchange")

#                 # Publish the result to `policy_queue` in the exchange
#                 await exchange.publish(
#                     aio_pika.Message(body=json.dumps({"claimId": claimId}).encode("utf-8")),
#                     routing_key="policy.key",  # Routing key for policy queue
#                 )

#                 print(f"📤 Sent to policy_queue: {data['claimId']}")


# async def start_fraud_consumer():
#     asyncio.create_task(consume_and_forward())


import aio_pika
import asyncio
import json
from dotenv import load_dotenv
import os
from services.z_detector import excute_fraud_detector
from database import insert_to_fraud_collection, update_claim_status_end, update_claim_status_start

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME")

async def consume_and_forward():
    try:
        connection = await aio_pika.connect_robust(
            RABBITMQ_URL, reconnect_interval=5, heartbeat=120
        )
        async with connection:
            channel = await connection.channel()
            fraud_queue = await channel.declare_queue("fraud_detection_queue", durable=True)

            async for message in fraud_queue:
                async with message.process():
                    try:
                        data = json.loads(message.body)
                        claimId = data.get('claimId')

                        print(f"🔍 Processing fraud detection for: {claimId}")

                        if not claimId:
                            print("⚠️ Missing claimId in message. Skipping.")
                            continue

                        # Update the claim status to 'Fraud Detection Started'
                        await update_claim_status_start(claimId)

                        result = await excute_fraud_detector(claimId)
                        
                        if not result:
                            print(f"⚠️ Fraud detection failed for claimId: {claimId}")
                            continue

                        new_fraud_record = await insert_to_fraud_collection(result, claimId)
                        
                        # Update claim status in the database
                        await update_claim_status_end(claimId)

                        print(f"📝 Inserted to fraud collection: {new_fraud_record}")

                        exchange = await channel.get_exchange("insure_geini_exchange")

                        # Publish the result to `policy_queue` in the exchange
                        await exchange.publish(
                            aio_pika.Message(body=json.dumps({"claimId": claimId}).encode("utf-8")),
                            routing_key="policy.key",  # Routing key for policy queue
                        )

                        print(f"📤 Sent to policy_queue: {claimId}")

                    except Exception as e:
                        print(f"❌ Error processing message: {e}")
                        continue 

    except Exception as e:
        print(f"❌ Critical Error in consume_and_forward: {e}")

async def start_fraud_consumer():
    asyncio.create_task(consume_and_forward())