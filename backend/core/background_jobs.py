"""
Background job processor for Redis queues.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .redis import dequeue_job, get_queue_length
from .config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class BackgroundJobProcessor:
    """Process background jobs from Redis queues."""
    
    def __init__(self):
        self.running = False
        self.processors = {
            "process_document": self._process_document,
            "send_notification": self._send_notification,
            "generate_report": self._generate_report,
            "update_analytics": self._update_analytics,
            "cleanup_old_data": self._cleanup_old_data
        }
    
    async def start(self):
        """Start the background job processor."""
        self.running = True
        logger.info("🚀 Starting background job processor...")
        
        while self.running:
            try:
                # Process jobs from the queue
                await self._process_queue("background_jobs")
                
                # Wait before checking again
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Background job processor error: {str(e)}")
                await asyncio.sleep(5)  # Wait longer on error
    
    async def stop(self):
        """Stop the background job processor."""
        self.running = False
        logger.info("🛑 Stopping background job processor...")
    
    async def _process_queue(self, queue_name: str):
        """Process jobs from a specific queue."""
        try:
            # Check if there are jobs in the queue
            queue_length = await get_queue_length(queue_name)
            if queue_length == 0:
                return
            
            # Dequeue and process a job
            job_data = await dequeue_job(queue_name)
            if job_data:
                await self._process_job(job_data)
                
        except Exception as e:
            logger.error(f"❌ Queue processing error for {queue_name}: {str(e)}")
    
    async def _process_job(self, job_data: Dict[str, Any]):
        """Process a single job."""
        try:
            job_type = job_data.get("type")
            data = job_data.get("data", {})
            
            logger.info(f"📋 Processing job: {job_type}")
            
            # Get the appropriate processor
            processor = self.processors.get(job_type)
            if processor:
                await processor(data)
                logger.info(f"✅ Job completed: {job_type}")
            else:
                logger.warning(f"⚠️ Unknown job type: {job_type}")
                
        except Exception as e:
            logger.error(f"❌ Job processing error: {str(e)}")
    
    async def _process_document(self, data: Dict[str, Any]):
        """Process document job."""
        document_id = data.get("document_id")
        case_id = data.get("case_id")
        
        logger.info(f"📄 Processing document {document_id} for case {case_id}")
        
        try:
            # Get document from database
            from ..data.database import get_db_session
            from ..data.repository import document_repository, audit_repository
            from ..data.schemas import AuditLogCreate
            from datetime import datetime
            
            async with get_db_session() as session:
                # Get document
                document = await document_repository.get_by_id(session, document_id)
                if not document:
                    logger.error(f"Document {document_id} not found")
                    return
                
                # Update processing status
                await document_repository.update(session, document_id, processing_status="processing")
                
                # Simulate text extraction (in real implementation, use OCR/text extraction)
                extracted_text = f"Extracted text from {document.original_filename}"
                
                # Simulate data extraction
                extracted_data = {
                    "document_type": document.document_type or "unknown",
                    "extracted_text_length": len(extracted_text),
                    "processing_timestamp": datetime.utcnow().isoformat()
                }
                
                # Update document with extracted data
                await document_repository.update(
                    session, 
                    document_id,
                    is_processed=True,
                    processing_status="completed",
                    extracted_text=extracted_text,
                    extracted_data=extracted_data,
                    processed_at=datetime.utcnow()
                )
                
                # Create audit log
                await audit_repository.create(session, AuditLogCreate(
                    action="document_processed",
                    resource_type="document",
                    resource_id=document_id,
                    user_id=None,  # System action
                    details={
                        "filename": document.original_filename,
                        "processing_status": "completed",
                        "extracted_data": extracted_data
                    }
                ))
                
                await session.commit()
                logger.info(f"✅ Document {document_id} processed successfully")
                
        except Exception as e:
            logger.error(f"❌ Document processing failed: {str(e)}")
            # Update document status to failed
            try:
                async with get_db_session() as session:
                    await document_repository.update(session, document_id, processing_status="failed")
                    await session.commit()
            except:
                pass
    
    async def _send_notification(self, data: Dict[str, Any]):
        """Send notification job."""
        user_id = data.get("user_id")
        message = data.get("message")
        notification_type = data.get("type", "info")
        
        logger.info(f"📧 Sending {notification_type} notification to user {user_id}: {message}")
        
        try:
            # Get user from database
            from ..data.database import get_db_session
            from ..data.repository import user_repository, audit_repository
            from ..data.schemas import AuditLogCreate
            from datetime import datetime
            
            async with get_db_session() as session:
                # Get user
                user = await user_repository.get_by_id(session, user_id)
                if not user:
                    logger.error(f"User {user_id} not found")
                    return
                
                # Simulate notification sending (in real implementation, send email/push)
                notification_data = {
                    "user_email": user.email,
                    "user_name": user.full_name,
                    "message": message,
                    "notification_type": notification_type,
                    "sent_at": datetime.utcnow().isoformat(),
                    "delivery_status": "sent"
                }
                
                # Create audit log for notification
                await audit_repository.create(session, AuditLogCreate(
                    action="notification_sent",
                    resource_type="notification",
                    resource_id=user_id,
                    user_id=user_id,
                    details=notification_data
                ))
                
                await session.commit()
                logger.info(f"✅ Notification sent to user {user_id}")
                
        except Exception as e:
            logger.error(f"❌ Notification sending failed: {str(e)}")
    
    async def _generate_report(self, data: Dict[str, Any]):
        """Generate report job."""
        report_type = data.get("report_type")
        date_range = data.get("date_range")
        user_id = data.get("user_id")
        
        logger.info(f"📊 Generating {report_type} report for {date_range}")
        
        # TODO: Implement report generation logic
        # - Query database for data
        # - Generate charts and analytics
        # - Create PDF/Excel report
        # - Send to user or store in file system
        
        await asyncio.sleep(5)  # Simulate report generation time
    
    async def _update_analytics(self, data: Dict[str, Any]):
        """Update analytics job."""
        case_id = data.get("case_id")
        action = data.get("action")
        
        logger.info(f"📈 Updating analytics for case {case_id}, action: {action}")
        
        try:
            # Get case from database
            from ..data.database import get_db_session
            from ..data.repository import case_repository, audit_repository
            from ..data.schemas import AuditLogCreate
            from datetime import datetime
            
            async with get_db_session() as session:
                # Get case
                case = await case_repository.get_by_id(session, case_id)
                if not case:
                    logger.error(f"Case {case_id} not found")
                    return
                
                # Calculate analytics metrics
                analytics_data = {
                    "case_id": case_id,
                    "action": action,
                    "timestamp": datetime.utcnow().isoformat(),
                    "metrics": {
                        "processing_time": 0.0,  # TODO: Calculate actual processing time
                        "sla_status": "on_track",  # TODO: Calculate actual SLA status
                        "risk_score": case.ai_risk_score or 0.0,
                        "confidence_score": case.ai_confidence_score or 0.0
                    }
                }
                
                # Create audit log for analytics update
                await audit_repository.create(session, AuditLogCreate(
                    action="analytics_updated",
                    resource_type="case",
                    resource_id=case_id,
                    user_id=None,  # System action
                    details=analytics_data
                ))
                
                await session.commit()
                logger.info(f"✅ Analytics updated for case {case_id}")
                
        except Exception as e:
            logger.error(f"❌ Analytics update failed: {str(e)}")
    
    async def _cleanup_old_data(self, data: Dict[str, Any]):
        """Cleanup old data job."""
        retention_days = data.get("retention_days", settings.audit_log_retention_days)
        
        logger.info(f"🧹 Cleaning up data older than {retention_days} days")
        
        try:
            from ..data.database import get_db_session
            from ..data.repository import audit_repository
            from ..data.schemas import AuditLogCreate
            from datetime import datetime, timedelta
            from sqlalchemy import delete
            from ..data.models import AuditLog
            
            async with get_db_session() as session:
                # Calculate cutoff date
                cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
                
                # Delete old audit logs
                result = await session.execute(
                    delete(AuditLog).where(AuditLog.created_at < cutoff_date)
                )
                deleted_logs = result.rowcount
                
                # Create audit log for cleanup
                await audit_repository.create(session, AuditLogCreate(
                    action="data_cleanup",
                    resource_type="system",
                    resource_id="cleanup",
                    user_id=None,  # System action
                    details={
                        "retention_days": retention_days,
                        "cutoff_date": cutoff_date.isoformat(),
                        "deleted_audit_logs": deleted_logs,
                        "cleanup_timestamp": datetime.utcnow().isoformat()
                    }
                ))
                
                await session.commit()
                logger.info(f"✅ Cleanup completed: deleted {deleted_logs} old audit logs")
                
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {str(e)}")


# Global background job processor instance
background_processor = BackgroundJobProcessor()


async def start_background_processor():
    """Start the background job processor."""
    await background_processor.start()


async def stop_background_processor():
    """Stop the background job processor."""
    await background_processor.stop()


async def enqueue_document_processing(document_id: str, priority: int = 0):
    """Enqueue a document processing job."""
    from .redis import enqueue_job
    
    await enqueue_job("background_jobs", {
        "type": "process_document",
        "document_id": document_id
    }, priority=priority)


async def enqueue_notification(user_id: str, message: str, notification_type: str = "info", priority: int = 0):
    """Enqueue a notification job."""
    from .redis import enqueue_job
    
    await enqueue_job("background_jobs", {
        "type": "send_notification",
        "user_id": user_id,
        "message": message,
        "type": notification_type
    }, priority=priority)


async def enqueue_report_generation(report_type: str, date_range: str, user_id: str, priority: int = 0):
    """Enqueue a report generation job."""
    from .redis import enqueue_job
    
    await enqueue_job("background_jobs", {
        "type": "generate_report",
        "report_type": report_type,
        "date_range": date_range,
        "user_id": user_id
    }, priority=priority)


async def enqueue_analytics_update(case_id: str, action: str, priority: int = 0):
    """Enqueue an analytics update job."""
    from .redis import enqueue_job
    
    await enqueue_job("background_jobs", {
        "type": "update_analytics",
        "case_id": case_id,
        "action": action
    }, priority=priority)


async def enqueue_cleanup(retention_days: Optional[int] = None, priority: int = 0):
    """Enqueue a cleanup job."""
    from .redis import enqueue_job
    
    await enqueue_job("background_jobs", {
        "type": "cleanup_old_data",
        "retention_days": retention_days or settings.audit_log_retention_days
    }, priority=priority)
