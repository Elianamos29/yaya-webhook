from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.db import transaction
from .models import WebhookEvent
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_webhook_event(self, event_id):
    try:
        with transaction.atomic():
            event = WebhookEvent.objects.select_for_update().get(id=event_id)

            if event.processed:
                logger.info(f"Webhook event {event_id} already processed")
                return
            
            logger.info(f"Processing webhook event {event_id}")
            
            try:
                handle_event(event)

                event.processed = True
                event.save()
                logger.info(f"Successfully processed webhook event: {event.event_id}")
            except Exception as processing_error:
                logger.error(f"Error processing webhook event {event_id}: {str(processing_error)}")

                event.processed = True
                event.save()
                raise
    except WebhookEvent.DoesNotExist:
        logger.error(f"Webhook event {event_id} does not exist.")
    except Exception as e:
        logger.error(f"Error processing webhook event {event_id}: {str(e)}")
        try:
            raise self.retry(exc=e, countdown=60 * self.request.retries)
        except MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for webhook event {event_id}")

            try:
                event = WebhookEvent.objects.get(id=event_id)
                event.processed = True
                event.save()
            except WebhookEvent.DoesNotExist:
                pass

@shared_task
def cleanup_old_webhooks(days=30):
    try:
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count, _ = WebhookEvent.objects.filter(
            received_at__lt=cutoff_date
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} old webhook events")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error cleaning up old webhooks: {str(e)}")
        raise

@shared_task
def retry_failed_webhooks():
    try:
        retry_cutoff = timezone.now() - timedelta(minutes=5)
        failed_events = WebhookEvent.objects.filter(
            processed=False,
            received_at__lt=retry_cutoff
        )
        
        for event in failed_events:
            process_webhook_event.delay(event.id)
            
        logger.info(f"Retrying {failed_events.count()} failed webhook events")
        return failed_events.count()
        
    except Exception as e:
        logger.error(f"Error retrying failed webhooks: {str(e)}")
        raise
        

def handle_event(event):
    if event.event_type == 'payment_confirmed':
        logger.info(f"Handling payment confirmed for event {event.id}")
    elif event.event_type == 'payment_received':
        logger.info(f"Handling payment received for event {event.id}")
    elif event.event_type == 'recurring_payment':
        logger.info(f"Handling recurring payment for event {event.id}")
    elif event.event_type == 'subscription_payment':
        logger.info(f"Handling subscription payment for event {event.id}")
    else:
        logger.warning(f"Unknown event type {event.event_type} for event {event.id}")

@shared_task
def test_celery_connection():
    logger.info("Celery test task executed successfully")
    return "Celery is working!"