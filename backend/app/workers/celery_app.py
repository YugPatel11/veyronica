"""Celery application configuration.

Defines task queues, routing, and serialisation settings.
Workers and beat scheduler import this module.
"""

from __future__ import annotations

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "nexus",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    # Serialisation
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    # Reliability
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    # Memory management
    worker_max_tasks_per_child=100,
    # Task routing — queues defined for Phase 2
    task_default_queue="default",
    task_queues={},
    task_routes={},
    # Beat schedule — populated in Phase 2
    beat_schedule={},
)
