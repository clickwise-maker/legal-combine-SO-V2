import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class SchedulerStatus(str, Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ScrapeTask:
    """Represents a scraping task."""
    task_id: str
    name: str
    sources: List[str]
    trigger_type: str
    trigger_config: Dict
    status: TaskStatus = TaskStatus.PENDING
    last_run: Optional[datetime] = None
    last_status: Optional[str] = None
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    documents_scraped: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    next_run: Optional[datetime] = None


@dataclass
class ScrapeResult:
    """Result of a scraping run."""
    task_id: str
    task_name: str
    status: str
    sources_processed: int
    documents_found: int
    documents_saved: int
    errors: List[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0


class BaseTrigger(ABC):
    """Base class for trigger types."""

    @abstractmethod
    def get_trigger_config(self) -> Dict:
        """Get the trigger configuration."""
        pass


class WeeklyTrigger(BaseTrigger):
    """Weekly trigger configuration."""

    def __init__(
        self,
        day_of_week: str = "mon",
        hour: int = 2,
        minute: int = 0,
    ):
        self.day_of_week = day_of_week
        self.hour = hour
        self.minute = minute

    def get_trigger_config(self) -> Dict:
        return {
            "type": "cron",
            "day_of_week": self.day_of_week,
            "hour": self.hour,
            "minute": self.minute,
        }

    def to_apscheduler_trigger(self):
        day_map = {
            "mon": 0, "tue": 1, "wed": 2, "thu": 3,
            "fri": 4, "sat": 5, "sun": 6
        }
        return CronTrigger(
            day_of_week=day_map.get(self.day_of_week.lower(), 0),
            hour=self.hour,
            minute=self.minute,
        )


class DailyTrigger(BaseTrigger):
    """Daily trigger configuration."""

    def __init__(self, hour: int = 2, minute: int = 0):
        self.hour = hour
        self.minute = minute

    def get_trigger_config(self) -> Dict:
        return {
            "type": "cron",
            "hour": self.hour,
            "minute": self.minute,
        }

    def to_apscheduler_trigger(self):
        return CronTrigger(hour=self.hour, minute=self.minute)


class IntervalTriggerConfig(BaseTrigger):
    """Interval-based trigger configuration."""

    def __init__(self, hours: int = 0, minutes: int = 0, days: int = 0):
        self.hours = hours
        self.minutes = minutes
        self.days = days

    def get_trigger_config(self) -> Dict:
        return {
            "type": "interval",
            "hours": self.hours,
            "minutes": self.minutes,
            "days": self.days,
        }

    def to_apscheduler_trigger(self):
        return IntervalTrigger(
            days=self.days,
            hours=self.hours,
            minutes=self.minutes,
        )


class ScraperScheduler:
    """Scheduler for managing government scraper tasks."""

    def __init__(self):
        self._scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
        self._tasks: Dict[str, ScrapeTask] = {}
        self._results: List[ScrapeResult] = []
        self._status = SchedulerStatus.STOPPED
        self._on_complete_callbacks: List[Callable] = []
        self._max_results = 100

    @property
    def status(self) -> SchedulerStatus:
        return self._status

    @property
    def tasks(self) -> Dict[str, ScrapeTask]:
        return self._tasks.copy()

    @property
    def results(self) -> List[ScrapeResult]:
        return self._results.copy()

    def add_callback(self, callback: Callable[[ScrapeResult], None]):
        """Add a callback to be called when scraping completes."""
        self._on_complete_callbacks.append(callback)

    def _notify_callbacks(self, result: ScrapeResult):
        """Notify all registered callbacks of completion."""
        for callback in self._on_complete_callbacks:
            try:
                callback(result)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    async def _execute_task(self, task: ScrapeTask):
        """Execute a scraping task."""
        from ..tools.govt_scraper_tools import GovtScraperFactory
        import time

        task.status = TaskStatus.RUNNING
        task.total_runs += 1
        logger.info(f"Starting scrape task: {task.name}")

        result = ScrapeResult(
            task_id=task.task_id,
            task_name=task.name,
            status="running",
            sources_processed=len(task.sources),
        )

        start_time = time.time()
        total_docs_found = 0
        total_docs_saved = 0
        errors = []

        try:
            for source in task.sources:
                scraper = GovtScraperFactory.create_scraper(source)
                if not scraper:
                    errors.append(f"Unknown source: {source}")
                    continue

                try:
                    documents = await asyncio.get_event_loop().run_in_executor(
                        None, scraper.scrape
                    )
                    total_docs_found += len(documents)

                    saved_count = await asyncio.get_event_loop().run_in_executor(
                        None, scraper.save_to_database, documents
                    )
                    total_docs_saved += saved_count

                    logger.info(f"  {source}: {len(documents)} found, {saved_count} saved")

                except Exception as e:
                    error_msg = f"Error scraping {source}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)

            result.status = "completed"
            result.documents_found = total_docs_found
            result.documents_saved = total_docs_saved
            task.documents_scraped += total_docs_saved
            task.successful_runs += 1
            task.last_status = "success"

        except Exception as e:
            result.status = "failed"
            errors.append(f"Task execution failed: {str(e)}")
            task.failed_runs += 1
            task.last_status = "failed"
            logger.error(f"Task {task.name} failed: {e}")

        result.completed_at = datetime.utcnow()
        result.duration_seconds = time.time() - start_time
        result.errors = errors

        task.last_run = datetime.utcnow()
        task.status = TaskStatus.COMPLETED

        self._add_result(result)
        self._notify_callbacks(result)

        logger.info(
            f"Completed task {task.name}: "
            f"{total_docs_saved} saved in {result.duration_seconds:.2f}s"
        )

    def _add_result(self, result: ScrapeResult):
        """Add a result to the history."""
        self._results.insert(0, result)
        if len(self._results) > self._max_results:
            self._results = self._results[:self._max_results]

    def create_task(
        self,
        name: str,
        sources: List[str],
        trigger: BaseTrigger,
        task_id: Optional[str] = None,
    ) -> ScrapeTask:
        """Create a new scraping task."""
        import uuid

        task = ScrapeTask(
            task_id=task_id or str(uuid.uuid4()),
            name=name,
            sources=sources,
            trigger_type=trigger.get_trigger_config()["type"],
            trigger_config=trigger.get_trigger_config(),
        )

        self._tasks[task.task_id] = task
        logger.info(f"Created task: {task.name} (ID: {task.task_id})")

        return task

    def schedule_task(self, task: ScrapeTask):
        """Schedule a task with its trigger."""
        trigger = self._create_trigger(task.trigger_type, task.trigger_config)

        self._scheduler.add_job(
            func=self._execute_task,
            trigger=trigger,
            args=[task],
            id=task.task_id,
            name=task.name,
            replace_existing=True,
        )

        task.next_run = self._scheduler.get_job(task.task_id).next_run_time
        logger.info(f"Scheduled task: {task.name}, next run: {task.next_run}")

    def _create_trigger(self, trigger_type: str, config: Dict) -> BaseTrigger:
        """Create a trigger from configuration."""
        if trigger_type == "cron":
            return WeeklyTrigger(
                day_of_week=config.get("day_of_week", "mon"),
                hour=config.get("hour", 2),
                minute=config.get("minute", 0),
            )
        elif trigger_type == "interval":
            return IntervalTriggerConfig(
                days=config.get("days", 0),
                hours=config.get("hours", 0),
                minutes=config.get("minutes", 0),
            )
        else:
            return DailyTrigger(hour=2, minute=0)

    def remove_task(self, task_id: str) -> bool:
        """Remove a scheduled task."""
        if task_id in self._tasks:
            self._scheduler.remove_job(task_id)
            del self._tasks[task_id]
            logger.info(f"Removed task: {task_id}")
            return True
        return False

    def run_task_now(self, task_id: str):
        """Trigger a task to run immediately."""
        if task_id in self._tasks:
            task = self._tasks[task_id]
            asyncio.create_task(self._execute_task(task))
            logger.info(f"Triggered immediate run for task: {task.name}")

    def get_task_status(self, task_id: str) -> Optional[ScrapeTask]:
        """Get the status of a task."""
        return self._tasks.get(task_id)

    def get_task_results(
        self, task_id: Optional[str] = None, limit: int = 10
    ) -> List[ScrapeResult]:
        """Get results for a specific task or all tasks."""
        if task_id:
            return [r for r in self._results if r.task_id == task_id][:limit]
        return self._results[:limit]

    def start(self):
        """Start the scheduler."""
        if self._status != SchedulerStatus.RUNNING:
            self._scheduler.start()
            self._status = SchedulerStatus.RUNNING
            logger.info("Scraper scheduler started")

    def stop(self):
        """Stop the scheduler."""
        if self._status == SchedulerStatus.RUNNING:
            self._scheduler.shutdown(wait=False)
            self._status = SchedulerStatus.STOPPED
            logger.info("Scraper scheduler stopped")

    def pause(self):
        """Pause the scheduler."""
        if self._status == SchedulerStatus.RUNNING:
            self._scheduler.pause()
            self._status = SchedulerStatus.PAUSED
            logger.info("Scraper scheduler paused")

    def resume(self):
        """Resume the scheduler."""
        if self._status == SchedulerStatus.PAUSED:
            self._scheduler.resume()
            self._status = SchedulerStatus.RUNNING
            logger.info("Scraper scheduler resumed")

    def get_stats(self) -> Dict:
        """Get scheduler statistics."""
        return {
            "status": self._status.value,
            "total_tasks": len(self._tasks),
            "running_tasks": sum(1 for t in self._tasks.values() if t.status == TaskStatus.RUNNING),
            "total_runs": sum(t.total_runs for t in self._tasks.values()),
            "successful_runs": sum(t.successful_runs for t in self._tasks.values()),
            "failed_runs": sum(t.failed_runs for t in self._tasks.values()),
            "total_documents": sum(t.documents_scraped for t in self._tasks.values()),
            "recent_results_count": len(self._results),
        }


def create_default_schedule(scheduler: ScraperScheduler):
    """Create the default scraping schedule."""

    weekly_trigger = WeeklyTrigger(day_of_week="mon", hour=2, minute=0)
    scheduler.create_task(
        name="Weekly Full Scrape",
        sources=["gazette", "dgtr", "mca", "rbi", "sebi", "minlaw"],
        trigger=weekly_trigger,
        task_id="weekly_full_scrape",
    )

    daily_trigger = DailyTrigger(hour=6, minute=0)
    scheduler.create_task(
        name="Daily RBI/SEBI Updates",
        sources=["rbi", "sebi"],
        trigger=daily_trigger,
        task_id="daily_regulator_updates",
    )

    return scheduler


_singleton_scheduler: Optional[ScraperScheduler] = None


def get_scheduler() -> ScraperScheduler:
    """Get the singleton scheduler instance."""
    global _singleton_scheduler
    if _singleton_scheduler is None:
        _singleton_scheduler = ScraperScheduler()
    return _singleton_scheduler


async def start_scheduler():
    """Start the scheduler with default configuration."""
    scheduler = get_scheduler()

    if not scheduler.tasks:
        create_default_schedule(scheduler)

    for task in scheduler.tasks.values():
        scheduler.schedule_task(task)

    scheduler.start()

    return scheduler


async def stop_scheduler():
    """Stop the scheduler."""
    scheduler = get_scheduler()
    scheduler.stop()
