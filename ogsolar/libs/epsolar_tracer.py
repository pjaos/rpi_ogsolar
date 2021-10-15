#!/usr/bin/env python

import os
from   time import sleep

from ogsolar.libs.app_config import AppConfig
from ogsolar.libs.tracer import EPSolarTracer,\
                        CHARGING_EQUIPMENT_INPUT_VOLTAGE,\
                        CHARGING_EQUIPMENT_INPUT_CURRENT,\
                        CHARGING_EQUIPMENT_OUTPUT_VOLTAGE,\
                        CHARGING_EQUIPMENT_OUTPUT_CURRENT,\
                        CHARGING_EQUIPMENT_STATUS,\
                        CHARGING_EQUIPMENT_INPUT_POWER_L,\
                        CHARGING_EQUIPMENT_INPUT_POWER_H,\
                        CHARGING_EQUIPMENT_OUTPUT_POWER_L,\
                        CHARGING_EQUIPMENT_OUTPUT_POWER_H,\
                        DISCHARGING_EQUIPMENT_OUTPUT_POWER_L,\
                        DISCHARGING_EQUIPMENT_OUTPUT_POWER_H,\
                        DISCHARGING_EQUIPMENT_OUTPUT_VOLTAGE,\
                        DISCHARGING_EQUIPMENT_OUTPUT_CURRENT,\
                        TOTAL_GENERATED_ENERGY_L,\
                        TOTAL_GENERATED_ENERGY_H,\
                        GENERATED_ENERGY_TODAY_L,\
                        GENERATED_ENERGY_TODAY_H,\
                        GENERATED_ENERGY_THIS_MONTH_L,\
                        GENERATED_ENERGY_THIS_MONTH_H,\
                        GENERATED_ENERGY_THIS_YEAR_L,\
                        GENERATED_ENERGY_THIS_YEAR_H,\
                        REMOTE_BATTERY_TEMPERATURE,\
                        TEMPERATURE_INSIDE_EQUIPMENT,\
                        TRACER_REG_DICT,\
                        MANUAL_CONTROL_THE_LOAD,\
                        BATTERY_STATUS,\
                        BATTERY_TEMPERATURE_WARNING_LOWER_LIMIT

class EPSolarTracerInterface(object):

    CONDUIT_CMD                = "CMD"
    GET_TRACER_STATE_CMD       = 1
    SET_LOAD_ON_CMD            = 2
    SET_LOAD_OFF_CMD           = 3
    
    STATUS_REG_SET = [
        TRACER_REG_DICT[CHARGING_EQUIPMENT_STATUS],
        TRACER_REG_DICT[CHARGING_EQUIPMENT_INPUT_VOLTAGE],
        TRACER_REG_DICT[CHARGING_EQUIPMENT_INPUT_CURRENT],
        TRACER_REG_DICT[CHARGING_EQUIPMENT_OUTPUT_VOLTAGE],
        TRACER_REG_DICT[CHARGING_EQUIPMENT_OUTPUT_CURRENT],
        TRACER_REG_DICT[CHARGING_EQUIPMENT_INPUT_POWER_L],
        TRACER_REG_DICT[CHARGING_EQUIPMENT_INPUT_POWER_H],
        TRACER_REG_DICT[CHARGING_EQUIPMENT_OUTPUT_POWER_L],
        TRACER_REG_DICT[CHARGING_EQUIPMENT_OUTPUT_POWER_H],
        TRACER_REG_DICT[DISCHARGING_EQUIPMENT_OUTPUT_POWER_L],
        TRACER_REG_DICT[DISCHARGING_EQUIPMENT_OUTPUT_POWER_H],
        TRACER_REG_DICT[DISCHARGING_EQUIPMENT_OUTPUT_VOLTAGE],
        TRACER_REG_DICT[DISCHARGING_EQUIPMENT_OUTPUT_CURRENT],
        TRACER_REG_DICT[TOTAL_GENERATED_ENERGY_L],
        TRACER_REG_DICT[TOTAL_GENERATED_ENERGY_H],
        TRACER_REG_DICT[GENERATED_ENERGY_TODAY_L],
        TRACER_REG_DICT[GENERATED_ENERGY_TODAY_H],
        TRACER_REG_DICT[GENERATED_ENERGY_THIS_MONTH_L],
        TRACER_REG_DICT[GENERATED_ENERGY_THIS_MONTH_H],
        TRACER_REG_DICT[GENERATED_ENERGY_THIS_YEAR_L],
        TRACER_REG_DICT[GENERATED_ENERGY_THIS_YEAR_H],
        TRACER_REG_DICT[REMOTE_BATTERY_TEMPERATURE],
        TRACER_REG_DICT[TEMPERATURE_INSIDE_EQUIPMENT],
        TRACER_REG_DICT[BATTERY_STATUS],
        TRACER_REG_DICT[BATTERY_TEMPERATURE_WARNING_LOWER_LIMIT]
    ]

    # keys for status dict used by ogsolar
    TRACER_BAT_CHARGE_STATUS    = "BATTERY CHARGE STATUS"
    TRACER_PV_VOLTS             = "PV VOLTS"
    TRACER_PV_AMPS              = "PV AMPS"
    TRACER_BAT_VOLTS            = "BATTERY VOLTS"
    TRACER_BAT_AMPS             = "BATTERY AMPS IN"
    
    TRACER_PV_WATTS             = "PV WATTS"
    TRACER_BAT_WATTS            = "BATTERY WATTS IN"
    BAT_LOAD_WATTS              = "BATTERY WATTS OUT"
            
    TRACER_KW_GEN_DAY           = "GENERATED KW TODAY"
    TRACER_KW_GEN_MONTH         = "GENERATED KW THIS MONTH"
    TRACER_KW_GEN_YEAR          = "GENERATED KW THIS YEAR"
    TRACER_KW_GEN               = "GENERATED KW"
    BATTERY_TEMPERATURE         = "BATTERY TEMPERATURE (C)"
    CONTROLLER_TEMPERATURE      = "CONTROLLER TEMPERATURE (C)"
        
    BAT_VOLTS                  = "BATTERY VOLTS OUT"
    BAT_AMPS                   = "BATTERY AMPS OUT"

    MPPT_LOAD_VOLTS            = "MPPT_LOAD_VOLTS"
    MPPT_LOAD_AMPS             = "MPPT_LOAD_AMPS"
    MPPT_LOAD_WATTS            = "MPPT_LOAD_WATTS"
    
    CMD_RESPONSE               = "CMD_RESPONSE_SUCCESS"
    SUCCESS                    = 1
    FAILURE                    = 0
    
    MIN_BATTERY_CHARGE_TEMP    = 0
    
    def __init__(self, uio, options, appConfig, tracerConduit):
        self._uio               =   uio
        self._options           =   options
        self._appConfig         =   appConfig
        self._tracerConduit     =   tracerConduit
        self._translatedDict    =   {}
        self._tracerClient      =   None

    def run(self):
        """@param Periodically read the status from the EPSolar Tracer MPPT charge controller 
                  and send over the conduit."""
                  
                  
        while True:    
            try:
                
                try:
                    
                    self._connectToTracer()
                    
                    while True:
                        pollSeconds = self._appConfig.getAttr(AppConfig.TRACER_MPPT_POLL_SECONDS)/2
                        try:
                            
                            if self._tracerConduit.aReadAvailable():
                                cmdDict = self._tracerConduit.getA()
                                self._processCmd(cmdDict)
                            
                        except IOError:
                            self._uio.errorException()
            
                        sleep(pollSeconds)
                        
                finally:
                    pass

                self._tracerClient.disconnect()                    
                    
            except IOError:
                sleep(5)
                
    def _processCmd(self, cmdDict):
        """@brief Process a command received over the conduit.
           @param cmdDict The command dict to be processed."""
        
        cmdProcessed = False
        
        try:

            if EPSolarTracerInterface.CONDUIT_CMD in cmdDict:
                cmd = cmdDict[EPSolarTracerInterface.CONDUIT_CMD]
                self._uio.debug("EPSolarTracerInterface:_processCmd: {}".format(cmd))
                if cmd == EPSolarTracerInterface.GET_TRACER_STATE_CMD:
                    self._forward()
                    cmdProcessed = True
                    
                elif cmd == EPSolarTracerInterface.SET_LOAD_ON_CMD:
                    self._setLoadOn(True)
                    cmdProcessed = True
                    
                elif cmd == EPSolarTracerInterface.SET_LOAD_OFF_CMD:
                    self._setLoadOn(False)
                    cmdProcessed = True
                    

        #Sometimes the interface to the MPPT controller locks up, not sure why
        except:
            raise
            self._uio.errorException()
            
        if not cmdProcessed:
            self._sendNone()
            
    def _setLoadOn(self, on):
        """@brief Set the load o/off
           @param on If True then turn the load on."""
        try:
            loadReg = self._tracerClient.getRegisterByName(MANUAL_CONTROL_THE_LOAD)
            # Found that to reliably set the load it needs to be set
            for _ in range(0,1):
                if on:
                    loadReg.setValue(1)
                    loadStateStr = "ON"
                else:
                    loadReg.setValue(0)
                    loadStateStr = "OFF"
        
                self._tracerClient.writeRegList([loadReg,])
                self._uio.info("Set load {}".format(loadStateStr))
                sleep(1)
                responseDict = {EPSolarTracerInterface.CMD_RESPONSE: EPSolarTracerInterface.SUCCESS}
        except:
                responseDict = {EPSolarTracerInterface.CMD_RESPONSE: EPSolarTracerInterface.FAILURE}
        self._tracerConduit.putA(responseDict)
                                   
    def _sendNone(self):
        """@brief Send a None response on the conduit."""
        self._tracerConduit.putA(None)
 
    def _connectToTracer(self):
        """@brief connect to the tracer serial port."""
        self._tracerClient = EPSolarTracer(self._appConfig.getAttr(AppConfig.TRACER_MPPT_SERIAL_PORT))
        if not self._sumulateTracerHW():

            self._tracerClient.connect()
        
    def _forward(self):
        """@brief Forward messages from the tracer MPPT controller to the message bus server."""

        self._readRegSet()

        self._tracerConduit.putA(self._translatedDict)
                   
    def _sumulateTracerHW(self):
        """@brief Determine if the tracer HW should be simulated.
           @return True if the Tracer HW is to be simulated."""
        simulateTracerHW = False
        if self._options.sim_json:
            if os.path.isfile( self._options.sim_json ):
                simulateTracerHW = True
            else:
                raise Exception("{} file not found.".format( self._options.sim_json ) )
        return simulateTracerHW
    
    def _readSimulatedHW(self):
        """@brief Simulate the EPSolar Tracer HW by reading the tracer
                  register states from a JSON file rather than the
                  Tracer modbus serial interface.""" 
        fd = open( self._options.sim_json , 'r')
        jsonStr = fd.read()
        fd.close()
        self._tracerClient.setJSON(jsonStr)

    def _readRegSet(self):
        """@brief Read the registers from the tracer unit"""
        if self._sumulateTracerHW():
            self._readSimulatedHW()

        else:
            self._tracerClient.readRegList(EPSolarTracerInterface.STATUS_REG_SET)
            
        self._translatedDict = {}
        self._translatedDict[EPSolarTracerInterface.TRACER_BAT_CHARGE_STATUS] = self._tracerClient.getChargeStatus()
        self._translatedDict[EPSolarTracerInterface.TRACER_PV_VOLTS] = self._tracerClient.getRegisterByName(CHARGING_EQUIPMENT_INPUT_VOLTAGE).getValue()     # The PV volts
        self._translatedDict[EPSolarTracerInterface.TRACER_PV_AMPS] = self._tracerClient.getRegisterByName(CHARGING_EQUIPMENT_INPUT_CURRENT).getValue()      # The PV amps 
        self._translatedDict[EPSolarTracerInterface.TRACER_BAT_VOLTS] = self._tracerClient.getRegisterByName(CHARGING_EQUIPMENT_OUTPUT_VOLTAGE).getValue()   # The battery voltage
        self._translatedDict[EPSolarTracerInterface.TRACER_BAT_AMPS] = self._tracerClient.getRegisterByName(CHARGING_EQUIPMENT_OUTPUT_CURRENT).getValue()    # The battery charging amps
        
        self._translatedDict[EPSolarTracerInterface.TRACER_PV_WATTS] = self._tracerClient.getRegisterByName(CHARGING_EQUIPMENT_INPUT_POWER_H).getValue()     # The PV watts currently being generated
        self._translatedDict[EPSolarTracerInterface.TRACER_BAT_WATTS] = self._tracerClient.getRegisterByName(CHARGING_EQUIPMENT_OUTPUT_POWER_H).getValue()   # The battery charging current

        self._translatedDict[EPSolarTracerInterface.BATTERY_TEMPERATURE] = self._tracerClient.getRegisterByName(REMOTE_BATTERY_TEMPERATURE).getValue()       # The battery temperature (external MPPT sensor)
        self._translatedDict[EPSolarTracerInterface.CONTROLLER_TEMPERATURE] = self._tracerClient.getRegisterByName(TEMPERATURE_INSIDE_EQUIPMENT).getValue()  # The MPPT controller temperature.
    
        self._translatedDict[EPSolarTracerInterface.MPPT_LOAD_VOLTS] = self._tracerClient.getRegisterByName(DISCHARGING_EQUIPMENT_OUTPUT_VOLTAGE).getValue() # The MPPT Load volts (should be very close to the battery voltage)
        self._translatedDict[EPSolarTracerInterface.MPPT_LOAD_AMPS] = self._tracerClient.getRegisterByName(DISCHARGING_EQUIPMENT_OUTPUT_CURRENT).getValue()  # The MPPT Load Amps
        self._translatedDict[EPSolarTracerInterface.MPPT_LOAD_WATTS] = self._tracerClient.getRegisterByName(DISCHARGING_EQUIPMENT_OUTPUT_POWER_H).getValue() # The MPPT Load Watts        

        self._translatedDict[EPSolarTracerInterface.TRACER_KW_GEN] = self._tracerClient.getRegisterByName(TOTAL_GENERATED_ENERGY_H).getValue()               # The MPTT total KWH generated
        self._translatedDict[EPSolarTracerInterface.TRACER_KW_GEN_DAY] = self._tracerClient.getRegisterByName(GENERATED_ENERGY_TODAY_H).getValue()           # The MPTT KWH generated today
        self._translatedDict[EPSolarTracerInterface.TRACER_KW_GEN_MONTH] = self._tracerClient.getRegisterByName(GENERATED_ENERGY_THIS_MONTH_H).getValue()    # The MPTT KWH generated this month
        self._translatedDict[EPSolarTracerInterface.TRACER_KW_GEN_YEAR] = self._tracerClient.getRegisterByName(GENERATED_ENERGY_THIS_YEAR_H).getValue()      # The MPTT KWH generated this year

        # It is dangerous to charge Lion batteries below 0C as this risks dendrite creation. 
        # These can grow through the electrolyte and short out the battery.
        # Therefore ensure we set the min temperature that the charger will charge the battery.
        minBatChargeTemp = self._tracerClient.getRegisterByName(BATTERY_TEMPERATURE_WARNING_LOWER_LIMIT).getValue()
        self._uio.debug(">>>>>>>>>>>>>>>>>>>>>>>>>>>>> Min battery charge temp (°C): {:.1f}".format(minBatChargeTemp))
        if minBatChargeTemp < EPSolarTracerInterface.MIN_BATTERY_CHARGE_TEMP:
            minBatChargeTempReg = self._tracerClient.getRegisterByName(BATTERY_TEMPERATURE_WARNING_LOWER_LIMIT)
            minBatChargeTempReg.setValue(EPSolarTracerInterface.MIN_BATTERY_CHARGE_TEMP)
            self._tracerClient.writeRegList([minBatChargeTempReg,])
            self._uio.debug(">>>>>>>>>>>>>>>>>>>>>>>>>>>>> Set battery charge temp (°C): {:.1f}".format(EPSolarTracerInterface.MIN_BATTERY_CHARGE_TEMP))

        for key in self._translatedDict:
            self._uio.debug("{}={}".format(key, self._translatedDict[key]))
               

        

