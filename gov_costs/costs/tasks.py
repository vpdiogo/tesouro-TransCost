"""Celery tasks para ingestão periódica de dados."""

import logging

from celery import shared_task
from django.core.management import call_command

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def ingest_dataset(self, dataset_key):
    """Ingest a single dataset from Tesouro Nacional."""
    try:
        logger.info("Starting ingestion of %s", dataset_key)
        call_command("ingest_costs", dataset=dataset_key)
        logger.info("Finished ingestion of %s", dataset_key)
    except Exception as exc:
        logger.error("Failed to ingest %s: %s", dataset_key, exc)
        raise self.retry(exc=exc)


@shared_task
def ingest_all_datasets():
    """Ingest all datasets sequentially."""
    from costs.client import DATASETS

    for dataset_key in DATASETS:
        ingest_dataset.delay(dataset_key)
