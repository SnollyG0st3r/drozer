from logging import getLogger
from twisted.internet.protocol import Protocol

from drozer.server.files import FileProvider
from drozer.server.http import HTTP
from drozer.server.drozer_protocol import Drozer

class ProtocolSwitcher(Protocol):
    """
    ProtocolSwitcher is a virtual protocol that can differentiate between different
    protocols being spoken to the drozer Server.

    If the incoming message starts with GET or POST, the server will route the
    connection to an HTTP server, otherwise it is connected to the drozer
    Server.
    """

    enable_http = True
    protocol = None
    
    __file_provider = FileProvider()
    __logger = getLogger(__name__)
    
    def __init__(self):
        pass
    
    def __chooseProtocol(self, data):
        """
        Selects which protocol to be used, by inspecting the data.
        """

        if self.enable_http and data.startswith("GET") or data.startswith("POST"):
            return HTTP(self.__file_provider)
        else:
            return Drozer()
    
    def connectionMade(self):
        """
        When a connection is first established, no protocol is selected.
        """

        self.__logger.info("accepted incoming connection from " + str(self.transport.getPeer()))
        
        self.protocol = None
    
    def dataReceived(self, data):
        """
        When data is received, we try to select a protocol. Future messages are
        routed to the appropriate handler.
        """

        if self.protocol == None:
            protocol = self.__chooseProtocol(data)
            
            if protocol is not None:
                self.__logger.info("switching protocol to " + protocol.name + " for " + str(self.transport.getPeer()))
                
                self.protocol = protocol
                
                self.protocol.makeConnection(self.transport)
                self.protocol.dataReceived(data)
            else:
                self.__logger.error("unrecognised protocol from " + str(self.transport.getPeer()))
                
                self.transport.loseConnection()
        else:
            self.protocol.dataReceived(data)
            