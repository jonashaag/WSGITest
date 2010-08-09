import os
import sys
from wsgitest.utils import import_file
from wsgitest import config

app_file, app_name = sys.argv[1:3]
app_module = import_file(app_file)
app = getattr(app_module, app_name)

config.run_server(app)
