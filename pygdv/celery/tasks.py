from celery.task import task

@task()
def add(x, y):
    x = int(x)
    y = int(y)
    result = x+y
    return result

@task()
def callback():
    print 'task ended '


