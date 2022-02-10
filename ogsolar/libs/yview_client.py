#!/usr/bin/env python

import  socket
from    time import sleep, time
from    threading import Thread, Lock
from    p3lib.netif import NetIF
import  json

class AYTListener(object):
    """@brief Responsible listening for are you there messages from the host and sending responses
              back."""
    AYT_POLL_SECONDS         = 5
    UDP_DEV_DISCOVERY_PORT   = 2934
    UDP_RX_BUFFER_SIZE       = 2048
    ARE_YOU_THERE_STRING     = "-!#8[dkG^v's!dRznE}6}8sP9}QoIR#?O&pg)Qra"
    WEB_SERVER_PORT          = 8080
    
    @staticmethod
    def IsAYTMsg(msg, exepectedAYTString):
        """@brief Check if the AYT message contains the string.
           @return True if the message matches the AYT string."""
        aytMsg = False
        try:
            aDict = json.loads(msg)
            if "AYT" in aDict:
                aytString = aDict["AYT"]
                if aytString == exepectedAYTString:
                    aytMsg = True
        except:
            pass
        return aytMsg
    
    def __init__(self, uo, options, idDict):
        """@Constructor
            @param uo A UserOutput instance.
            @param options Command line options from OptionParser
            @param idDict A dictionary containing key=value pairs for each parameter for this device."""
        self._uio=uo
        self._options=options
        self._sock=None

        self._yviewClientLock = Lock()
        self._yviewDict = {}
        self._netIF = NetIF()
        
        # Open UDP socket to be used for discovering devices
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._sock.bind(('', AYTListener.UDP_DEV_DISCOVERY_PORT))
        
        self.initAYTTime()

        self._ipAddress = ""

    def _listener(self):
        """@brief Listen for messages from the icons dest server.
           @return The message received."""
        while True:
            try:
                self._uio.info("Listening on UDP port %d" % (AYTListener.UDP_DEV_DISCOVERY_PORT))
                rxData, addressPort = self._sock.recvfrom(AYTListener.UDP_RX_BUFFER_SIZE)
                rxData=rxData.decode()
                
                if len(addressPort) > 0:
                    self._uio.enableSyslog(True, host=addressPort[0])
                
                # Get the name of the interface on which we received the rxData
                ifName = self._netIF.getIFName(addressPort[0])
                self._ipAddress = self._netIF.getIFIPAddress(ifName)

                # If this was an AYT message
                if AYTListener.IsAYTMsg(rxData, AYTListener.ARE_YOU_THERE_STRING):
                    self._lastAYTMsgTime = time()
                    try:
                        self._yviewClientLock.acquire()

                        # Add the interface address on this machine as the source of the message for yview
                        self._yviewDict["IP_ADDRESS"] = self._ipAddress
                        self._yviewDict["UNIT_NAME"] = self._yviewDict["IP_ADDRESS"]
                        self._yviewDict["PRODUCT_ID"] = "OGSOLAR"
                        self._yviewDict["SERVICE_LIST"] = "SSH:22,WEB:{}".format(AYTListener.WEB_SERVER_PORT)
                        yviewDictStr = json.dumps(self._yviewDict, sort_keys=True, indent=4, separators=(',', ': '))

                        if self._options.debug:
                            self._uio.debug("%s: %s" % (self.__class__.__name__, yviewDictStr))

                        self._sock.sendto(yviewDictStr.encode(), addressPort)
                    finally:
                        self._yviewClientLock.release()

            except:
                self._uio.errorException()

            sleep(AYTListener.AYT_POLL_SECONDS)

            secondsSinceAYTMsg = self.getSecsSinceAYTMsg()

            self._uio.info("Seconds since last AYT reception: %d" % (secondsSinceAYTMsg))

    def run(self):
        """@brief Called to start sending UDP broadcast (beacon) messages."""

        try:
            self._listener()

        finally:
            self.shutDown()

    def getIPAddress(self):
        """@return The IP address of the unit. Normally assigned via DHCP."""
        return self._ipAddress

    def shutDown(self):
        """@brief Shutdown the network connection if connected."""
        if self._sock:
            self._sock.close()
            
    def setDict(self, yviewDict):
        """@brief set the dict (data) to be sent to the yview network."""
        try:
            self._yviewClientLock.acquire()
            self._yviewDict = yviewDict
        finally:
            self._yviewClientLock.release()
        
    def getSecsSinceAYTMsg(self):
        """@brief Get the number of seconds since we last received an Are You There Message."""
        try:
            self._yviewClientLock.acquire()
            seconds = time()-self._lastAYTMsgTime
        finally:
            self._yviewClientLock.release()
        return seconds
    
    def initAYTTime(self):
        """@brief Init the AYT message received time to now."""
        try:
            self._yviewClientLock.acquire()
            self._lastAYTMsgTime=time()
        finally:
            self._yviewClientLock.release()

class YViewClient(object):
    """@brief Responsible for.
              - Listening for are you there messages from an icons_dest server.
                    If we hear this message then we send a JSON message (unicast UDP) back to the server
                    so that it can identify us.
              - Read dicts from the yView conduit and pass to the ayt thread to be forwarded to the icons_dest server."""

    SPINLOCK_PAUSE_SECONDS         = 1

    @staticmethod
    def RunThread(uio, method):
        """@brief Responsible for running a thread method and if it stops then report any exceptions."""
        try:
            
            method()
            
        except:
            
            #Report the error so that it can be seen via syslog
            uio.errorException()
            
        uio.error("%s method exited." % ( str(method) ) )

    def __init__(self, uio, options, appConfig, yViewConduit):
        """@brief Constructor
           @param uo A UserOutput instance.
           @param options Command line options from OptionParser
           @param appConfig AppConfig instance"""
        self._uio           =   uio
        self._options       =   options
        self._appConfig     =   appConfig
        self._yViewConduit  =   yViewConduit
        
        self._aytListener = None

    def run(self):
        """@brief Called to start the client running."""

        self._aytListener = AYTListener(self._uio, self._options, {})
        
        aytServerThread = Thread(target=YViewClient.RunThread, args=(self._uio, self._aytListener.run,) )
        aytServerThread.setDaemon(True)
        aytServerThread.start()
        
        while True:

            try:
                if self._yViewConduit.bReadAvailable():

                    rxDict = self._yViewConduit.getB()

                    if rxDict:
                        self._aytListener.setDict(rxDict)

                else:
                    sleep(AYTListener.AYT_POLL_SECONDS)

                ipAddress = self._aytListener.getIPAddress()

                if ipAddress and len(ipAddress) > 0:
                    yViewStatusDict = {}
                    yViewStatusDict ["IP_ADDRESS"] = ipAddress
                    self._yViewConduit.putB(yViewStatusDict)

            except:
                self._uio.errorException()
                sleep(YViewClient.SPINLOCK_PAUSE_SECONDS)

    def shutDown(self):
        """@brief Shutdown the client"""
        if self._aytListener:
            self._aytListener.shutDown()
