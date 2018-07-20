import sys
import logging
logging.basicConfig(stream=sys.stderr)
if sys.version_info[0] < 3:
    raise Exception("Python3 required! Current (wrong) version: '%s'" % sys.version_info)

sys.path.insert(0, './3gm')
import app as application
