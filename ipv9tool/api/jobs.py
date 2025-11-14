"""
Background Job Manager

Manages long-running background tasks for the API.
"""

import uuid
import logging
from typing import Dict, Optional, List, Any
from datetime import datetime
from threading import Lock

logger = logging.getLogger(__name__)


class JobManager:
    """Manages background jobs"""

    def __init__(self):
        """Initialize job manager"""
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.lock = Lock()
        logger.info("Job manager initialized")

    def create_job(self, job_type: str, metadata: Optional[Dict] = None) -> str:
        """
        Create a new job

        Args:
            job_type: Type of job
            metadata: Optional job metadata

        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())

        with self.lock:
            self.jobs[job_id] = {
                'job_id': job_id,
                'type': job_type,
                'status': 'pending',
                'progress': 0.0,
                'created_at': datetime.utcnow(),
                'started_at': None,
                'completed_at': None,
                'result': None,
                'error': None,
                'metadata': metadata or {}
            }

        logger.info(f"Created job {job_id} (type: {job_type})")
        return job_id

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job by ID

        Args:
            job_id: Job ID

        Returns:
            Job data or None if not found
        """
        with self.lock:
            return self.jobs.get(job_id)

    def update_job(self, job_id: str, **kwargs):
        """
        Update job fields

        Args:
            job_id: Job ID
            **kwargs: Fields to update
        """
        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id].update(kwargs)
                logger.debug(f"Updated job {job_id}: {kwargs}")

    def list_jobs(self, status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List jobs

        Args:
            status: Filter by status
            limit: Maximum number of jobs to return

        Returns:
            List of jobs
        """
        with self.lock:
            jobs = list(self.jobs.values())

            if status:
                jobs = [j for j in jobs if j['status'] == status]

            # Sort by created_at desc
            jobs.sort(key=lambda x: x['created_at'], reverse=True)

            return jobs[:limit]

    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job

        Args:
            job_id: Job ID

        Returns:
            True if deleted, False if not found
        """
        with self.lock:
            if job_id in self.jobs:
                del self.jobs[job_id]
                logger.info(f"Deleted job {job_id}")
                return True
            return False

    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """
        Clean up old completed jobs

        Args:
            max_age_hours: Maximum age in hours
        """
        now = datetime.utcnow()
        max_age = max_age_hours * 3600

        with self.lock:
            to_delete = []

            for job_id, job in self.jobs.items():
                if job['status'] in ['completed', 'failed']:
                    age = (now - job['created_at']).total_seconds()
                    if age > max_age:
                        to_delete.append(job_id)

            for job_id in to_delete:
                del self.jobs[job_id]

            if to_delete:
                logger.info(f"Cleaned up {len(to_delete)} old jobs")
