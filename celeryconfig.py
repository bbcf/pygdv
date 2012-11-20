CELERY_IMPORTS = ('pygdv.worker.tasks',)

# Result storage settings
CELERY_RESULT_BACKEND = 'database'
CELERY_RESULT_DBURI = 'postgresql://localhost:5432/gdv'

# Transport URL
BROKER_URL = 'sqla+sqlite:///celery-transport.sqlite'


