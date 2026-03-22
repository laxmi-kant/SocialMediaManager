"""Celery application configuration."""

from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery("smm")

celery_app.config_from_object({
    "broker_url": settings.redis_url,
    "result_backend": settings.redis_url,
    "task_serializer": "json",
    "result_serializer": "json",
    "accept_content": ["json"],
    "timezone": "UTC",
    "enable_utc": True,
    "task_track_started": True,
    "task_time_limit": 300,
    "task_soft_time_limit": 240,
    "worker_prefetch_multiplier": 1,
    "worker_max_tasks_per_child": 100,
})

celery_app.conf.beat_schedule = {
    "fetch-trending-content": {
        "task": "app.tasks.research_tasks.fetch_trending_content",
        "schedule": crontab(minute=0, hour="*/2"),
        "options": {"queue": "research"},
    },
    "process-active-schedules": {
        "task": "app.tasks.generation_tasks.process_active_schedules",
        "schedule": crontab(minute="*/30"),
        "options": {"queue": "generation"},
    },
    "publish-scheduled-posts": {
        "task": "app.tasks.publishing_tasks.publish_scheduled_posts",
        "schedule": crontab(minute="*"),
        "options": {"queue": "publishing"},
    },
    "fetch-analytics": {
        "task": "app.tasks.analytics_tasks.fetch_analytics",
        "schedule": crontab(minute=0, hour="*/6"),
        "options": {"queue": "analytics"},
    },
    "collect-engager-profiles": {
        "task": "app.tasks.profile_tasks.collect_engager_profiles",
        "schedule": crontab(minute=30, hour="*/3"),
        "options": {"queue": "comments"},
    },
}

celery_app.autodiscover_tasks(["app.tasks"])
