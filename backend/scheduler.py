"""
Background scheduler for automatic package tracking updates

Uses APScheduler to periodically refresh all active packages
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import json
import logging

from database import SessionLocal
import crud
from trackers.kr_adapter import track_kr
from trackers.global_scraper import track_global
from notifications import notify_status_change, notify_delivery_complete, notify_error

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def refresh_all_packages():
    """
    Refresh tracking status for all active packages
    Detects status changes and sends notifications
    """
    logger.info(f"[{datetime.now()}] Starting scheduled package refresh")

    db = SessionLocal()
    try:
        packages = crud.get_packages(db, active_only=True, limit=1000)
        logger.info(f"Found {len(packages)} active packages to refresh")

        success_count = 0
        error_count = 0

        for package in packages:
            try:
                old_status = package.status

                # Track package
                if package.carrier.startswith("kr."):
                    result = track_kr(package.carrier, package.tracking_number)
                elif package.carrier.startswith("global."):
                    result = track_global(package.carrier, package.tracking_number)
                else:
                    logger.warning(f"Unknown carrier prefix: {package.carrier}")
                    continue

                if result.get("success"):
                    new_status = result.get("status", "Unknown")

                    # Update database
                    crud.update_package_status(
                        db,
                        package.tracking_number,
                        new_status,
                        json.dumps(result)
                    )

                    # Check if status changed
                    if old_status and old_status != new_status and package.notify_enabled:
                        logger.info(f"Status changed for {package.tracking_number}: {old_status} -> {new_status}")

                        # Check if delivered
                        if "delivered" in new_status.lower() or "배달완료" in new_status:
                            notify_delivery_complete(
                                package.tracking_number,
                                package.carrier,
                                package.alias
                            )
                        else:
                            notify_status_change(
                                package.tracking_number,
                                package.carrier,
                                old_status,
                                new_status,
                                package.alias
                            )

                    success_count += 1
                else:
                    error_count += 1
                    error_msg = result.get("error", "Unknown error")
                    logger.error(f"Failed to track {package.tracking_number}: {error_msg}")

                    if package.notify_enabled:
                        notify_error(
                            package.tracking_number,
                            package.carrier,
                            error_msg,
                            package.alias
                        )

            except Exception as e:
                error_count += 1
                logger.error(f"Error tracking {package.tracking_number}: {str(e)}")

        logger.info(f"Refresh complete: {success_count} success, {error_count} errors")

    except Exception as e:
        logger.error(f"Error in refresh_all_packages: {str(e)}")
    finally:
        db.close()

def start_scheduler(interval_hours: int = 1):
    """
    Start the background scheduler

    Args:
        interval_hours: How often to refresh packages (default: 1 hour)
    """
    if not scheduler.running:
        scheduler.add_job(
            refresh_all_packages,
            trigger=IntervalTrigger(hours=interval_hours),
            id="refresh_packages",
            name="Refresh all package tracking statuses",
            replace_existing=True
        )
        scheduler.start()
        logger.info(f"Scheduler started - refreshing every {interval_hours} hour(s)")

def stop_scheduler():
    """Stop the background scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")

def get_scheduler_status():
    """Get current scheduler status"""
    jobs = scheduler.get_jobs()
    return {
        "running": scheduler.running,
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None
            }
            for job in jobs
        ]
    }
