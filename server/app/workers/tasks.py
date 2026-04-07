"""
Background Tasks (Celery)
==========================
Long-running tasks that run in the background.
Will be implemented when Celery + Redis is set up.

LEARN: Why background tasks?
- AI document analysis can take 10-30 seconds
- You don't want the user waiting for the HTTP response
- Instead: return "processing" immediately, run AI in background
- Frontend polls for status updates
"""

# TODO: Setup Celery worker when needed
# For now, AI tasks run synchronously in the request
