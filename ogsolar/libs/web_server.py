'''
Created on 6 Oct 2021

@author: pja
'''
import asyncio
from threading import Thread
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application

import tornado.web as web

PUBLIC_ROOT = '/www'

class MainHandler(RequestHandler):
    def get(self):
        self.render('index.html')

handlers = [
  (r'/', MainHandler),
  (r'/(.*)', web.StaticFileHandler, {'path': PUBLIC_ROOT}),
]

settings = dict(
  debug=True,
  static_path=PUBLIC_ROOT,
  template_path=PUBLIC_ROOT
)

application = web.Application(handlers, **settings)

class WebServer(Thread):
    """@brief a web server to show the ogsolar status."""
    
    def setPort(self, port):
        """@brief Set the server port to use.
           @param port The TCP port to use."""
        self._port = port
    
    def setUIO(self, uio):
        """@brief Set a UIO instance to use to send messages to the user.
           @param uio A UIO instance."""
        self._uio = uio
    
    def run(self):
        """@brief Start a web server."""
        try:
            self._uio.info("Starting web server.") 
            asyncio.set_event_loop(asyncio.new_event_loop())
            application = Application(handlers, **settings)
            application.listen(self._port)
            IOLoop.instance().start()
        except Exception as ex:
            self._uio.error( "Web server failed: {}".format( str(ex) ) )
            
        
