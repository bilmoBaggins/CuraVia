from functools import wraps
from database import SessionLocal
from models_db import BackgroundJobs

def log_background_job(title: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # If first arg is a Celery task (bound), skip it
            maybe_self = args[0] if len(args) > 0 else None
            if hasattr(maybe_self, "request"):
                # it's a bound Celery task
                args = args[1:]

            session = SessionLocal()
            job_id = kwargs.pop("job_id", None)
            job = None

            if job_id:
                job = session.query(BackgroundJobs).filter_by(id=job_id).first()
                if job:
                    job.status = "running"
                    session.commit()

            try:
                result = func(*args, **kwargs)
                if job:
                    job.status = "success"
                    session.commit()
                return result
            except Exception as e:
                if job:
                    job.status = "failed"
                    job.error = str(e)
                    session.commit()
                raise
            finally:
                session.close()

        return wrapper
    return decorator
