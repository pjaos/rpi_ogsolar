#!/usr/bin/env python

from   time import sleep

from p3lib.pconfig import ConfigManager
from ogsolar.libs.ads1115 import ADS1115ADC
from ogsolar.libs.adc_cal import ADCCalibration

class ADCInterface(object):

    BAT_VOLTS                  = "BATTERY VOLTS OUT"
    BAT_AMPS                   = "BATTERY AMPS OUT"
    CONDUIT_CMD                = "CMD"
    GET_BAT_STATE_CMD          = 1
    MCP9700_CODES_PER_VOLT     = 16570.0
    MCP9700_VOUT_0C            = 0.5
    MCP9700_TC                 = 0.01

    def __init__(self, uio, options):
        self._uio       = uio
        self._options   = options
        self._value     = None
        
        self._ads1115ADC = ADS1115ADC(ADS1115ADC.ADDR_PIN_LOW_SLAVE_ADDR, simulateHardware=self._options.sim_ads1115)
        
        self._calConfigManager = ConfigManager(self._uio, ADCCalibration.CAL_FILE, ADCCalibration.DEFAULT_CAL_CONFIG)
        self._calConfigManager.load()
                       
    def getBatteryVoltage(self):
        """@return Read the battery voltage from the i2C ADC (ADS1115)"""
        codesPerVolt = self._calConfigManager.getAttr(ADCCalibration.CODES_PER_VOLT_ATTR)
        if codesPerVolt <= 0:
            self._uio.error("!!! Invalid voltage ADCCalibration: codesPerVolt = %.1f" % (codesPerVolt) )

        #Set the ADC that measures the voltage
        fsVoltage = 4.096
        samplesPerSecond = ADCCalibration.ADC_SPS
        self._ads1115ADC.setADC2(fsVoltage, samplesPerSecond)

        value = self._ads1115ADC.getADC2(singleEnded=True)
        if self._options.debug:
            self._uio.debug("VOLTAGE ADC value: 0x%04x" % (value) )
        self._value = value
            
        volts=0.0
        if codesPerVolt > 0 and value <= 32767:
            volts = float(value)/codesPerVolt

        return volts
                
    def getLoadAmps(self):
        """@return Read the current being pulled from the battery from the i2C ADC (ADS1115)"""

        noCurrentCodes=self._calConfigManager.getAttr(ADCCalibration.NO_CURRENT_CODES_ATTR)
        codesPerAmp=self._calConfigManager.getAttr(ADCCalibration.CODES_PER_AMP_ATTR)
        
        if codesPerAmp <= 0:
            self._uio.error("!!! Invalid current ADCCalibration: codesPerAmp = %.1f" % (codesPerAmp) )
            return -1.0

        #Set the ADC that measures the current
        fsVoltage = 1.024
        samplesPerSecond = ADCCalibration.ADC_SPS
        self._ads1115ADC.setADC0(fsVoltage, samplesPerSecond)

        value = self._ads1115ADC.getSignedValue(0, singleEnded=True, bitCount=16)
        if self._options.debug:
            self._uio.debug("AMPS ADC value: 0x%04x" % (value) )
        self._value = value

        codes = value-noCurrentCodes
        amps=0.0
        if codesPerAmp > 0:
            amps = float(codes)/codesPerAmp
        
        self._uio.debug("AMPS = {:.03f}".format(amps) )
        
        #Add a 10ma low current limit as previously low -ve amps values could be reported.
        if amps < 0.01:
            amps = 0
            self._uio.debug("Set AMPS to 0.0 as below 0.01 threshold." )

        return amps
        
    def getHSTemp(self):
        """@brief Read the temperature of the MCP9700 heatsink temp sensor.
           @return The temp in C"""
        fsVoltage = 2.048
        samplesPerSecond = ADCCalibration.ADC_SPS
        self._ads1115ADC.setADC3(fsVoltage, samplesPerSecond)
        tempADC = self._ads1115ADC.getADC3(singleEnded=True)
        self._value = tempADC
        mcp9700Volts = tempADC / ADCInterface.MCP9700_CODES_PER_VOLT
        tempC = ( mcp9700Volts - ADCInterface.MCP9700_VOUT_0C ) / ADCInterface.MCP9700_TC
        return tempC
    
    def getCPUTemp(self):
        """@brief Read the temperature of the MCP9700 CPU temp sensor.
           @return The temp in C"""
        fsVoltage = 2.048
        samplesPerSecond = ADCCalibration.ADC_SPS
        self._ads1115ADC.setADC1(fsVoltage, samplesPerSecond)
        tempADC = self._ads1115ADC.getADC1(singleEnded=True)
        self._value = tempADC
        mcp9700Volts = tempADC / ADCInterface.MCP9700_CODES_PER_VOLT
        tempC = ( mcp9700Volts - ADCInterface.MCP9700_VOUT_0C ) / ADCInterface.MCP9700_TC
        return tempC

    def debugVoltage(self):
        """@brief Debug the voltage ADC measurement."""
        
        while True:
            
            volts = self.getBatteryVoltage()
            self._uio.info("VOLTS (ADC2): 0x%04x %.3f Volts" % (self._value, volts) )
            sleep(1)

    def debugCurrent(self):
        """@brief Debug the amps ADC measurement."""
        
        while True:
            
            amps  = self.getLoadAmps()
            self._uio.info("AMPS (ADC0): {}/{:.3f} Amps".format(self._value, amps) )
            sleep(1)
            
    def debugHeatSinkTempC(self):
        """@brief Debug the heatsink temperature measurement."""
        
        while True:
            
            tempC  = self.getHSTemp()
            self._uio.info("AMPS (ADC3): 0x%04x %.3f ℃" % (self._value, tempC) )
            sleep(1)

    def debugCPUTempC(self):
        """@brief Debug the CPU temperature measurement."""
        
        while True:
            
            tempC  = self.getCPUTemp()
            self._uio.info("AMPS (ADC1): 0x%04x %.3f ℃" % (self._value, tempC) )
            sleep(1)
