#!/usr/bin/env python3

from p3lib.pconfig import ConfigManager
from ogsolar.libs.ads1115 import ADS1115ADC
from ogsolar.libs.gpio_control import GPIOControl

class ADCCalibration(object):
    """@brief Responsible for calibrating the voltage and current measurements."""

    #Choose slowest ADS1115 conversion rate for highest accuracy.
    ADC_SPS                    = 8
    CAL_FILE                   = "ogsolar_adc_cal.cfg"
    CODES_PER_VOLT_ATTR        = "CODES_PER_VOLT"
    NO_CURRENT_CODES_ATTR      = "NO_CURRENT_CODES"
    CODES_PER_AMP_ATTR         = "CODES_PER_AMP"
    DEFAULT_CAL_CONFIG = {
        CODES_PER_VOLT_ATTR:      2209,
        CODES_PER_AMP_ATTR:       785,
        NO_CURRENT_CODES_ATTR:    0
    }
    
    def __init__(self, uio, options):
        """@brief Constructor."""
        self._uio     = uio
        self._options = options
        
        self._ads1115ADC = ADS1115ADC(ADS1115ADC.ADDR_PIN_LOW_SLAVE_ADDR, simulateHardware=self._options.sim_ads1115)
        self._gpioControl = GPIOControl(self._uio, self._options)       
               
        self._calConfigManager = ConfigManager(self._uio, ADCCalibration.CAL_FILE, ADCCalibration.DEFAULT_CAL_CONFIG)
        self._calConfigManager.load()
        
    def calibrate(self):
        """@brief calibrate the voltage and current measurements."""
        self._calibrateVoltage()
        self._calibrateCurrent()
        
    def _calibrateVoltage(self):
        """@brief Calibrate the voltage measurements."""
        self._gpioControl.selectACMains(True)
        self._gpioControl.spare(False)
        self._gpioControl.setLoad1(GPIOControl.DC_POWER_OFF)
        self._gpioControl.setLoad2(GPIOControl.DC_POWER_OFF)
        
        voltage = ConfigManager.GetFloat(self._uio, "Enter the voltage measured")

        #Set the ADC that measures the voltage
        fsVoltage = 4.096
        samplesPerSecond = ADCCalibration.ADC_SPS
        self._ads1115ADC.setADC2(fsVoltage, samplesPerSecond)
        codes = self._ads1115ADC.getADC2(singleEnded=True)

        codesPerVolt = int(round(float(codes)/float(voltage)))

        self._calConfigManager.addAttr(ADCCalibration.CODES_PER_VOLT_ATTR, codesPerVolt)
        self._calConfigManager.store()    
        
    def _calibrateCurrent(self):
        """@brief Calibrate the current measurements."""

        self._gpioControl.selectACMains(True)
        self._gpioControl.spare(False)
        self._gpioControl.setLoad1(GPIOControl.DC_POWER_OFF)
        self._gpioControl.setLoad2(GPIOControl.DC_POWER_OFF)
        
        #Set the ADC that measures the current
        fsVoltage = 1.024
        samplesPerSecond = ADCCalibration.ADC_SPS
        self._ads1115ADC.setADC0(fsVoltage, samplesPerSecond)
        noCurrentValue = self._ads1115ADC.getSignedValue(0, singleEnded=True, bitCount=16)
        self._uio.debug("noCurrentValue = {}".format(noCurrentValue))

        self._gpioControl.setLoad1(GPIOControl.DC_POWER_ON)
        self._gpioControl.setLoad2(GPIOControl.DC_POWER_ON)
        self._uio.info("Switched Load 1 and Load 2 ON.")
        self._uio.info("Ensure you have a load current.")
        amps = ConfigManager.GetFloat(self._uio, "Enter the amps measured")

        if amps < 1:
            raise Exception("The current measured must be at least 1 amp when calibrating the ADC for current measurement.")  

        withCurrentValue = self._ads1115ADC.getSignedValue(0, singleEnded=True, bitCount=16)
        #ampCodes = self._ads1115ADC.getADC0(singleEnded=False)
        self._uio.debug("No current ADC0 value = {}/0x{:x}".format(noCurrentValue, noCurrentValue))
        self._uio.debug("ADC0 value            = {}/0x{:x}".format(withCurrentValue, withCurrentValue))
        
        deltaCodes = withCurrentValue-noCurrentValue
        self._uio.debug("deltaCodes            = {}".format(deltaCodes))
        codesPerAmp = int(round(deltaCodes/amps))
        self._uio.debug("codesPerAmp           = {}".format(codesPerAmp))

        self._gpioControl.setLoad1(GPIOControl.DC_POWER_OFF)
        self._gpioControl.setLoad2(GPIOControl.DC_POWER_OFF)

        self._calConfigManager.addAttr(ADCCalibration.NO_CURRENT_CODES_ATTR, noCurrentValue)
        self._calConfigManager.addAttr(ADCCalibration.CODES_PER_AMP_ATTR, codesPerAmp)
        self._calConfigManager.store()
