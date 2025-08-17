# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0
import logging

from kink import inject
from procrastinate import Blueprint, JobContext, builtin_tasks

from beeai_server.configuration import Configuration
from beeai_server.service_layer.services.contexts import ContextService
from beeai_server.service_layer.unit_of_work import IUnitOfWorkFactory

blueprint = Blueprint()

logger = logging.getLogger(__name__)


@blueprint.periodic(cron="5 * * * *")
@blueprint.task(queueing_lock="cleanup_expired_vector_stores", queue="cron:cleanup")
@inject
async def cleanup_expired_context_resources(timestamp: int, context: ContextService) -> None:
    """Delete resources of contexts that haven't been used for several days."""
    deleted_stats = await context.expire_resources()
    logger.info(f"Deleted: {deleted_stats}")


@blueprint.periodic(cron="*/10 * * * *")
@blueprint.task(queueing_lock="remove_old_jobs", queue="cron:cleanup", pass_context=True)
async def remove_old_jobs(context: JobContext, timestamp: int):
    return await builtin_tasks.remove_old_jobs(
        context,
        max_hours=1,
        remove_failed=True,
        remove_cancelled=True,
        remove_aborted=True,
    )


@blueprint.periodic(cron="*/2 * * * *")
@blueprint.task(queueing_lock="remove_expired_passcodes", queue="cron:cleanup")
@inject
async def remove_expired_passcodes(configuration: Configuration, uow: IUnitOfWorkFactory, timestamp: int) -> None:
    async with uow() as uow:
        deleted_count = await uow.tokens.delete_expired()
        await uow.commit()
    logger.info(f"Deleted {deleted_count} expired passcodes")
