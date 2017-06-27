
from __future__ import absolute_import, unicode_literals
from .models import KeyValue
from adsputils import ADSCelery



class ADSImportPipelineCelery(ADSCelery):
    
    def example_call(self, key, value):
        with self.session_scope() as session:
            r = session.query(KeyValue).filter_by(key=key).first()
            if r is None:
                r = KeyValue(key=key)
                session.add(r)
            r.value = value
            session.commit()
            return r.toJSON()
