#!/usr/bin/env python

from p3lib.pconfig import ConfigManager

class AppConfig(object):
    """@brief Responsible for managing the configuration used by all processes
              that are part of the offgrid_solar application."""

    LOAD1_ON_VOLTAGE                    = "LOAD1_ON_VOLTAGE"            # The battery voltage at which load 1 will be turned on
    LOAD1_OFF_VOLTAGE                   = "LOAD1_CUTOFF_VOLTAGE"        # The battery voltage at which load 1 will be turned off 
    LOAD2_ON_VOLTAGE                    = "LOAD2_ON_VOLTAGE"            # The battery voltage at which load 2 will be turned on
    LOAD2_OFF_VOLTAGE                   = "LOAD2_CUTOFF_VOLTAGE"        # The battery voltage at which load 2 will be turned off 
    SYSLOG_SERVER                       = "SYSLOG_SERVER"
    TRACER_MPPT_SERIAL_PORT             = "TRACER_MPPT_SERIAL_PORT"
    TRACER_MPPT_POLL_SECONDS            = "TRACER_MPPT_POLL_SECONDS"
    ALLOW_BATTERY_LOAD_ON               = "ALLOW_BATTERY_LOAD_ON"
    DELAY_BEFORE_ERROR_REBOOT           = "DELAY_BEFORE_ERROR_REBOOT"

    DEFAULT_STAGE_2_CHARGE_SECONDS      = (3*60*60) #Default 3 hour stage 2 battery charge time.
    DEFAULT_TRACER_MPPT_SERIAL_PORT     = "/dev/ttyUSB0"
    DEFAULT_TRACER_MPPT_POLL_SECONDS    = 5

    CONFIG_FILE                         = "ogsolar.cfg"
    DEFAULT_CONFIG = {
        LOAD1_ON_VOLTAGE:           15.95,
        LOAD1_OFF_VOLTAGE:          14.8,
        LOAD2_ON_VOLTAGE:           15.95,        
        LOAD2_OFF_VOLTAGE:          14.4,
        DELAY_BEFORE_ERROR_REBOOT:  120,
        SYSLOG_SERVER:              "",
        TRACER_MPPT_SERIAL_PORT:    DEFAULT_TRACER_MPPT_SERIAL_PORT,
        TRACER_MPPT_POLL_SECONDS:   DEFAULT_TRACER_MPPT_POLL_SECONDS,
        ALLOW_BATTERY_LOAD_ON:      "y"
    }

    def __init__(self, uio):
        """@brief Constructor."""
        self._uio     = uio

        self._configManager = ConfigManager(self._uio, AppConfig.CONFIG_FILE, AppConfig.DEFAULT_CONFIG)
        self._configManager.load()  

    def _voltageLimitsOK(self, onVKey, offVKey):
        """@brief Check that the voltage limits are correct.
           @param onVKey The on voltage key in the config dict.
           @param offVKey The off voltage key in the config dict.
           @return True if OK."""
        vaildLimits = False
        loadOnV = self._configManager.getAttr(onVKey)
        loadOffV = self._configManager.getAttr(offVKey)
        if loadOnV > loadOffV:
            vaildLimits = True
        else:
            self._uio.error("Load ON voltage {:.2f} is greater than the load OFF voltage {:.2f}.".format(loadOnV, loadOffV))
            
        return vaildLimits
            
    def configure(self):
        """@brief Allow the user to configure the test station attributes.
           @return None"""
        self._configManager.configure(self.editConfig)
        
    def editConfig(self, key):
        """@brief Edit a single config parameter/attribute
           @param key The dictionary key to edit."""
            
        if key == AppConfig.LOAD1_ON_VOLTAGE:
            while True:
                self._configManager.inputFloat(AppConfig.LOAD1_ON_VOLTAGE,  "Enter battery voltage at which load 1 will turn on." , minValue=12.0, maxValue=16.8)
                if self._voltageLimitsOK(AppConfig.LOAD1_ON_VOLTAGE, AppConfig.LOAD1_OFF_VOLTAGE):
                    break
    
        elif key == AppConfig.LOAD1_OFF_VOLTAGE:
            while True:
                self._configManager.inputFloat(AppConfig.LOAD1_OFF_VOLTAGE,  "Enter battery voltage at which load 1 will turn off." , minValue=12.0, maxValue=16.8)
                if self._voltageLimitsOK(AppConfig.LOAD1_ON_VOLTAGE, AppConfig.LOAD1_OFF_VOLTAGE):
                    break
                
        if key == AppConfig.LOAD2_ON_VOLTAGE:
            while True:
                self._configManager.inputFloat(AppConfig.LOAD2_ON_VOLTAGE,  "Enter battery voltage at which load 2 will turn on." , minValue=12.0, maxValue=16.8)
                if self._voltageLimitsOK(AppConfig.LOAD2_ON_VOLTAGE, AppConfig.LOAD2_OFF_VOLTAGE):
                    break

        if key == AppConfig.LOAD2_ON_VOLTAGE:
            self._configManager.inputDecInt(AppConfig.LOAD2_ON_VOLTAGE,  "Enter battery voltage at which load 2 will turn on." , minValue=12.0, maxValue=16.8)
    
        elif key == AppConfig.DELAY_BEFORE_ERROR_REBOOT:
            while True:
                self._configManager.inputFloat(AppConfig.DELAY_BEFORE_ERROR_REBOOT,  "Delay (seconds) before rebooting if an error occurs", 1, 86400)

        elif key == AppConfig.SYSLOG_SERVER:
            self._configManager.inputStr(AppConfig.SYSLOG_SERVER, "Enter the syslog server address", True)

        elif key == AppConfig.TRACER_MPPT_SERIAL_PORT:
            self._configManager.inputStr(AppConfig.TRACER_MPPT_SERIAL_PORT, "Tracer MPPT controller serial port", False )

        elif key == AppConfig.TRACER_MPPT_POLL_SECONDS:
            self._configManager.inputFloat(AppConfig.TRACER_MPPT_POLL_SECONDS, "Tracer MPPT controller poll period", minValue=0.5, maxValue=3600)

        elif key == AppConfig.ALLOW_BATTERY_LOAD_ON:
            self._configManager.inputBool(AppConfig.ALLOW_BATTERY_LOAD_ON, "Allow DC load to be switched on.")
        
    def show(self):
        """@brief Show the current configuration parameters."""
        attrList = self._configManager.getAttrList()
        attrList.sort()

        maxAttLen=0
        for attr in attrList:
            if len(attr) > maxAttLen:
                maxAttLen=len(attr)

        for attr in attrList:
            padding = " "*(maxAttLen-len(attr))
            self._uio.info("%s%s = %s" % (attr, padding, self._configManager.getAttr(attr)) )

    def loadConfigQuiet(self):
        """@brief Load the config without displaying a message to the user."""
        self._configManager.load(showLoadedMsg=False)
        #Update the syslog server address in the UIO instance
        self._uio.setSyslogServer( self._configManager.getAttr(AppConfig.SYSLOG_SERVER) )

    def getAttr(self, key):
        """@brief Get an attribute value.
           @param key The key for the value we're after."""

        #If the config file has been modified then read the config to get the updated state.
        if self._configManager.isModified():
            self._configManager.load(showLoadedMsg=False)
            self._configManager.updateModifiedTime()

        return self._configManager.getAttr(key)
