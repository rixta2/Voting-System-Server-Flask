from . import app, socketio
import logging
from .api.api import init_api

if __name__ == '__main__':
    if __debug__: 
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    socketio.run(app, host='0.0.0.0', port=7373, debug=True)
    init_api()