import logging
from django_redis import get_redis_connection
import json

logger = logging.getLogger(__name__)

def queue_email_task(email: str, task_type: str, context: dict, stream_name: str = "email_sending_queue"):
    """
    Pushes an email-related task to a Redis Stream for a worker to process.

    Args:
        email (str): The recipient's email address.
        task_type (str): The type of task for the worker (e.g., 'otp_verification').
        context (dict): The context data for the email template.
        stream_name (str): The name of the Redis Stream.

    Returns:
        bool: True if the message was sent successfully, False otherwise.
    """
    try:
        redis_conn = get_redis_connection("default")
        message = {
            "email": email,
            "type": task_type,
            "context": json.dumps(context),
        }
        redis_conn.xadd(stream_name, message)
        logger.info(f"Successfully queued task '{task_type}' for {email} to stream '{stream_name}'.")
        return True
    except Exception as e:
        logger.error(f"Failed to queue task '{task_type}' for {email}: {e}", exc_info=True)
        return False
