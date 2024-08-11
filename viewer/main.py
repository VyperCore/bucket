

import js;
js._py_readings = getattr(js, '._py', [])

from bucket.rw import SQLAccessor

readings = SQLAccessor.File('./example_file_store.db').read_all()

for reading in readings:
    js._py_readings.append(reading)

js.document.dispatchEvent(js.PyReadyEvent)
