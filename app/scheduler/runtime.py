from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler


class SchedulerRuntime:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    def health(self) -> dict:
        jobs = self.scheduler.get_jobs()
        return {
            "running": self.scheduler.running,
            "job_count": len(jobs),
            "jobs": [j.id for j in jobs],
        }


scheduler_runtime = SchedulerRuntime()
