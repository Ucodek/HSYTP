"""
Scheduler module for periodic background jobs.

Provides a simple wrapper around APScheduler's AsyncIOScheduler with logging and error handling.
Use this to schedule, start, stop, and manage background jobs in the application.
"""
from functools import wraps
from typing import Callable, List, Optional

from apscheduler.job import Job
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastcore.logging.manager import ensure_logger

# Configure logger
logger = ensure_logger(None, __name__)


def log_exceptions(method):
    """
    Decorator to log exceptions in Scheduler methods.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except Exception as e:
            logger.error(f"{method.__name__} failed: {str(e)}")
            raise

    return wrapper


class Scheduler:
    """
    Simple wrapper for APScheduler's AsyncIOScheduler with logging and error handling.
    Provides methods to start, shutdown, add, remove, and list jobs.
    """

    def __init__(self, db_url: str) -> None:
        """
        Initialize the Scheduler. Scheduler is not started until start() is called.
        """
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.db_url = db_url

    def _ensure_started(self) -> None:
        """
        Ensure the scheduler is started. Raise RuntimeError if not.
        """
        if not self.scheduler:
            logger.error("Scheduler is not started.")
            raise RuntimeError("Scheduler is not started.")

    @log_exceptions
    def start(self) -> None:
        """
        Start the scheduler if it is not already running.
        Logs the action and handles errors.
        """
        if self.scheduler:
            logger.warning("Scheduler is already started.")
            return

        logger.info("Starting the scheduler")

        jobstores = {"default": SQLAlchemyJobStore(url=self.db_url)}

        self.scheduler = AsyncIOScheduler(jobstores=jobstores)
        self.scheduler.start()
        logger.info("Scheduler started successfully")

    @log_exceptions
    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the scheduler if it is running.
        Args:
            wait (bool): Whether to wait for running jobs to finish before shutting down.
        Logs the action and handles errors.
        """
        self._ensure_started()
        logger.info(f"Shutting down scheduler (wait={wait})")
        self.scheduler.shutdown(wait=wait)
        self.scheduler = None
        logger.info("Scheduler shut down successfully")

    @log_exceptions
    def add_job(
        self,
        # func: Callable,
        func: str,  # it is for db store "modulename:functionname"
        trigger: str,
        **kwargs,
    ) -> Job:
        """
        Add a job to the scheduler.

        Args:
            func (str): The function to be scheduled, as a string in 'module:function' format
                (e.g., 'myapp.jobs:my_job_func').
            trigger (str): The type of trigger for the job (e.g., 'interval', 'cron').
            **kwargs: Additional arguments for the job.

        Returns:
            Job: The scheduled job instance.

        Logs the action and handles errors.
        """

        self._ensure_started()

        # check if the job already exists
        if self.job_exists(kwargs.get("id")):
            logger.warning(
                f"Job with id '{kwargs.get('id')}' already exists. Skipping."
            )
            return self.scheduler.get_job(kwargs.get("id"))

        job = self.scheduler.add_job(func, trigger, **kwargs)
        logger.info(f"Added job '{job.id}' with trigger '{trigger}'")
        return job

    @log_exceptions
    def remove_job(self, job_id: str) -> None:
        """
        Remove a job from the scheduler.
        Args:
            job_id (str): The ID of the job to be removed.
        Logs the action and handles errors.
        """
        self._ensure_started()

        if not self.job_exists(job_id):
            logger.warning(f"Job with id '{job_id}' does not exist. Skipping.")
            return

        self.scheduler.remove_job(job_id)
        logger.info(f"Removed job '{job_id}'")

    @log_exceptions
    def get_jobs(self) -> List[Job]:
        """
        Retrieve all jobs from the scheduler.
        Returns:
            list: A list of scheduled jobs.
        Logs the action and handles errors.
        """
        self._ensure_started()
        jobs = self.scheduler.get_jobs()
        logger.debug(f"Retrieved {len(jobs)} jobs")
        return jobs

    @log_exceptions
    def job_exists(self, job_id: str) -> bool:
        """
        Check if a job with the given ID exists in the scheduler.
        Args:
            job_id (str): The ID of the job to check.
        Returns:
            bool: True if the job exists, False otherwise.
        """
        self._ensure_started()
        return self.scheduler.get_job(job_id) is not None

    @log_exceptions
    def update_job(self, job_id: str, **changes) -> Job:
        """
        Update an existing job's configuration.
        Args:
            job_id (str): The ID of the job to update.
            **changes: Fields to update (e.g., trigger, args, kwargs, etc.)
        Returns:
            Job: The updated job instance.
        Raises:
            RuntimeError: If scheduler is not started.
            ValueError: If the job does not exist.
        """
        self._ensure_started()
        if not self.job_exists(job_id):
            raise ValueError(f"Job with id '{job_id}' does not exist.")
        job = self.scheduler.modify_job(job_id, **changes)
        logger.info(f"Updated job '{job_id}' with changes: {changes}")
        return job

    @log_exceptions
    def add_listener(self, callback: Callable, mask: Optional[int] = None) -> None:
        """
        Add an event listener to the scheduler.
        Args:
            callback: The function to call on events.
            mask: APScheduler event mask (optional).
        """
        self._ensure_started()
        self.scheduler.add_listener(callback, mask)
