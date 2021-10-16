'''
Created on 6 Oct 2021

@author: pja
'''

import os
import asyncio
import tempfile
import inspect

from pathlib import Path
from shutil import copytree

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
    
    WEB_ROOT_SRC = "www/html" #The folder in the ogsolar module containing the web root files
    
    @staticmethod
    def GetWebRootFolder():
        """@return The folder that holds the files served by the tornado web server."""
        #Get the system temp folder
        tempFolder = tempfile.gettempdir()
        return os.path.join(tempFolder, "ogsolar_webroot")
    
    @staticmethod
    def EnsureWebRootExists():
        """@brief The root folder used by the web server must exist before the web server is started.
                  The contents of this foler are copied from the www/html folder in the ogsolar 
                  site-packages folder. The ogsolar/www is installed when the package is installed."""
        webRoot = WebServer.GetWebRootFolder()
        # If the web root does not exist, create it.
        if not os.path.isdir(webRoot):
            thisFolder = Path(os.path.dirname(inspect.getfile(WebServer)))
            webRootSrc = os.path.join(thisFolder.parent.absolute(), WebServer.WEB_ROOT_SRC)
            if os.path.isdir(webRootSrc):
                # Copy installed web root files to the temp folder so that it is 
                # writable by this application.
                copytree(webRootSrc, webRoot)
            else:
                raise Exception("{} folder not found.".format(webRootSrc))
    
    def setPort(self, port):
        """@brief Set the server port to use.
           @param port The TCP port to use."""
        self._port = port
    
    def setUIO(self, uio):
        """@brief Set a UIO instance to use to send messages to the user.
           @param uio A UIO instance."""
        self._uio = uio
        
    def setWebRoot(self, webRoot):
        """@brief Set the web root folder.
           @param webRoot The web server root folder."""
        global PUBLIC_ROOT
        PUBLIC_ROOT = webRoot

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
            
        
