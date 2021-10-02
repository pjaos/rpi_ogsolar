#!/usr/bin/env python

import resource

from time import sleep, time
from ogsolar.libs.app_config import AppConfig
from ogsolar.libs.epsolar_tracer import EPSolarTracerInterface
from ogsolar.libs.gpio_control import GPIOControl
from ogsolar.libs.adc_interface import ADCInterface

class OGSolarController(object):
    """@brief Responsible for controlling when the battery is discharged."""
    MIN_PV_PWR_WATTS                    = 1.0
    DARKNESS_CHECK_SECONDS              = 3600  # We expected the PV power to be bellow MIN_PV_PWR_WATTS for this period of time before we assume darkness.
    MIN_LOAD_ON_BATTERY_VOLTAGE         = 12.3
    POLL_SECONDS                        = 5
    LOW_POWER_WATTS                     = 2.0
    UPTIME                              = "UPTIME"
    MAX_THREAD_READ_ERROR_COUNT         = 2
    INVERTER_ON_OFF_DELAY               = 2
    MAX_HEATSINK_TEMP_C                 = 65
    MAX_CPU_TEMP_C                      = 60

    @staticmethod
    def GetMemUsage():
        """@brief Return the memory usage of the running python program in kB"""
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

    def __init__(self, uio, options, appConfig, traceConduit, yViewConduit, webConduit, jsonPusherConduit):
        """@brief Constructor."""
        self._uio                   = uio
        self._options               = options
        self._appConfig             = appConfig
        self._traceConduit          = traceConduit
        self._yViewConduit          = yViewConduit
        self._webConduit            = webConduit
        self._jsonPusherConduit     = jsonPusherConduit
        
        self._lastTimePwrFromPV     = time()-OGSolarController.DARKNESS_CHECK_SECONDS
        self._errorMessage          = None
        self._startTime             = time()
        self._allowBatteryLoadOn    = True
        self._running               = False
        self._stopped               = False
                
        self._gpioControl = GPIOControl(self._uio, self._options)    
        self._adcInterface = ADCInterface(self._uio, self._options)
        
        self._load1On               = False
        self._load2On               = False
        
    def getErrorMessage(self):
        """@brief Get an error message. If no error has occured then this will be None."""
        return self._errorMessage    
    
    def _showMemUsage(self, id):
        """@brief Report the memory usage
           @param id The ID (integer value) of the point in the code at which the memory usage is reported."""     
        if self._options.debug:
            self._uio.info("%s: %d Memory usage: %d (kB)'" % (self.__class__.__name__, id, OGSolarController.GetMemUsage() ) )

    def _getBValue(self, conduit):
        """@brief get a value from the conduit (B end)."""
        bValue = None
        #If multiple values exist in conduit then read the last one.
        while conduit.bReadAvailable():
            bValue = conduit.getB()
        
        return bValue
               
    def _getTracerRegDict(self):
        """@brief Get the register state from the charge controller."""
        cmdDict={EPSolarTracerInterface.CONDUIT_CMD: EPSolarTracerInterface.GET_TRACER_STATE_CMD}
        self._traceConduit.putB(cmdDict)
        return self._traceConduit.getB()

    def _updateWiFiConnectedLED(self):
        """@brief Update the state of the Wifi connected LED"""
        #If we have message/s from the yviewClient read them
        ipDict = None
        while self._yViewConduit.aReadAvailable():
             ipDict = self._yViewConduit.getA()

        if ipDict and "IP_ADDRESS" in ipDict:
            ipAddress = ipDict["IP_ADDRESS"]
            self._uio.info("ipAddress=%s" % (str(ipAddress)) )
            if len(ipAddress) > 0:
                self._gpioControl.setLed(True)
            else:
                self._gpioControl.setLed(False)
                  
    def _spinLockDelay(self):
        """Add a delay to stop spin lock."""
        sleep(0.25)
                 
    def run(self):
        """@brief Called to start the process of controlling the ogsolar controller."""
        
        if self._options.off:
            self._setLoadsOff()
            return 

        self._allowBatteryLoadOn = self._appConfig.getAttr(AppConfig.ALLOW_BATTERY_LOAD_ON)
                
        self._setInitalLoadState()
        self._running = True
        self._stopped = False
        self._mpptReadErrorCount = 0
        try:
            while self._running:            

                self._updateWiFiConnectedLED()
            
                #Update here so that the user can change config on the fly while ogsolar is running
                self._allowBatteryLoadOn = self._appConfig.getAttr(AppConfig.ALLOW_BATTERY_LOAD_ON)

                pollSecs = self._appConfig.getAttr(AppConfig.TRACER_MPPT_POLL_SECONDS)
                
                self._showMemUsage(1)
                        
                self._checkMaxTemp()
                
                sysStatusDict = self._getTracerRegDict()
                if not sysStatusDict:
                    errMsg        = "!!! No data read from Tracer MPPT Controller !!!"
                    self._uio.error("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    self._uio.error(errMsg)
                    self._uio.error("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    self._setLoadsOff()
                    if not self._errorMessage:
                        self._errorMessage = errMsg
                    self._spinLockDelay()
                    self._mpptReadErrorCount = self._mpptReadErrorCount + 1
                    if self._mpptReadErrorCount > OGSolarController.MAX_THREAD_READ_ERROR_COUNT:
                        raise Exception("{} attempts failed to read data from the MPPT controller.".format(self._mpptReadErrorCount))
                    raise Exception(errMsg)

                self._adcUpdate(sysStatusDict)
                
                #Reset the thread read error count now we've read data from the MPPT controller
                self._mpptReadErrorCount = 0
        
                self._showMemUsage(2)
        
                #Send to the icons network for propagation to cloud services
                self._yViewConduit.putA(sysStatusDict)
        
                self._showMemUsage(3)
        
                #Send to the HTTP rest API server
                self._webConduit.putB(sysStatusDict)
        
                self._showMemUsage(4)
        
                #Send JSON to JSON pusher to be pushed over any connected clients 
                self._jsonPusherConduit.putA(sysStatusDict)
        
                self._showMemUsage(5)

                self.updateLoadState(sysStatusDict)
        
                self._showMemUsage(6)
        
                #If the user changes the syslog host calling this here will mean it gets updated on the fly
                syslogServer = self._appConfig.getAttr(AppConfig.SYSLOG_SERVER)
                if syslogServer and len(syslogServer) > 0:
                    self._uio.enableSyslog(True, host=syslogServer)
        
                self._showMemUsage(7)
                   
                sleep(pollSecs)
        
        finally:
            self._uio.info("OGSolar controller shutting down.")
            self._setLoadsOff()
            self._uio.info("OGSolar controller shut down.")
            self._gpioControl.close()
            self._stopped = True
                              
    def _setInitalLoadState(self):
        """@brief Select the initial state as defined on the command line."""
        if self._options.inv_on:
            if self._allowBatteryLoadOn:
                self._uio.info("Set inverter ON (initial state).")
                self._setLoad1(True)
            else:
                self._uio.error("Cannot force inverter on as battery load disabled.")
                
        else:
            self._uio.info("Set inverter off initial state.")
            self._setLoad1(False)

        #Always start with load2 on
        self._setLoad2(True)

    def _adcUpdate(self, sysStatusDict):
        """@brief Update the readings from the ADC. 
           @param sysStatusDict The dict of values obtained from the MPPT controller."""     
       
        # We have the ability to read the battery voltage from the I2C ADC but we use the battery voltage
        # as read from the MPPT controller.
        
        # Use battery voltage read by EPEver Tracer controller
        #sysStatusDict[EPSolarTracerInterface.BAT_VOLTS] = sysStatusDict[EPSolarTracerInterface.TRACER_BAT_VOLTS]
        
        #Use battery voltage measured by ADC on this controller.
        sysStatusDict[EPSolarTracerInterface.BAT_VOLTS] = self._adcInterface.getBatteryVoltage()
        
        # The load current is derived from the ADC measuring the voltage across a shunt resistor.
        sysStatusDict[EPSolarTracerInterface.BAT_AMPS] = self._adcInterface.getLoadAmps()

        # Calc the total load Watts   
        sysStatusDict[EPSolarTracerInterface.BAT_LOAD_WATTS] = sysStatusDict[EPSolarTracerInterface.BAT_VOLTS]*sysStatusDict[EPSolarTracerInterface.BAT_AMPS]
        
        self._uio.info('Load AMPS: {:.3f}, Load WATTS {:.3f}'.format(sysStatusDict[EPSolarTracerInterface.BAT_AMPS], 
                                                                     sysStatusDict[EPSolarTracerInterface.BAT_LOAD_WATTS])) 
                
    def _checkMaxTemp(self):
        """@brief Check that the temperatures of the hatsink and the CPU are below the max values."""
        heatSinkTempC = self._adcInterface.getHSTemp()
        cpuTempC = self._adcInterface.getCPUTemp()
        
        self._uio.info('Heat sink: {:.1f} °C'.format(heatSinkTempC)) 
        self._uio.info('CPU:       {:.1f} °C'.format(cpuTempC)) 
        
        if heatSinkTempC > OGSolarController.MAX_HEATSINK_TEMP_C:
            raise Exception("Heat sink temp > max {:.1f}".format(OGSolarController.MAX_HEATSINK_TEMP_C))

        if cpuTempC > OGSolarController.MAX_CPU_TEMP_C:
            raise Exception("CPU temp > max {:.1f}".format(OGSolarController.MAX_CPU_TEMP_C))
    
    def _updateLoad(self, load, onV, offV, batVolts):
        """@brief Update the load state.
           @param load The load to update (1 or 2).
           @param onV The battery voltage at which the load should be turned on.
           @param offV The battery voltage at which the load should be turned off.
           @param batVolts The current battery voltage.
           @return True if the load is on"""

        if load == 1:
            loadOn = self._load1On
            
        elif load == 2:
            loadOn = self._load2On     
            
        else:
            raise Exception("BUG: {} load is invalid. Must be 1 or 2.")
            
        if loadOn:
            self._uio.info( 'Load {} ON:  Battery volts: {:.3f}. Waiting for battery voltage to drop to {:.3f} volts.'.format(load, batVolts, offV) )         
            if batVolts <= offV:
                self._setLoad(load, False)
                self._uio.info('Off battery voltage threshold reached. Turned OFF load {}'.format(load)) 

        else:
            self._uio.info( 'Load {} OFF:  Battery volts: {:.3f}. Waiting for battery voltage to reach {:.3f} volts.'.format(load, batVolts, onV) )         
            if batVolts >= onV:
                self._setLoad(load, True)
                self._uio.info('On battery voltage threshold reached. Turned ON load {}'.format(load))
                
        return loadOn
                           
    def updateLoadState(self, sysStatusDict):
        """@brief update the load states of the system. This does not include the load port of the MPPT controller.
           We check for the float charge state from the tracer MPPT controller.
           If at the float charge state then we switch the acMains off and the inverter on.
           This moves us to the loadOn state.
           In the loadOn state we check for the minimum.
           @param sysStatusDict The dict of values obtained from the MPPT controller."""

        if EPSolarTracerInterface.TRACER_BAT_VOLTS in sysStatusDict and \
           EPSolarTracerInterface.TRACER_BAT_CHARGE_STATUS in sysStatusDict:
            batVolts = sysStatusDict[EPSolarTracerInterface.TRACER_BAT_VOLTS]
            chargeState = sysStatusDict[EPSolarTracerInterface.TRACER_BAT_CHARGE_STATUS]            
            
            self._uio.info('Battery charge state = {}'.format(chargeState))
    
            load1OnVoltage  = self._appConfig.getAttr(AppConfig.LOAD1_ON_VOLTAGE)
            load1OffVoltage = self._appConfig.getAttr(AppConfig.LOAD1_OFF_VOLTAGE)
            self._updateLoad(1, load1OnVoltage, load1OffVoltage, batVolts)
                    
            load2OnVoltage  = self._appConfig.getAttr(AppConfig.LOAD2_ON_VOLTAGE)  
            load2OffVoltage = self._appConfig.getAttr(AppConfig.LOAD2_OFF_VOLTAGE)  
            self._updateLoad(2, load2OnVoltage, load2OffVoltage, batVolts)

        else:
            self._setLoadsOff()
            self._uio.error('Unable to read battery volts and charge state.')
            self._uio.error('Turned load 1 and load 2 off.')
                            
    def _setLoadsOff(self):
        """@brief Turn off both load ports. Select AC mains and turn off spare relay."""
        self._setLoad1(False)
        self._setLoad2(False)
        self._gpioControl.selectACMains(True)
        self._gpioControl.spare(False)
        
    def _setLoad1(self, on):
        """@brief Set load 1 on/off. Load 1 is connected to the inverter.
                  The load is turned 
           @param on If True set load on."""
        self._gpioControl.setLoad1(on)
        self._load1On = on
        if on:
            loadState = "ON"
        else:
            loadState = "OFF"
        self._uio.info('Turned load 1 {}'.format(loadState) )
        
        sleep(OGSolarController.INVERTER_ON_OFF_DELAY)
        if on:
            self._gpioControl.selectACMains(False)
            self._uio.info('------------------> Selected AC from inverter output.')
        else:
            self._gpioControl.selectACMains(True)
            self._uio.info('------------------> Selected AC from mains supply.')            

    def _setLoad2(self, on):
        """@brief Set load 2 on/off.
           @param on If True set load on."""
        self._gpioControl.setLoad2(on)
        self._load2On = on
        if on:
            loadState = "ON"
        else:
            loadState = "OFF"
        self._uio.info('Turned load 2 {}'.format(loadState) )
                
    def _setLoad(self, load, on):
        """@brief Set either load 1 or load 2 on/off.
           @param load The load, either 1 or 2.
           @param on If True turn load on."""
        if load == 1:
            self._setLoad1(on)
        elif load == 2:
            self._setLoad2(on)
        else:
            raise Exception("BUG: {} load is invalid. Must be 1 or 2.".format(load))
        
    def shutDown(self):
        """@brief Shutdown the controller"""
        self._uio.info("Shutting down ogsolar controller")
        self._running = False
        self._uio.warn("Waiting for the ogsolar controller to shutdown.")
        while not self._stopped:
            pass
        self._uio.warn("OGSolar controller is shutdown.")      

        
