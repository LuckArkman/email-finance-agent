from celery import Celery
from app.config import BaseAPIConfig

settings = BaseAPIConfig.get_settings()

class CeleryManager:
    @staticmethod
    def create_celery_app() -> Celery:
        # Use redis as message broker and result backend
        celery_app = Celery(
            "finance_agent_worker",
            broker=settings.redis_url,
            backend=settings.redis_url,
            include=["app.tasks.ocr_tasks"]
        )
        
        # Configure advanced celery settings
        celery_app.conf.update(
            task_serializer="json",
            accept_content=["json"],
            result_serializer="json",
            timezone="UTC",
            enable_utc=True,
            # Routing specific queues
            task_routes={
                "app.tasks.ocr_tasks.*": {"queue": "ai_queue"},
            },
            # Acknowledge task only after execution
            task_acks_late=True,
            worker_prefetch_multiplier=1,
            task_reject_on_worker_lost=True,
        )
        return celery_app

celery_app = CeleryManager.create_celery_app()
