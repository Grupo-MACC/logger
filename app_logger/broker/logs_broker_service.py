from microservice_chassis_grupo2.core.rabbitmq_core import get_channel, declare_exchange_logs
import json
from aio_pika import Message
from microservice_chassis_grupo2.core.router_utils import AUTH_SERVICE_URL

async def publish_to_logger(message, topic):
    connection = None
    try:
        connection, channel = await get_channel()
        
        exchange = await declare_exchange_logs(channel)
        
        # Asegúrate de que el mensaje tenga estos campos
        log_data = {
            "measurement": "logs",
            "service": topic.split('.')[0],
            "severity": topic.split('.')[1],
            **message
        }

        msg = Message(
            body=json.dumps(log_data).encode(), 
            content_type="application/json", 
            delivery_mode=2
        )
        await exchange.publish(message=msg, routing_key=topic)
        
    except Exception as e:
        print(f"Error publishing to logger: {e}")
    finally:
        if connection:
            await connection.close()