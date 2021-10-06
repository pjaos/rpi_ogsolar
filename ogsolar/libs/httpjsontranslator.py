#!/usr/bin/env python

import os
import json
from   ogsolar.libs.epsolar_tracer import EPSolarTracerInterface
from   ogsolar.libs.ogsolar_controller import OGSolarController

class HttpJsonTranslator(object):
    """@brief Responsible for providing a JSON file to be read by the web server."""

    TRACER_KWH_GEN_DAY           = "GENERATED KWH TODAY"
    TRACER_KWH_GEN_MONTH         = "GENERATED KWH THIS MONTH"
    TRACER_KWH_GEN_YEAR          = "GENERATED KWH THIS YEAR"
    TRACER_KWH_GEN               = "GENERATED KWH"

    def __init__(self, uio, options, webConduit):
        """@brief Constructor
           @param uo A UserOutput instance.
           @param options Command line options from OptionParser
           @param appConfig AppConfig instance"""
        self._uio           =   uio
        self._options       =   options
        self._webConduit    =   webConduit
        
        webRoot             = self._options.web_root
            
        try:
            if not os.path.isdir(webRoot):
                os.mkdir(webRoot)
        except:
            self._uio.errorException()
            raise
        
        self._table1File = os.path.join(webRoot, 'table1.json')
        self._table2File = os.path.join(webRoot, 'table2.json')

    def run(self):
        """@brief Called to start the client running."""
        while True:
            sysStatusDict = self._webConduit.getA()
            if sysStatusDict:

                table1Dict = {}            
    
                if EPSolarTracerInterface.TRACER_BAT_CHARGE_STATUS in sysStatusDict:
                    table1Dict[0]=[EPSolarTracerInterface.TRACER_BAT_CHARGE_STATUS, sysStatusDict[EPSolarTracerInterface.TRACER_BAT_CHARGE_STATUS] ]
                
                if EPSolarTracerInterface.TRACER_PV_VOLTS in sysStatusDict:
                    table1Dict[1]=[EPSolarTracerInterface.TRACER_PV_VOLTS, "%.2f" % (sysStatusDict[EPSolarTracerInterface.TRACER_PV_VOLTS]) ]
                    
                if EPSolarTracerInterface.TRACER_PV_AMPS in sysStatusDict:
                    table1Dict[2]=[EPSolarTracerInterface.TRACER_PV_AMPS, "%.2f" % (sysStatusDict[EPSolarTracerInterface.TRACER_PV_AMPS]) ]

                if EPSolarTracerInterface.TRACER_PV_WATTS in sysStatusDict:
                    table1Dict[3]=[EPSolarTracerInterface.TRACER_PV_WATTS, "%.0f" % (sysStatusDict[EPSolarTracerInterface.TRACER_PV_WATTS]) ]
                                        
                if EPSolarTracerInterface.TRACER_BAT_VOLTS in sysStatusDict:
                    table1Dict[4]=[EPSolarTracerInterface.TRACER_BAT_VOLTS, "%.2f" % (sysStatusDict[EPSolarTracerInterface.TRACER_BAT_VOLTS]) ]
                    
                if EPSolarTracerInterface.TRACER_BAT_AMPS in sysStatusDict:
                    table1Dict[5]=[EPSolarTracerInterface.TRACER_BAT_AMPS, "%.2f" % (sysStatusDict[EPSolarTracerInterface.TRACER_BAT_AMPS]) ]
                    
                if EPSolarTracerInterface.TRACER_BAT_WATTS in sysStatusDict:
                    table1Dict[6]=[EPSolarTracerInterface.TRACER_BAT_WATTS, "%.0f" % (sysStatusDict[EPSolarTracerInterface.TRACER_BAT_WATTS]) ]
                    
                if EPSolarTracerInterface.BAT_AMPS in sysStatusDict:
                    table1Dict[7]=[EPSolarTracerInterface.BAT_AMPS, "%.2f" % (sysStatusDict[EPSolarTracerInterface.BAT_AMPS]) ]
                
                if EPSolarTracerInterface.BAT_LOAD_WATTS in sysStatusDict:
                    table1Dict[8]=[EPSolarTracerInterface.BAT_LOAD_WATTS, "%.0f" % (sysStatusDict[EPSolarTracerInterface.BAT_LOAD_WATTS]) ]
                
                if EPSolarTracerInterface.BATTERY_TEMPERATURE in sysStatusDict:
                    table1Dict[9]=[EPSolarTracerInterface.BATTERY_TEMPERATURE, "%.1f" % (sysStatusDict[EPSolarTracerInterface.BATTERY_TEMPERATURE]) ]
                
                if EPSolarTracerInterface.CONTROLLER_TEMPERATURE in sysStatusDict:
                    #Changed the name of the key here until the web server database schema has been updated.
                    table1Dict[10]=["MPPT CONTROLLER TEMPERATURE", "%.1f" % (sysStatusDict[EPSolarTracerInterface.CONTROLLER_TEMPERATURE]) ]
                
                if OGSolarController.RPI_HEATSINK_TEMPERATURE in sysStatusDict:
                    table1Dict[11]=[OGSolarController.RPI_HEATSINK_TEMPERATURE, "%.1f" % (sysStatusDict[OGSolarController.RPI_HEATSINK_TEMPERATURE]) ]
                
                if OGSolarController.RPI_CPU_TEMPERATURE in sysStatusDict:
                    table1Dict[12]=[OGSolarController.RPI_CPU_TEMPERATURE, "%.1f" % (sysStatusDict[OGSolarController.RPI_CPU_TEMPERATURE]) ]
                
                table1StatusDictStr = json.dumps( table1Dict, sort_keys=True, indent=4, separators=(',', ': '))
                
                fd = open(self._table1File, 'w')
                fd.write(table1StatusDictStr)
                fd.close()
                            
                table2Dict = {}
                   
                #Database stores KW not KWH, in error. Report KWH as it should be.
                if EPSolarTracerInterface.TRACER_KW_GEN_DAY in sysStatusDict:
                    table2Dict[0]=[HttpJsonTranslator.TRACER_KWH_GEN_DAY, "%.3f" % (sysStatusDict[EPSolarTracerInterface.TRACER_KW_GEN_DAY]) ]
                
                if EPSolarTracerInterface.TRACER_KW_GEN_MONTH in sysStatusDict:
                    table2Dict[1]=[HttpJsonTranslator.TRACER_KWH_GEN_MONTH, "%.3f" % (sysStatusDict[EPSolarTracerInterface.TRACER_KW_GEN_MONTH]) ]
                
                if EPSolarTracerInterface.TRACER_KW_GEN_YEAR in sysStatusDict:
                    table2Dict[2]=[HttpJsonTranslator.TRACER_KWH_GEN_YEAR, "%.3f" % (sysStatusDict[EPSolarTracerInterface.TRACER_KW_GEN_YEAR]) ]
                
                if EPSolarTracerInterface.TRACER_KW_GEN in sysStatusDict:
                    table2Dict[3]=[HttpJsonTranslator.TRACER_KWH_GEN, "%.3f" % (sysStatusDict[EPSolarTracerInterface.TRACER_KW_GEN]) ]
               
                if OGSolarController.UPTIME in sysStatusDict:
                    table2Dict[3]=[OGSolarController.UPTIME, "%s" % (sysStatusDict[OGSolarController.UPTIME]) ]
     
                table2StatusDictStr = json.dumps( table2Dict, sort_keys=True, indent=4, separators=(',', ': '))
                
                fd = open(self._table2File, 'w')
                fd.write(table2StatusDictStr)
                fd.close()
            
            else:
                self._uio.error("{}: No sysStatusDict read from conduit.".format(self.__class__))


