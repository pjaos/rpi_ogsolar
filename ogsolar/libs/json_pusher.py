#!/usr/bin/env python
           
from p3lib.json_networking import JSONServer, JsonServerHandler

import  threading

class JsonPusherServerHandler (JsonServerHandler):
    """@brief The handler for clients that wish to receive (pushed) json status updates."""

    def handle(self):

        try:
            try:

                self.connectedClientListLock.acquire()
                self.connectedClientList.append(self)
                self.connectedClientListLock.release()

                #As we don't receive anything from this push server
                #just wait around to exit
                self.serverActive = True

                while self.serverActive:

                    rxDict = JsonServerHandler.RX(self.request)
                    if not rxDict:
                        break

            finally:

                self.connectedClientListLock.acquire()
                self.connectedClientList.remove(self)
                self.connectedClientListLock.release()
                self.serverActive = False

        except:

            if self.request:
                self.request.close()

    def txJsonDict(self, jsonDict):
        """@brief Send the jsonDict to this dest client
           @param jsonDict The python dict (JSON data) to be sent to the client."""

        try:
            JsonServerHandler.TX(self.request, jsonDict)
        except:
            #If unable to send then close the connection to the client
            self.request.close()
            self.serverActive = False
       
        
class JsonPusher(object):
    """@brief Responsible for receiving status messages from the ogsolar controller and sending them to any connected clients."""
    
    JSON_PUSHER_SERVER_PORT = 8090

    def __init__(self, uio, options, jsonPusherConduit):
        """@brief Constructor
           @param uo A UserOutput instance.
           @param options Command line options from OptionParser
           @param jsonPusherConduit JsonPusherConduit instance"""
        self._uio                       = uio
        self._options                   = options
        self._jsonPusherConduit         = jsonPusherConduit
        self._connectedClientList       = []
        self._connectedClientListLock   = threading.Lock()
        
    def _sendToAllClients(self, statusDict):
        """@brief Send the status dict to all connected clients."""
        try:
            self._connectedClientListLock.acquire()
            
            for client in self._connectedClientList:
                client.txJsonDict(statusDict)
                
        finally:
            self._connectedClientListLock.release()
                
    def run(self):
        """@brief Called to start the JSON pusher running."""
        
        class SubHander (JsonPusherServerHandler):
            #can be referenced inside handle() using self.uo
            connectedClientList = self._connectedClientList
            connectedClientListLock = self._connectedClientListLock
        
        self.jsonPusherServerServer = JSONServer(('0.0.0.0', JsonPusher.JSON_PUSHER_SERVER_PORT), SubHander)
        self._srcServerThread = threading.Thread(target=self.jsonPusherServerServer.serve_forever)
        self._srcServerThread.setDaemon(True)
        self._srcServerThread.start()

        while True:
            #Wait for messages to be sent from the controller (blocking).
            statusDict = self._jsonPusherConduit.getB()
            
            self._sendToAllClients(statusDict)
            
        