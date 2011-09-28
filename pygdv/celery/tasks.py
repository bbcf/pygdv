from celery.task import task

@task(serializer='json')
def add(x, y):
    x = int(x)
    y = int(y)
    result = x+y
    return result
    



