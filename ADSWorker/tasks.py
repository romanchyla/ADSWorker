
from __future__ import absolute_import, unicode_literals
from ADSWorker import app as app_module
from adsputils import get_date, exceptions
from ADSWorker.models import KeyValue
from kombu import Queue

# ============================= INITIALIZATION ==================================== #

app = app_module.ADSWorkerPipelineCelery('ADSWorker')
logger = app.logger


app.conf.CELERY_QUEUES = (
    Queue('errors', app.exchange, routing_key='errors', durable=False, message_ttl=24*3600*5),
    Queue('some-queue', app.exchange, routing_key='some-queue')
)


# ============================= TASKS ============================================= #

@app.task(queue='some-queue')
def task_hello_world(message):
    """
    Fetch a message from the queue. Save it into the database.
    And print out into a log.
    

    :param: message: contains the message inside the packet
        {
         'name': '.....',
         'start': 'ISO8801 formatted date (optional), indicates 
             the moment we checked the orcid-service'
        }
    :return: no return
    """
    
    if 'name' not in message:
        raise exceptions.IgnorableException('Received garbage: {}'.format(message))
    
    with app.session_scope() as session:
        kv = session.query(KeyValue).filter_by(key=message['name']).first()
        if kv is None:
            kv = KeyValue(key=message['name'])
        
        now = get_date()
        kv.value = now
        session.add(kv)
        session.commit()
        
        logger.info('Hello {key} we have recorded seeing you at {value}'.format(**kv.toJSON()))
        
        
    
    

if __name__ == '__main__':
    app.start()