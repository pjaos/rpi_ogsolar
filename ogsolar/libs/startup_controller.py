#!/usr/bin/env python

import sys
import traceback
from threading import Thread, active_count
from time import sleep, time
from subprocess import call

from p3lib.conduit import Conduit

from ogsolar.libs.ogsolar_controller import OGSolarController
from ogsolar.libs.epsolar_tracer import EPSolarTracerInterface
from ogsolar.libs.yview_client import YViewClient
from ogsolar.libs.httpjsontranslator import HttpJsonTranslator
from ogsolar.libs.json_pusher import JsonPusher
from ogsolar.libs.app_config import AppConfig
from ogsolar.libs.web_server import WebServer
from ogsolar.libs.yview_client import AYTListener
 
class StartupController(object):
    """@brief Responsible for starting all the threads that compose the ogsolar system."""
    
    MIN_RUNNING_THREAD_COUNT     = 8
    MAX_MEM_INCREASE_KB          = 10000
    REBOOT_CMD                   = "/sbin/reboot"
    CONDUIT_READ_TIMEOUT_SECONDS = 30

    @staticmethod
    def RunThread(uio, method):
        """@brief Responsible for running a thread method and if it stops then report any exceptions."""
        try:
            
            method()
            
        except:
            traceback.print_exc(file=sys.stdout)        
            #Report the error so that it can be seen via syslog
            uio.errorException()
            
        uio.error("%s method exited." % ( str(method) ) )
        
    def __init__(self, uio, options, appConfig):
        """@brief Constructor."""
        self._uio       = uio
        self._options   = options
        self._appConfig =   appConfig

    def run(self):
        
        conduitUIO = None
        if self._options.debug:
            conduitUIO = self._uio

        self._traceConduit = Conduit(uio=conduitUIO, cName="tracer", readBlockTimeoutSeconds=StartupController.CONDUIT_READ_TIMEOUT_SECONDS)
        self._epSolarTracerInterface = EPSolarTracerInterface(self._uio, self._options, self._appConfig, self._traceConduit)
        epSolarTracerReaderThread = Thread(target=StartupController.RunThread, args=(self._uio, self._epSolarTracerInterface.run,) )
        epSolarTracerReaderThread.setDaemon(True)
        epSolarTracerReaderThread.start()
        
        self._yViewConduit = Conduit(uio=conduitUIO, cName="yView", readBlockTimeoutSeconds=StartupController.CONDUIT_READ_TIMEOUT_SECONDS)
        self._yViewClient = YViewClient(self._uio, self._options, self._appConfig, self._yViewConduit)
        yViewClientThread = Thread(target=StartupController.RunThread, args=(self._uio, self._yViewClient.run,) )
        yViewClientThread.setDaemon(True)
        yViewClientThread.start()
        
        self._webConduit = Conduit(uio=conduitUIO, cName="web", readBlockTimeoutSeconds=StartupController.CONDUIT_READ_TIMEOUT_SECONDS)
        self._httpJsonTranslator = HttpJsonTranslator(self._uio, self._options, self._webConduit)
        httpJsonTranslatorThread = Thread(target=StartupController.RunThread, args=(self._uio, self._httpJsonTranslator.run,) )
        httpJsonTranslatorThread.setDaemon(True)
        httpJsonTranslatorThread.start()
        
        self._jsonPusherConduit = Conduit(uio=conduitUIO, cName="json", readBlockTimeoutSeconds=StartupController.CONDUIT_READ_TIMEOUT_SECONDS)
        self._jsonPusher = JsonPusher(self._uio, self._options, self._jsonPusherConduit)
        jsonPusherThread = Thread(target=StartupController.RunThread, args=(self._uio, self._jsonPusher.run,) )
        jsonPusherThread.setDaemon(True)
        jsonPusherThread.start()

        webServerThread = WebServer()
        webServerThread.setPort(AYTListener.WEB_SERVER_PORT)
        webServerThread.setUIO(self._uio)
        webServerThread.setDaemon(True)
        webServerThread.start()
        
        self._oGSolarController = OGSolarController(self._uio, self._options, self._appConfig, self._traceConduit, self._yViewConduit, self._webConduit, self._jsonPusherConduit)
        #This thread has to shutdown in a controlled fashion and so is not a daemon thread.
        oGSolarControllerThread = Thread(target=StartupController.RunThread, args=(self._uio, self._oGSolarController.run,) )
        #oGSolarControllerThread.setDaemon(True)
        oGSolarControllerThread.start()
        
        #Block here
        self._threadMonitor()

    def _shutDown(self):
        """@brief Shutdown the solar controller system."""
        rebootDelay = self._appConfig.getAttr(AppConfig.DELAY_BEFORE_ERROR_REBOOT)
        self._uio.info("Starting shutdown.")
        self._oGSolarController.shutDown()
        self._uio.info("SHUTDOWN:")
        if not self._options.no_reboot:
            self._uio.info("SHUTDOWN: rebooting in %d seconds." % (rebootDelay) )
            # Provide details on how long before restart, useful in syslog.
            rebootTime=time()+rebootDelay
            while time() < rebootTime:
                self._uio.warn("%d seconds before reboot." % (rebootTime-time()) )
                sleep(2)
            
            self._reboot()

    def _reboot(self):
        """@brief reboot the Linux platform."""
        self._uio.info("REBOOT: NOW !!!")
        call([StartupController.REBOOT_CMD])

    def _threadMonitor(self, pollSeconds=5):
        """@brief Monitor all running threads and if one stops exit the main thread. 
                  Exiting the main thread will shutdown all other threads as they are all daemon threads."""
        
        #Sleep to allow all threads to start
        sleep(pollSeconds)
        
        threadCount = active_count()
        self._uio.info("STARTUP: %d threads running" % (threadCount) )
        
        initialMemUsedKB = OGSolarController.GetMemUsage()
        try:
            
            try:
        
                while True:
                    
                    memUsedKb = OGSolarController.GetMemUsage()
                    memIncreaseKB = memUsedKb-initialMemUsedKB
                    threadCount = active_count()
                    self._uio.info("%d threads running (min=%d)." % (threadCount, StartupController.MIN_RUNNING_THREAD_COUNT) )
                    self._uio.info("Memory in use = %d kB, increase since startup = %d kB (max = %d kB)." % (memUsedKb, memIncreaseKB, self._options.max_mem_inc) )                    

                    ctrlErrMsg = self._oGSolarController.getErrorMessage()
                    if threadCount < StartupController.MIN_RUNNING_THREAD_COUNT:
                        self._uio.error("THREAD ERROR: Not all threads are running.")
                        break 
                        
                    elif memIncreaseKB > self._options.max_mem_inc:
                        self._uio.error("MEMORY ERROR: To much memory is now being used.")
                        break 
                    
                    elif ctrlErrMsg:
                        self._uio.error("OGSOLAR_CONTROLLER: %s" % (ctrlErrMsg) )
                        break
                        
                    else:
                        sleep(pollSeconds)
                
            
            except KeyboardInterrupt:
                self._uio.error("SHUTDOWN: User pressed CTRL C")
            
        finally:
            
            self._shutDown()

    