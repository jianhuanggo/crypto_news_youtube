"""
Module for scheduling the execution of the Crypto YouTube News Summarizer.
"""

import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Callable, Any, Dict, Optional

import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Scheduler:
    """Class for scheduling the execution of tasks."""
    
    def __init__(self, interval_hours: int = None):
        """
        Initialize the scheduler.
        
        Args:
            interval_hours: Interval in hours between executions. If None, uses the value from config.
        """
        self.interval_hours = interval_hours or config.SCHEDULE_INTERVAL
        self.running = False
        self.next_run = None
        self.thread = None
        
        logger.info(f"Scheduler initialized with interval: {self.interval_hours} hours")
    
    def start(self, task: Callable, *args, **kwargs) -> bool:
        """
        Start the scheduler.
        
        Args:
            task: Function to execute
            *args: Arguments to pass to the task
            **kwargs: Keyword arguments to pass to the task
            
        Returns:
            True if the scheduler was started successfully, False otherwise
        """
        if self.running:
            logger.warning("Scheduler is already running")
            return False
        
        self.running = True
        self.next_run = datetime.now()
        
        self.thread = threading.Thread(
            target=self._run_scheduler,
            args=(task, args, kwargs),
            daemon=True
        )
        self.thread.start()
        
        logger.info("Scheduler started")
        return True
    
    def stop(self) -> bool:
        """
        Stop the scheduler.
        
        Returns:
            True if the scheduler was stopped successfully, False otherwise
        """
        if not self.running:
            logger.warning("Scheduler is not running")
            return False
        
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
        
        logger.info("Scheduler stopped")
        return True
    
    def _run_scheduler(self, task: Callable, args: tuple, kwargs: Dict[str, Any]) -> None:
        """
        Run the scheduler.
        
        Args:
            task: Function to execute
            args: Arguments to pass to the task
            kwargs: Keyword arguments to pass to the task
        """
        logger.info(f"Scheduler thread started, next run at: {self.next_run}")
        
        self._execute_task(task, args, kwargs)
        
        self.next_run = datetime.now() + timedelta(hours=self.interval_hours)
        
        while self.running:
            now = datetime.now()
            
            if now >= self.next_run:
                self._execute_task(task, args, kwargs)
                
                self.next_run = now + timedelta(hours=self.interval_hours)
                
                logger.info(f"Next run scheduled for: {self.next_run}")
            
            time.sleep(60)  # Check every minute
    
    def _execute_task(self, task: Callable, args: tuple, kwargs: Dict[str, Any]) -> None:
        """
        Execute the task.
        
        Args:
            task: Function to execute
            args: Arguments to pass to the task
            kwargs: Keyword arguments to pass to the task
        """
        try:
            logger.info(f"Executing scheduled task: {task.__name__}")
            task(*args, **kwargs)
            logger.info(f"Scheduled task completed: {task.__name__}")
        except Exception as e:
            logger.error(f"Error executing scheduled task: {e}", exc_info=True)
    
    def get_next_run(self) -> Optional[datetime]:
        """
        Get the next run time.
        
        Returns:
            Next run time or None if the scheduler is not running
        """
        if not self.running:
            return None
        
        return self.next_run
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the scheduler.
        
        Returns:
            Dictionary containing the status of the scheduler
        """
        return {
            'running': self.running,
            'interval_hours': self.interval_hours,
            'next_run': self.next_run.strftime("%Y-%m-%d %H:%M:%S") if self.next_run else None
        }
