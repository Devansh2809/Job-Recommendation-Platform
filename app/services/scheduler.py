"""
Background tasks scheduler for job cleanup.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.db.session import AsyncSessionLocal
from app.db.crud import cleanup_expired_jobs


scheduler = AsyncIOScheduler()


async def cleanup_job():
    """Scheduled task to cleanup expired jobs"""
    async with AsyncSessionLocal() as db:
        try:
            deleted_count = await cleanup_expired_jobs(db)
            if deleted_count > 0:
                print(f"[SCHEDULER] Cleaned up {deleted_count} expired jobs")
        except Exception as e:
            print(f"[SCHEDULER] Error during cleanup: {e}")


def start_scheduler():
    """Start the background scheduler"""
    # Run cleanup every day at 2 AM
    scheduler.add_job(
        cleanup_job,
        trigger=CronTrigger(hour=2, minute=0),
        id="cleanup_expired_jobs",
        name="Cleanup expired job cache",
        replace_existing=True
    )
    
    scheduler.start()
    print(" Background scheduler started ")


def stop_scheduler():
    """Stop the scheduler"""
    scheduler.shutdown()
    print(" Background scheduler stopped")