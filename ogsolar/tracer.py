#!/usr/bin/env python3.9

# An command line template using argparse as optparse is now deprecated.

import  os
import  sys
import  argparse
from    time import time

from    p3lib.uio import UIO, ConsoleMenu
from    p3lib.helper import logTraceBack

from    ogsolar.libs.tracer import EPSolarTracer

class TracerIF(object):
    """@brief Responsible for controlling the off grid solar system."""
    def __init__(self, serialPort):
        """@brief Constructor"""
        self._serialPort = serialPort


        
class EPSolarTracerIF(object):
        def __init__(self, uio, options):
            """@brief A user interface to an EPSolar Tracer MPPT controller.
               @param uio A UIO instance.
               @param options An argparse options interface.""" 
            self._uio = uio
            self._options = options
            self._tracerIF = EPSolarTracer(self._options.port)
            
        def readRegs(self):
            """@brief Read the Tracer regs and display them to the user."""
            self._tracerIF.connect()
            startT = time()
            self._tracerIF.readAllRegs()
            elapseSeconds = time()-startT
            self._tracerIF.disconnect()
            self._uio.info("Took {:.1f} seconds to read all registers.".format(elapseSeconds))
            self.showRegs()
            
        def showRegs(self):
            lines = self._tracerIF.getRegLines()
            for line in lines:
                self._uio.info(line)
                
        def saveRegs(self):
            """@brief Save the Tracer regs to a json file."""
            jsonFile = self._uio.getInput("Enter the name of the file to save")
            if not jsonFile.endswith(".json"):
                jsonFile = jsonFile + ".json"
                
            self._tracerIF.connect()
            startT = time()
            self._tracerIF.readAllRegs()
            elapseSeconds = time()-startT                        
            self._tracerIF.disconnect()
            self._uio.info("Took {:.1f} seconds to read all registers.".format(elapseSeconds))
            
            writeFile = True
            if os.path.isfile(jsonFile):
                writeFile = self._uio.getBoolInput("{} file exists. Overwrite ?".format(jsonFile))
            
            if writeFile:
                jsonStr = self._tracerIF.getJSON()
                fd = open(jsonFile, 'w')
                fd.write(jsonStr)
                fd.close()
            self._uio.info("Saved Tracer Registers to the {} file.".format(jsonFile))
                
        def loadRegs(self):
            """@brief Load the Tracer regs from a json file."""
            jsonFile = self._uio.getInput("Enter the name of the file to save")
            if not jsonFile.endswith(".json"):
                jsonFile = jsonFile + ".json"
                
            fd = open(jsonFile, 'r')
            jsonStr = fd.read()
            fd.close()

            self._tracerIF.setJSON(jsonStr)
            self.showRegs()
            self._uio.info("Loaded Tracer Registers to the {} file.".format(jsonFile))
            
        def regWrite(self):
            """@brief Write a register."""
            address = self._uio.getIntInput("Enter the register address (in hex) of the register to write", radix=16)
            if self._tracerIF.isValidAddress(address):
                try:
                    value = self._uio.getIntInput("Enter the register value (in decimal)", radix=10)
                    self._tracerIF.connect()
                    self._tracerIF.readReg(address)
                    register = self._tracerIF.getRegister(address)
                    register.setValue(value)
                    self._tracerIF.writeRegList( (register,) )
                    self._uio.info("Set register {} to {}".format(address, value))
                finally:
                    self._tracerIF.disconnect()
            else:
                self._uio.error("{} is not a valid Tracer register address.".format(address))
            
        def regRead(self):
            """@brief Read a single register value."""
            address = self._uio.getIntInput("Enter the address (in hex) of the register to read", radix=16)
            try:
                self._tracerIF.connect()
                self._tracerIF.readReg(address)
                register = self._tracerIF.getRegister(address)
                lines = register.getLines()
                for line in lines:
                    self._uio.info(line)

            finally:
                self._tracerIF.disconnect()
            
            
        def quit(self):
            """@brief Exit the program."""
            sys.exit(0)
            
def main():
    """@brief Program entry point"""
    uio = UIO()

    try:
        parser = argparse.ArgumentParser(description="Responsible for access to read and write EPSolar Tracer registers.\n"\
                                                     "via the modbus interface over the RS485 serial interface.\n"\
                                                     "The Raspberry PI must have a USB RS485 adpator connected to a USB port.",
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-d", "--debug",  help="Enable debugging.", action='store_true')
        parser.add_argument("-p", "--port",   help="The USB port (default=/dev/ttyUSB0).", default="/dev/ttyUSB0")
        
        options = parser.parse_args()

        uio.enableDebug(options.debug)

        tracerUIF = EPSolarTracerIF(uio, options)
                
        consoleMenu = ConsoleMenu(uio)
        consoleMenu.add("Read all registers", tracerUIF.readRegs)
        consoleMenu.add("Save registers to JSON file.", tracerUIF.saveRegs)
        consoleMenu.add("Load registers from a JSON file.", tracerUIF.loadRegs)
        consoleMenu.add("Save registers to JSON file.", tracerUIF.saveRegs)
        consoleMenu.add("Register read.", tracerUIF.regRead)
        consoleMenu.add("Register write.", tracerUIF.regWrite)
        consoleMenu.add("Quit", tracerUIF.quit)
        consoleMenu.show(showSelectedOption=True)
        


    #If the program throws a system exit exception
    except SystemExit:
        pass
    #Don't print error information if CTRL C pressed
    except KeyboardInterrupt:
        pass
    except Exception as ex:
        logTraceBack(uio)

        if options.debug:
            raise
        else:
            uio.error(str(ex))

if __name__== '__main__':
    main()
