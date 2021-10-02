#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json

class EPSolarTracer(object):
    """@brief Provides an interface to the EPsolar Tracer series MPPT Solar controller."""

    READ                 = "R"
    READ_WRITE           = "R/W"
    COIL_READ_WRITE      = "C_R/W"
    DISCRETE_READ        = "D_R"
    
    CHARGE_STATUS               = "CHARGE_STATUS"
    CHARGE_STATE_UNKNOWN        = "UNKNOWN"
    CHARGE_STATE_NOT_CHARGING   = "Not Charging"
    CHARGE_STATE_BOOST          = "Boost"
    CHARGE_STATE_FLOAT          = "Float"
    CHARGE_STATE_EQUALISATION   = "Equalisation"
    
    #Register sets. Each entry defines a consecutive number of registers.
    # The ID number 0,1,2 etc defines a set.
    # Each set holds a dict with
    # start:  The start address of the registers set.
    # size:   The number of consecutive 16 bit registers in the set.
    # access: R, R/W, CR/W
    REG_SETS = { 0:  {"start": 0x3000, "size": 9,   "access": READ},
                 1:  {"start": 0x300E, "size": 1,   "access": READ},
                 2:  {"start": 0x3100, "size": 8,   "access": READ},
                 3:  {"start": 0x310C, "size": 7,   "access": READ},
                 4:  {"start": 0x311a, "size": 2,   "access": READ},
                 5:  {"start": 0x311d, "size": 1,   "access": READ},
                 6:  {"start": 0x3200, "size": 2,   "access": READ},
                 7:  {"start": 0x3300, "size": 22,  "access": READ},
                 8:  {"start": 0x331b, "size": 4 ,  "access": READ},
                 9:  {"start": 0x331b, "size": 4 ,  "access": READ},
                 10: {"start": 0x9000, "size": 15 , "access": READ_WRITE},
                 11: {"start": 0x9013, "size": 15 , "access": READ_WRITE},
                 12: {"start": 0x903d, "size": 3 ,  "access": READ_WRITE},
                 13: {"start": 0x9042, "size": 12 , "access": READ_WRITE},
                 14: {"start": 0x9065, "size": 1 ,  "access": READ_WRITE},
                 15: {"start": 0x9067, "size": 1 ,  "access": READ_WRITE},
                 16: {"start": 0x9069, "size": 1 ,  "access": READ_WRITE},
                 17: {"start": 0x906a, "size": 5 ,  "access": READ_WRITE},
                 18: {"start": 0x9070, "size": 1 ,  "access": READ_WRITE},
                 19: {"start": 0x2,    "size": 1 ,  "access": COIL_READ_WRITE},
                 20: {"start": 0x5,    "size": 2 ,  "access": COIL_READ_WRITE},
                 21: {"start": 0x2000, "size": 1,   "access": DISCRETE_READ},
                 22: {"start": 0x200c, "size": 1,   "access": DISCRETE_READ},
               }

    def __init__(self, serialPort, jsonDebugFile=None):
        """@brief Constructor
           @param serialPort The seiral port to whch the EPSolar Tracer unit is connected.
           @param jsonDebugFile If defined then the json file is read rather than the Tracer serial port.
                                This is for debug purposes only when testing without a EPSolar Tracer unit connected to a serial port."""
        self._serialPort = serialPort
        self._jsonDebugFile = jsonDebugFile
        self._tracerClient = None
        self._createAddrIndexDict()
        
    def _createAddrIndexDict(self):
        #We create a dict that has all the Tracer registers.
        # Rather than the key being the register name the key is the register address.
        self._addrKeyTracerRegDict = {}
        for regKey in TRACER_REG_DICT:
            register = TRACER_REG_DICT[regKey]
            register.setRegName(regKey)
            #Add the name of the register to the register to ease identification.
            self._addrKeyTracerRegDict[register.getAddress()] = register
            
    def getRegLines(self):
        """@brief Return lines of text that details the state of all registers."""
        addrList = list( self._addrKeyTracerRegDict.keys() )
        addrList.sort()
        lines = []
        for addr in addrList:
            lines.append(self._addrKeyTracerRegDict[addr])
        return lines

    def connect(self, simTracer=False):
        """@brief connect to the tracer serial port.
           @param simTracer If True then simulate an EPSolar tracer unit."""
        self._simTracer=simTracer
        if not self._simTracer:

            # Import here so that the modbus module is not imported unless an attempt to connect to a modbus device is attempted.
            # The alternative is to use the debug file.
            from pymodbus.client.sync import ModbusSerialClient as ModbusClient

            self._tracerClient = ModbusClient(method='rtu', port=self._serialPort, baudrate=115200, stopbits=1, bytesize=8, timeout=1)
            self._tracerClient.connect()

    def disconnect(self):
        """@brief Disconnect from the tracer unit if connected."""
        if self._tracerClient:
            self._tracerClient.close()
            self._tracerClient = None

    def readRegList(self, tracerRegList):
        """@brief Read a single EPSoler Tracer register.
           @param tracerRegList A list of Register instances.
           @return None"""
        if self._jsonDebugFile:
            # If in debug mode read registers from the file.
            self.readAll()

        else:
           
           for tracerReg in tracerRegList:
                baseAddress = tracerReg.getAddress()
                size = 1
                access =  tracerReg.getAccess()
    
                if access == EPSolarTracer.READ:
                    rr = self._tracerClient.read_input_registers(baseAddress, size, unit=1)
        
                elif access == EPSolarTracer.READ_WRITE:
                    rr = self._tracerClient.read_holding_registers(baseAddress, size, unit=1)
        
                elif access == EPSolarTracer.COIL_READ_WRITE:
                    rr = self._tracerClient.read_coils(baseAddress, size, unit=1)
        
                elif access == EPSolarTracer.DISCRETE_READ:
                    rr = self._tracerClient.read_discrete_inputs(baseAddress, size, unit=1)
        
                for index in range(0, size):
                    regAddress = (baseAddress + index)
                    if tracerReg.getAccess() == EPSolarTracer.COIL_READ_WRITE:
                        value = rr.getBit(regAddress)
                        
                    elif tracerReg.getAccess() == EPSolarTracer.DISCRETE_READ:
                        value = rr.getBit(0)

                    else:
                        value = rr.getRegister(index)

                    self._addrKeyTracerRegDict[regAddress].setRawValue(value)
                    tracerReg.setRawValue(value)
                    
                #Update the value of a register from its raw value
                tracerReg.process()
    
    def writeRegList(self, registerList):
        """@brief Write the state of a register.
           @param registerList A list of registers to write to. The rawValue in the register
                               is the value that will be written.
           @param value The value to be written."""
        for register in registerList:

            if register.getAccess() == COILS_READ_WRITE:
                self._tracerClient.write_coil( register.getAddress(), register.getRawValue() )
    
            elif register.getAccess() == READ_WRITE:
                self._tracerClient.write_register(register.getAddress(), register.getRawValue())
                                
            else:
                raise Exception("{} register is not writeable.".format(register.getAddress()))
        
    def readAllRegs(self):
        """@brief Read all registers from the EPSolar Tracer unit."""
        # If in debug mode read the register data from a json file
        if self._jsonDebugFile:

            if os.path.isfile(self._jsonDebugFile):
                 fd = open(self._jsonDebugFile, 'r')
                 fileContents = fd.read()
                 fd.close()
                 self._addrKeyTracerRegDict = json.loads( fileContents )

            else:
                raise Exception("{} file not found.".format(self._jsonDebugFile))

        else:

            #Read data from an EPSolar Tracer unit connected to the serial port.
            regSets = list( EPSolarTracer.REG_SETS.keys() )
            regSets.sort()
            for regSet in regSets:
                baseAddress = EPSolarTracer.REG_SETS[regSet]["start"]
                size = EPSolarTracer.REG_SETS[regSet]["size"]
                access =  EPSolarTracer.REG_SETS[regSet]["access"]
                        
                if access == EPSolarTracer.READ:
                    rr = self._tracerClient.read_input_registers(baseAddress, size, unit=1)

                elif access == EPSolarTracer.READ_WRITE:
                    rr = self._tracerClient.read_holding_registers(baseAddress, size, unit=1)

                elif access == EPSolarTracer.COIL_READ_WRITE:
                    rr = self._tracerClient.read_coils(baseAddress, size, unit=1)

                elif access == EPSolarTracer.DISCRETE_READ:
                    rr = self._tracerClient.read_discrete_inputs(baseAddress, size, unit=1)

                for index in range(0, size):
                    regAddress = (baseAddress + index)
                    if EPSolarTracer.REG_SETS[regSet]["access"] == EPSolarTracer.COIL_READ_WRITE:
                        value = rr.getBit(regAddress)
                        
                    elif EPSolarTracer.REG_SETS[regSet]["access"] == EPSolarTracer.DISCRETE_READ:
                        value = rr.getBit(0)

                    else:
                        value = rr.getRegister(index)
                        
                    self._addrKeyTracerRegDict[regAddress].setRawValue( value )
                    
            #Update the value of a register from its raw value
            for addr in self._addrKeyTracerRegDict:
                self._addrKeyTracerRegDict[addr].process()

    def getJSON(self):
        """@brief Get the reg dict in JSON format."""
        dictList = []
        for key in TRACER_REG_DICT:
            dictList.append(TRACER_REG_DICT[key].toDict())
        return json.dumps(dictList, indent=4, sort_keys=True)
    
    def setJSON(self, jsonStr):
        """@brief Set the Register state from a JSON str.
           @param jsonStr The JSON str."""
        theDict = json.loads(jsonStr)
        for regDict in theDict:
            reg = Register(None, None, None, None, None)
            reg.fromDict(regDict)
            TRACER_REG_DICT[regDict[Register.REG_NAME]] = reg
        self._createAddrIndexDict()
        
    def writeReg(self, register, value):
        """@brief Write the state of a register.
           @param register The register to write to.
           @param value The value to be written. This is not the raw value of the register but the unit value."""
        register.setValue(value)
        self.writeRegList( (register,) )
        
    def readReg(self, address):
        """@brief Read a single register.
           @param address The address of the register."""
        if address not in self._addrKeyTracerRegDict:
            raise Exception("0x{:04x}/{} is an invalid register address.".format(address, address))

        register = self._addrKeyTracerRegDict[address]
        self.readRegList( (register,) )
        return register.getValue()
    
    def getRegister(self, address):
        """@brief Get the register instance given the register address.
           @param address The address of the register."""
        if address not in self._addrKeyTracerRegDict:
            raise Exception("0x{:04x}/{} is an invalid register address.".format(address, address))

        return self._addrKeyTracerRegDict[address]
    
    def isValidAddress(self, address):
        """@brief Check if an address is valid
           @param address The register address to check
           @return True if the address is a valid register address."""
        addrList = list(self._addrKeyTracerRegDict)
        validAddr = False
        if address in addrList:
            validAddr = True
        return validAddr
    
    def getRegisterByName(self, name):
        """@brief Get a single register instance.
           @param name The register name.
           @return The Regitser instance."""
        if name not in TRACER_REG_DICT:
            raise Exception("{} is an unknown register name.".format(name))

        return TRACER_REG_DICT[name]
        
    def getChargeStatus(self):
        """@brief Get the string indicating the tracer battery charge state.
                  The CHARGING_EQUIPMENT_STATUS register must be updated (read 
                  from the unit) before this method is called."""
        
        chargeStatusReg = TRACER_REG_DICT[CHARGING_EQUIPMENT_STATUS]
        chargeStatus = (int(chargeStatusReg.getValue())>>2)&0x03
        
        chargeStatusStr=EPSolarTracer.CHARGE_STATE_UNKNOWN

        if chargeStatus == 0:
            chargeStatusStr = EPSolarTracer.CHARGE_STATE_NOT_CHARGING

        elif chargeStatus == 1:
            chargeStatusStr = EPSolarTracer.CHARGE_STATE_FLOAT

        elif chargeStatus == 2:
            chargeStatusStr = EPSolarTracer.CHARGE_STATE_BOOST

        elif chargeStatus == 3:
            chargeStatusStr = EPSolarTracer.CHARGE_STATE_EQUALISATION
            
        return chargeStatusStr
    
    
# Unit types
UNDEFINED_UNIT_TYPE = "UNDEFINED"
VOLTS = "V"
AMPS  = "A"
WATTS = "W"
CELSIUS = "C"
KWH = "KWH"
TON = "TON"
AH  = "AH"
MV_C_2V = "MV_C_2V"
MILLIOHM = "milliohm"
MIN = "Min"
SECOND = "second"
MINUTE = "minute"
HOUR = "hour"
PERCENTAGE = "%"

READ_WRITE = EPSolarTracer.READ_WRITE
READ = EPSolarTracer.READ
COILS_READ_WRITE = EPSolarTracer.COIL_READ_WRITE
DISCRETE_READ = EPSolarTracer.DISCRETE_READ


# The following is a list of keys of the TracerregDict. They are taken from the
# 1733_modbus_protocol.pdf document.

# Read registers
CHARGING_EQUIPMENT_RATED_INPUT_VOLTAGE               = "Charging equipment rated input voltage"
CHARGING_EQUIPMENT_RATED_INPUT_CURRENT               = "Charging equipment rated input current"
CHARGING_EQUIPMENT_RATED_INPUT_POWER                 = "Charging equipment rated input power"
CHARGING_EQUIPMENT_RATED_INPUT_POWER_L               = "Charging equipment rated input power L"
CHARGING_EQUIPMENT_RATED_INPUT_POWER_H               = "Charging equipment rated input power H"
CHARGING_EQUIPMENT_RATED_OUTPUT_VOLTAGE              = "Charging equipment rated output voltage"
CHARGING_EQUIPMENT_RATED_OUTPUT_CURRENT              = "Charging equipment rated output current"
CHARGING_EQUIPMENT_RATED_OUTPUT_POWER_L              = "Charging equipment rated output power L"
CHARGING_EQUIPMENT_RATED_OUTPUT_POWER_H              = "Charging equipment rated output power H"
CHARGING_MODE                                        = "Charging mode"
RATED_OUTPUT_CURRENT_OF_LOAD                         = "Rated output current of load"
CHARGING_EQUIPMENT_INPUT_VOLTAGE                     = "Charging equipment input voltage"
CHARGING_EQUIPMENT_INPUT_CURRENT                     = "Charging equipment input current"
CHARGING_EQUIPMENT_INPUT_POWER_L                     = "Charging equipment input power L"
CHARGING_EQUIPMENT_INPUT_POWER_H                     = "Charging equipment input power H"
CHARGING_EQUIPMENT_OUTPUT_VOLTAGE                    = "Charging equipment output voltage"
CHARGING_EQUIPMENT_OUTPUT_CURRENT                    = "Charging equipment output current"
CHARGING_EQUIPMENT_OUTPUT_POWER_L                    = "Charging equipment output power L"
CHARGING_EQUIPMENT_OUTPUT_POWER_H                    = "Charging equipment output power H"
DISCHARGING_EQUIPMENT_OUTPUT_VOLTAGE                 = "Discharging equipment output voltage"
DISCHARGING_EQUIPMENT_OUTPUT_CURRENT                 = "Discharging equipment output current"
DISCHARGING_EQUIPMENT_OUTPUT_POWER_L                 = "Discharging equipment output power L"
DISCHARGING_EQUIPMENT_OUTPUT_POWER_H                 = "Discharging equipment output power H"
BATTERY_TEMPERATURE                                  = "Battery Temperature"
TEMPERATURE_INSIDE_EQUIPMENT                         = "Temperature inside equipment"
POWER_COMPONENTS_TEMPERATURE                         = "Power components temperature"
BATTERY_SOC                                          = "Battery SOC"
REMOTE_BATTERY_TEMPERATURE                           = "Remote battery temperature"
BATTERYS_REAL_RATED_POWER                            = "Battery's real rated power"
BATTERY_STATUS                                       = "Battery status"
CHARGING_EQUIPMENT_STATUS                            = "Charging equipment status"
MAXIMUM_INPUT_VOLT_PV_TODAY                          = "Maximum input volt (PV) today"
MINIMUM_INPUT_VOLT_PV_TODAY                          = "Minimum input volt (PV) today"
MAXIMUM_BATTERY_VOLT_TODAY                           = "Maximum battery volt today"
MINIMUM_BATTERY_VOLT_TODAY                           = "Minimum battery volt today"
CONSUMED_ENERGY_TODAY_L                              = "Consumed energy today L"
CONSUMED_ENERGY_TODAY_H                              = "Consumed energy today H"
CONSUMED_ENERGY_THIS_MONTH_L                         = "Consumed energy this month L"
CONSUMED_ENERGY_THIS_MONTH_H                         = "Consumed energy this month H"
CONSUMED_ENERGY_THIS_YEAR_L                          = "Consumed energy this year L"
CONSUMED_ENERGY_THIS_YEAR_H                          = "Consumed energy this year H"
TOTAL_CONSUMED_ENERGY_L                              = "Total consumed energy L"
TOTAL_CONSUMED_ENERGY_H                              = "Total consumed energy H"
GENERATED_ENERGY_TODAY_L                             = "Generated energy today L"
GENERATED_ENERGY_TODAY_H                             = "Generated energy today H"
GENERATED_ENERGY_THIS_MONTH_L                        = "Generated energy this month L"
GENERATED_ENERGY_THIS_MONTH_H                        = "Generated energy this month H"
GENERATED_ENERGY_THIS_YEAR_L                         = "Generated energy this year L"
GENERATED_ENERGY_THIS_YEAR_H                         = "Generated energy this year H"
TOTAL_GENERATED_ENERGY_L                             = "Total generated energy L"
TOTAL_GENERATED_ENERGY_H                             = "Total generated energy H"
CARBON_DIOXIDE_REDUCTION_L                           = "Carbon dioxide reduction L"
CARBON_DIOXIDE_REDUCTION_H                           = "Carbon dioxide reduction H"
BATTERY_CURRENT_L                                    = "Battery Current L"
BATTERY_CURRENT_H                                    = "Battery Current H"
BATTERY_TEMP                                         = "Battery Temp"
AMBIENT_TEMP                                         = "Ambient Temp"
HIGH_VOLT_DISCONNECT                                 = "High Volt.disconnect"
CHARGING_LIMIT_VOLTAGE                               = "Charging limit voltage"
OVER_VOLTAGE_RECONNECT                               = "Over voltage reconnect"
EQUALIZATION_VOLTAGE                                 = "Equalization voltage"
BOOST_VOLTAGE                                        = "Boost voltage"
FLOAT_VOLTAGE                                        = "Float voltage"
BOOST_RECONNECT_VOLTAGE                              = "Boost reconnect voltage"

# Write registers
BATTERY_TYPE                                         = "Battery Type"
BATTERY_CAPACITY                                     = "Battery Capacity"
TEMPERATURE_COMPENSATION_COEFFICIENT                 = "Temperature compensation coefficient"
LOW_VOLTAGE_RECONNECT                                = "Low voltage reconnect"
UNDER_VOLTAGE_RECOVER                                = "Under voltage recover"
UNDER_VOLTAGE_WARNING                                = "Under voltage warning"
LOW_VOLTAGE_DISCONNECT                               = "Low voltage disconnect"
DISCHARGING_LIMIT_VOLTAGE                            = "Discharging limit voltage"
REAL_TIME_CLOCK_A                                    = "Real time clock A"
REAL_TIME_CLOCK_B                                    = "Real time clock B"
REAL_TIME_CLOCK_C                                    = "Real time clock C"
EQUALIZATION_CHARGING_CYCLE                          = "Equalization charging cycle"
BATTERY_TEMPERATURE_WARNING_UPPER_LIMIT              = "Battery temperature warning upper limit"
BATTERY_TEMPERATURE_WARNING_LOWER_LIMIT              = "Battery temperature warning lower limit"
CONTROLLER_INNER_TEMPERATURE_UPPER_LIMIT             = "Controller inner temperature upper limit"
CONTROLLER_INNER_TEMPERATURE_UPPER_LIMIT_RECOVER     = "Controller inner temperature upper limit recover"
POWER_COMPONENT_TEMPERATURE_UPPER_LIMIT              = "Power component temperature upper limit"
POWER_COMPONENT_TEMPERATURE_UPPER_LIMIT_RECOVER      = "Power component temperature upper limit recover"
LINE_IMPEDANCE                                       = "Line Impedance"
NIGHT_TIMETHRESHOLD_VOLT_NTTV                        = "Night TimeThreshold Volt.(NTTV)"
LIGHT_SIGNAL_STARTUP_NIGHT_DELAY_TIME                = "Light signal startup (night) delay time"
DAY_TIME_THRESHOLD_VOLT_DTTV                         = "Day Time Threshold Volt.(DTTV)"
LIGHT_SIGNAL_TURN_OFF_DAY_DELAY_TIME                 = "Light signal turn off(day) delay time"
LOAD_CONTROLING_MODES                                = "Load controlling modes"
WORKING_TIME_LENGTH_1                                = "Working time length 1"
WORKING_TIME_LENGTH_2                                = "Working time length 2"
TURN_ON_TIMING_1_SEC                                 = "Turn on timing 1_SEC"
TURN_ON_TIMING_1_MIN                                 = "Turn on timing 1_MIN"
TURN_ON_TIMING_1_HOUR                                = "Turn on timing 1_HOUR"
TURN_OFF_TIMING_1_SEC                                = "Turn off timing 1_SEC"
TURN_OFF_TIMING_1_MIN                                = "Turn off timing 1_MIN"
TURN_OFF_TIMING_1_HOUR                               = "Turn off timing 1_HOUR"
TURN_ON_TIMING_2_SEC                                 = "Turn on timing 2_SEC"
TURN_ON_TIMING_2_MIN                                 = "Turn on timing 2_MIN"
TURN_ON_TIMING_2_HOUR                                = "Turn on timing 2_HOUR"
TURN_OFF_TIMING_2_SEC                                = "Turn off timing 2_SEC"
TURN_OFF_TIMING_2_MIN                                = "Turn off timing 2_MIN"
TURN_OFF_TIMING_2_HOUR                               = "Turn off timing 2_HOUR"
LENGTH_OF_NIGHT                                      = "Length of night"
BATTERY_RATED_VOLTAGE_CODE                           = "Battery rated voltage code"
LOAD_TIMING_CONTROL_SELECTION                        = "Load timing control selection"
DEFAULT_LOAD_ON_OFF_IN_MANUAL_MODE                   = "Default Load On/Off in manual mode"
EQUALIZE_DURATION                                    = "Equalize duration"
BOOST_DURATION                                       = "Boost duration"
DISCHARGING_PERCENTAGE                               = "Discharging percentage"
CHARGING_PERCENTAGE                                  = "Charging percentage"
MANAGEMENT_MODES_OF_BATTERY_CHARGING_AND_DISCHARGING = "Management modes of battery charging and discharging"

# Coils(read-write
MANUAL_CONTROL_THE_LOAD                              = "Manual control the load"
ENABLE_LOAD_TEST_MODE                                = "Enable load test mode"
FORCE_THE_LOAD_ON_OFF                                = "Force the load on/off"

# Discrete input（read-only)
OVER_TEMPERATURE_INSIDE_THE_DEVICE                   = "Over temperature inside the device"
DAY_NIGHT                                            = "Day/Night"


class Register(object):
    """@brief Defines an EPsolar Tracer register"""
    ADDRESS = "_address"
    DESCRIPTIONS_LINES = "_descriptionLines"
    UNIT = "_unit"
    MULTIPLIER = "_multiplier"
    ACCESS = "_access"
    RAW_REG_VALUE = "_rawRegValue"
    VALUE = "_value"
    REG_NAME = "_regName"
    LSW_REG_NAME = "_lswRegName"
    REG_BIT_COUNT = 16
    
    def __init__(self, address, descriptionLines, unit, multiplier, access, lswRegName=None):
        """@brief Constructor
           @param address The register address
           @param descriptionLines Lins of text describing the register
           @param unit The unit that the register value holds.
           @param multiplier The multiplier of the 16 bit reg value.
           @param access The access level (READ, READ_WRITE COILS_READ_WRITE or DISCRETE_READ).
           @param lswRegName If the register value is a combination of two registers then
                                     this holds the name of the register that holds the lower 16 bits.
                                     If the register value is a single 16 bit register then this is None.""" 
            
        self._address = address
        self._descriptionLines = descriptionLines
        self._unit = unit
        self._multiplier = multiplier
        self._access = access
        
        self._rawRegValue = None
        self._value = None
        self._regName = None
        self._lswRegName = lswRegName
        
    def toDict(self):
        """@brief Convert the Register to a dict.
           @return The dict instance."""
        theDict = {}
        theDict[Register.ADDRESS] = self._address
        theDict[Register.DESCRIPTIONS_LINES] = self._descriptionLines
        theDict[Register.UNIT] = self._unit
        theDict[Register.MULTIPLIER] = self._multiplier
        theDict[Register.ACCESS] = self._access
        theDict[Register.RAW_REG_VALUE] = self._rawRegValue
        theDict[Register.VALUE] = self._value
        theDict[Register.REG_NAME] = self._regName
        theDict[Register.LSW_REG_NAME] = self._lswRegName
        return theDict
        
    def fromDict(self, theDict):
        """@brief Set the Register state from theDict.
           @param theDict The dict that holds the Register state."""
        self._address = theDict[Register.ADDRESS]
        self._descriptionLines = theDict[Register.DESCRIPTIONS_LINES]
        self._unit = theDict[Register.UNIT]
        self._multiplier = theDict[Register.MULTIPLIER]
        self._access = theDict[Register.ACCESS]
        self._rawRegValue = theDict[Register.RAW_REG_VALUE]
        self._value = theDict[Register.VALUE]
        self._regName = theDict[Register.REG_NAME]
        self._lswRegName = theDict[Register.LSW_REG_NAME]
           
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4, sort_keys=True)
    
    def getAddress(self):
        """@return The Address of this register."""
        return self._address
    
    def getDescriptionLine(self):
        """@return A list of description lines for this register."""
        return self._descriptionLines
    
    def getUnit(self):
        """@return The unit type of this register."""
        return self._unit
    
    def getMultiplier(self):
        """@return The multiplier value for this register.""" 
        return self._multiplier
    
    def getAccess(self):
        """@return Get the access of this register"""
        return self._access
    
    def getRawValue(self):
        """@return Get raw 16 bit register value."""
        return self._rawRegValue

    def getValue(self):
        """@return Get the unit value."""
        return self._value
        
    def getRegName(self):
        """@return Get the name of this register."""
        return self._regName
    
    def setRawValue(self, rawValue):
        """@brief Set the raw 16 bit register value.
                  This also updates the register value.
           @param rawValue The 16 bit register value."""
        self._rawRegValue = int(rawValue)
        
    def setValue(self, value):
        """@brief Set the register value. This is not the raw register value but the unit value.
                  The raw register value is also updated. This is the value * the multiplier.
                  This can only be called for writable registers.
           @param value The value to be written."""
        if self._access == READ_WRITE or self._access == COILS_READ_WRITE:
            if value < 0:
                raise Exception("{} is less than 0 (min)".format(value))
    
            rawRegValue = value * self._multiplier
            maxRegValue = 2E16
            if rawRegValue > maxRegValue:
                raise Exception("{} is greater than the max of {}".format(rawRegValue, maxRegValue))
    
            self._value = int(value)
            self._rawRegValue = int(rawRegValue)

        else:
            raise Exception("setValue() cannot be called as the '{}' register is not a writeable register. ".format(self._regName))

    def process(self):
        """@brief Process the raw register value."""
        #If we have an associated register containing the lower 16 bits
        if self._lswRegName:
            #create a composite value
            rawValue = float(TRACER_REG_DICT[self._lswRegName].getRawValue() | (self._rawRegValue << 16) )
            if rawValue > 0.0 or rawValue < 0.0:
                self._value = float(rawValue / self._multiplier)
            else:
                self._value = 0
        else:
            if self._unit == CELSIUS:
                #The only unit type that uses 2's compliment
                rawValue = self._rawRegValue
                if (rawValue & (1 << (Register.REG_BIT_COUNT - 1))) != 0:
                    rawValue = rawValue - (1 << Register.REG_BIT_COUNT)   
                if rawValue == 0:
                    self._value = 0
                else:
                    self._value = float(rawValue / self._multiplier)
            else:       
                rawValue = float(self._rawRegValue)
                if rawValue > 0.0 or rawValue < 0.0:
                    self._value =  float(rawValue / self._multiplier)
                else:
                    self._value = 0
        
    def setRegName(self, regName):
        """@brief Set the register name.
           @param regName The name of the register."""
        self._regName = regName
        
    def getLines(self):
        """@brief represent the instance as a string"""
        lines = []
        lines.append("----------------------------------------------------------")
        lines.append("self._address          = 0x{:04x}/{}".format(self._address, self._address) )
        lines.append("self._regName          = {}".format(self._regName) )
        lines.append("self._descriptionLines = {}".format(self._descriptionLines) )
        lines.append("self._unit             = {}".format(self._unit) )
        lines.append("self._multiplier       = {}".format(self._multiplier) )
        lines.append("self._access           = {}".format(self._access) )
        lines.append("self._rawRegValue      = {}".format(self._rawRegValue) )
        lines.append("self._value            = {}".format(self._value) )
        lines.append("self._lswRegName       = {}".format(self._lswRegName) )
        return lines
    
    def __str__(self):
        lines = self.getLines()
        return "\n".join(lines)
        

TRACER_REG_DICT = {

# Rated data (read only) input registers
CHARGING_EQUIPMENT_RATED_INPUT_VOLTAGE:                 Register(0x3000, ("PV array rated voltage",), VOLTS, 100, READ),
CHARGING_EQUIPMENT_RATED_INPUT_CURRENT:                 Register(0x3001, ("PV array rated current",), AMPS,  100, READ),
CHARGING_EQUIPMENT_RATED_INPUT_POWER_L:                 Register(0x3002, ("PV array rated power (low 16 bits)",), WATTS, 100, READ),
CHARGING_EQUIPMENT_RATED_INPUT_POWER_H:                 Register(0x3003, ("PV array rated power (high 16 bits)",), WATTS, 100, READ, lswRegName=CHARGING_EQUIPMENT_RATED_INPUT_POWER_L),
CHARGING_EQUIPMENT_RATED_OUTPUT_VOLTAGE:                Register(0x3004, ("Battery's voltage",), VOLTS, 100, READ),
CHARGING_EQUIPMENT_RATED_OUTPUT_CURRENT:                Register(0x3005, ("Rated charging current to battery",), AMPS, 100, READ),
CHARGING_EQUIPMENT_RATED_OUTPUT_POWER_L:                Register(0x3006, ("Rated charging power to battery (low 16 bits)",), WATTS, 100, READ),
CHARGING_EQUIPMENT_RATED_OUTPUT_POWER_H:                Register(0x3007, ("Rated charging power to battery (high 16 bits)",), WATTS, 100, READ, lswRegName=CHARGING_EQUIPMENT_RATED_OUTPUT_POWER_L),
CHARGING_MODE:                                          Register(0x3008, ("0001H-PWM",), UNDEFINED_UNIT_TYPE, 1 , READ),
RATED_OUTPUT_CURRENT_OF_LOAD:                           Register(0X300E, ("",), AMPS, 100, READ),

# Real-time data/status (read only) input registers
CHARGING_EQUIPMENT_INPUT_VOLTAGE:                       Register(0x3100, ("Solar charge controller--PV array voltage"), VOLTS, 100, READ),
CHARGING_EQUIPMENT_INPUT_CURRENT:                       Register(0x3101, ("Solar charge controller--PV array current"), AMPS, 100, READ),
CHARGING_EQUIPMENT_INPUT_POWER_L:                       Register(0x3102, ("Solar charge controller--PV array power (low 16 bits)",), WATTS, 100, READ),
CHARGING_EQUIPMENT_INPUT_POWER_H:                       Register(0x3103, ("Solar charge controller--PV array power (high 16 bits)",), WATTS, 100, READ, lswRegName=CHARGING_EQUIPMENT_INPUT_POWER_L),
CHARGING_EQUIPMENT_OUTPUT_VOLTAGE:                      Register(0x3104, ("Battery voltage",), VOLTS, 100, READ),
CHARGING_EQUIPMENT_OUTPUT_CURRENT:                      Register(0x3105, ("Battery charging current",), AMPS, 100, READ),
CHARGING_EQUIPMENT_OUTPUT_POWER_L:                      Register(0x3106, ("Battery charging power (low 16 bits)"), WATTS, 100, READ),
CHARGING_EQUIPMENT_OUTPUT_POWER_H:                      Register(0x3107, ("Battery charging power (high 16 bits)",), WATTS, 100, READ, lswRegName=CHARGING_EQUIPMENT_OUTPUT_POWER_L),
DISCHARGING_EQUIPMENT_OUTPUT_VOLTAGE:                   Register(0x310c, ("Load voltage",), VOLTS, 100, READ),
DISCHARGING_EQUIPMENT_OUTPUT_CURRENT:                   Register(0x310d, ("Load current",), AMPS, 100, READ),
DISCHARGING_EQUIPMENT_OUTPUT_POWER_L:                   Register(0x310E, ("Load power (low 16 bits)",), WATTS, 100, READ),
DISCHARGING_EQUIPMENT_OUTPUT_POWER_H:                   Register(0x310F, ("Load power (high 16 bits)",), WATTS, 100, READ, lswRegName=DISCHARGING_EQUIPMENT_OUTPUT_POWER_L),
BATTERY_TEMPERATURE:                                    Register(0x3110, ("Battery Temperature",), CELSIUS, 100, READ),
TEMPERATURE_INSIDE_EQUIPMENT:                           Register(0x3111, ("Temperature inside case",), CELSIUS, 100, READ),
POWER_COMPONENTS_TEMPERATURE:                           Register(0x3112, ("Heat sink surface temperature of equipments power components",), CELSIUS, 100, READ),
BATTERY_SOC:                                            Register(0x311a, ("The percentage of battery's remaining capacity",), UNDEFINED_UNIT_TYPE, 100, READ),
REMOTE_BATTERY_TEMPERATURE:                             Register(0x311b, ("The battery tempeture measured by remote temperature sensor",), CELSIUS, 100, READ),
BATTERYS_REAL_RATED_POWER:                              Register(0x311d, ("Current system rated votlage. 1200, 2400 represent 12V, 24V",), VOLTS, 100, READ),
BATTERY_STATUS:                                         Register(0x3200, ("D3-D0: 01H Overvolt , 00H Normal , 02H Under",\
                                                                  "Volt, 03H Low Volt Disconnect, 04H Fault",\
                                                                  "D7-D4: 00H Normal, 01H Over Temp.(Higher",\
                                                                  "than the warning settings), 02H Low Temp.(",\
                                                                  "Lower than the warning settings),",\
                                                                  "D8: Battery inerternal resistance abnormal 1,",\
                                                                  "normal 0",\
                                                                  "D15: 1-Wrong identification for rated voltage"), UNDEFINED_UNIT_TYPE, 1, READ),
CHARGING_EQUIPMENT_STATUS:                              Register(0x3201, ("D15-D14: Input volt status. 00 normal, 01 no",\
                                                                  "power connected, 02H Higher volt input, 03H",\
                                                                  "Input volt error.",\
                                                                  "D13: Charging MOSFET is short.",\
                                                                  "D12: Charging or Anti-reverse MOSFET is short.",\
                                                                  "D11: Anti-reverse MOSFET is short.",\
                                                                  "D10: Input is over current.",\
                                                                  "D9: The load is Over current.",\
                                                                  "D8: The load is short.",\
                                                                  "D7: Load MOSFET is short.",\
                                                                  "D4: PV Input is short.",\
                                                                  "D3-2: Charging status. 00 No charging,01 Float,02",\
                                                                  "Boost,03 Equlization.",\
                                                                  "D1: 0 Normal, 1 Fault.",\
                                                                  "D0: 1 Running, 0 Standby.",), UNDEFINED_UNIT_TYPE, 1, READ),

# Statistical parameter（read only）input registers
MAXIMUM_INPUT_VOLT_PV_TODAY:                            Register(0x3300, ("00: 00 Refresh every day",), VOLTS, 100, READ),
MINIMUM_INPUT_VOLT_PV_TODAY:                            Register(0x3301, ("00: 00 Refresh every day",), VOLTS, 100, READ),
MAXIMUM_BATTERY_VOLT_TODAY:                             Register(0x3302, ("00: 00 Refresh every day",), VOLTS, 100, READ),
MINIMUM_BATTERY_VOLT_TODAY:                             Register(0x3303, ("00: 00 Refresh every day",), VOLTS, 100, READ),
CONSUMED_ENERGY_TODAY_L:                                Register(0x3304, ("00: 00 Clear every day (low 16 bits ",), KWH, 100, READ),
CONSUMED_ENERGY_TODAY_H:                                Register(0x3305, ("00: 00 Clear every day (high 16 bits)",), KWH, 100, READ, lswRegName=CONSUMED_ENERGY_TODAY_L),
CONSUMED_ENERGY_THIS_MONTH_L:                           Register(0x3306, ("00: 00 Clear on the first day of month (low 16 bits)",), KWH, 100, READ),
CONSUMED_ENERGY_THIS_MONTH_H:                           Register(0x3307, ("00: 00 Clear on the first day of month (high 16 bits)",), KWH, 100, READ, lswRegName=CONSUMED_ENERGY_THIS_MONTH_L),
CONSUMED_ENERGY_THIS_YEAR_L:                            Register(0x3308, ("00: 00 Clear on 1, Jan (low 16 bits)",), KWH, 100, READ),
CONSUMED_ENERGY_THIS_YEAR_H:                            Register(0x3309, ("00: 00 Clear on 1, Jan (high 16 bits)",), KWH, 100, READ, lswRegName=CONSUMED_ENERGY_THIS_YEAR_L),
TOTAL_CONSUMED_ENERGY_L:                                Register(0x330a, ("(low 16 bits)",), KWH, 100, READ, lswRegName=TOTAL_CONSUMED_ENERGY_H),
TOTAL_CONSUMED_ENERGY_H:                                Register(0x330b, ("(high 16 bits)",), KWH, 100, READ),
GENERATED_ENERGY_TODAY_L:                               Register(0x330c, ("00: 00 Clear every day (low 16 bits)",), KWH, 100, READ),
GENERATED_ENERGY_TODAY_H:                               Register(0x330d, ("(high 16 bits)",), KWH, 100, READ, lswRegName=GENERATED_ENERGY_TODAY_L),
GENERATED_ENERGY_THIS_MONTH_L:                          Register(0x330e, ("00: 00 Clear on the first day of month (low 16 bits)",), KWH, 100, READ),
GENERATED_ENERGY_THIS_MONTH_H:                          Register(0x330f, ("(high 16 bits)",), KWH, 100, READ, lswRegName=GENERATED_ENERGY_THIS_MONTH_L),
GENERATED_ENERGY_THIS_YEAR_L:                           Register(0x3310, ("00: 00 Clear on 1, Jan (low 16 bits)",), KWH, 100, READ),
GENERATED_ENERGY_THIS_YEAR_H:                           Register(0x3311, ("(high 16 bits)",), KWH, 100, READ, lswRegName=GENERATED_ENERGY_THIS_YEAR_L),
TOTAL_GENERATED_ENERGY_L:                               Register(0x3312, ("(low 16 bits)",), KWH, 100, READ),
TOTAL_GENERATED_ENERGY_H:                               Register(0x3313, ("(high 16 bits)",), KWH, 100, READ, lswRegName=TOTAL_GENERATED_ENERGY_L),
CARBON_DIOXIDE_REDUCTION_L:                             Register(0x3314, ("Saving 1 Kilowatt=Reduction 0.997KG (Carbon dioxide) = Reduction 0.272KG (Carton) (low 16 bits)",), TON, 100, READ),
CARBON_DIOXIDE_REDUCTION_H:                             Register(0x3315, ("(high 16 bits)",), TON, 100, READ, lswRegName=CARBON_DIOXIDE_REDUCTION_L),
BATTERY_CURRENT_L:                                      Register(0x331b, ("The net battery current,charging current minus the discharging one.",
                                                                  "The positive value represents A charging and negative, discharging (low 16 bits).",), AMPS, 100, READ),
BATTERY_CURRENT_H:                                      Register(0x331c, ("(high 16 bits)",), AMPS, 100, READ, lswRegName=BATTERY_CURRENT_L),
BATTERY_TEMP:                                           Register(0x331d, ("Battery Temp.",), CELSIUS, 100, READ),
AMBIENT_TEMP:                                           Register(0x331e, ("Ambient Temp.",), CELSIUS, 100, READ),

# Setting Parameter （read-write）holding register
BATTERY_TYPE:                                           Register(0x9000, ("0001H- Sealed",\
                                                                  "0002H- GEL",\
                                                                  "0003H- Flooded",\
                                                                  "0000H- User defined",), UNDEFINED_UNIT_TYPE, 1, READ_WRITE),
BATTERY_CAPACITY:                                       Register(0x9001, ("Rated capacity of the battery. PJA: The pdf does not state the multiplier for this, 1 is a guess.",), AH, 1, READ_WRITE),
TEMPERATURE_COMPENSATION_COEFFICIENT:                   Register(0x9002, ("Range 0-9. PJA: -3 is the default value when read from the unit. This does not tie up with the range 0-9 stated in the pdf.",), MV_C_2V, 100, READ_WRITE),
HIGH_VOLT_DISCONNECT:                                   Register(0x9003, ("",), VOLTS, 100, READ_WRITE),
CHARGING_LIMIT_VOLTAGE:                                 Register(0x9004, ("",), VOLTS, 100, READ_WRITE),
OVER_VOLTAGE_RECONNECT:                                 Register(0x9005, ("",), VOLTS, 100, READ_WRITE),
EQUALIZATION_VOLTAGE:                                   Register(0x9006, ("",), VOLTS, 100, READ_WRITE),
BOOST_VOLTAGE:                                          Register(0x9007, ("",), VOLTS, 100, READ_WRITE),
FLOAT_VOLTAGE:                                          Register(0x9008, ("",), VOLTS, 100, READ_WRITE),
BOOST_RECONNECT_VOLTAGE:                                Register(0x9009, ("",), VOLTS, 100, READ_WRITE),
LOW_VOLTAGE_RECONNECT:                                  Register(0x900a, ("",), VOLTS, 100, READ_WRITE),
UNDER_VOLTAGE_RECOVER:                                  Register(0x900b, ("",), VOLTS, 100, READ_WRITE),
UNDER_VOLTAGE_WARNING:                                  Register(0x900c, ("",), VOLTS, 100, READ_WRITE),
LOW_VOLTAGE_DISCONNECT:                                 Register(0x900d, ("",), VOLTS, 100, READ_WRITE),
DISCHARGING_LIMIT_VOLTAGE:                              Register(0x900e, ("",), VOLTS, 100, READ_WRITE),
REAL_TIME_CLOCK_A:                                      Register(0x9013, ("D7-0 Sec",
                                                                  "D15-8 Min",
                                                                  "(Year,Month,Day,Min,Sec.should be written simultaneously)",), UNDEFINED_UNIT_TYPE, 1, READ_WRITE),
REAL_TIME_CLOCK_B:                                      Register(0x9014, ("D7-0 Hour",
                                                                  "D15-8 Day",), UNDEFINED_UNIT_TYPE, 1, READ_WRITE),
REAL_TIME_CLOCK_C:                                      Register(0x9015, ("D7-0 Month",
                                                                  "D15-8 Year",), UNDEFINED_UNIT_TYPE, 1, READ_WRITE),
EQUALIZATION_CHARGING_CYCLE:                            Register(0x9016, ("Interval days of auto equalisation charging in cycle",), UNDEFINED_UNIT_TYPE, 1, READ_WRITE),
BATTERY_TEMPERATURE_WARNING_UPPER_LIMIT:                Register(0x9017, ("",), CELSIUS, 100, READ_WRITE),
BATTERY_TEMPERATURE_WARNING_LOWER_LIMIT:                Register(0x9018, ("",), CELSIUS, 100, READ_WRITE),
CONTROLLER_INNER_TEMPERATURE_UPPER_LIMIT:               Register(0x9019, ("",), CELSIUS, 100, READ_WRITE),
CONTROLLER_INNER_TEMPERATURE_UPPER_LIMIT_RECOVER:       Register(0x901a, ("After Over Temperature, system recover once it drop to lower than this value",), CELSIUS, 100, READ_WRITE),
POWER_COMPONENT_TEMPERATURE_UPPER_LIMIT:                Register(0x901b, ("Warning when surface temperature of power components higher than this value, and charging and discharging stop.",), CELSIUS, 100, READ_WRITE),
POWER_COMPONENT_TEMPERATURE_UPPER_LIMIT_RECOVER:        Register(0x901c, ("Recover once power components temperature lower than this value",), CELSIUS, 100, READ_WRITE),
LINE_IMPEDANCE:                                         Register(0x901d, ("The resistance of the connectted wires.",), MILLIOHM, 100, READ_WRITE),
NIGHT_TIMETHRESHOLD_VOLT_NTTV:                          Register(0x901e, ("PV lower than this value, controller would detect it as sundown",), VOLTS, 100, READ_WRITE),
LIGHT_SIGNAL_STARTUP_NIGHT_DELAY_TIME:                  Register(0x901f, ("PV voltage lower than NTTV, and duration",\
                                                                 "exceeds the Light signal startup (night) delay time",\
                                                                 "controller would detect it as night time.",), MIN, 1, READ_WRITE),
DAY_TIME_THRESHOLD_VOLT_DTTV:                           Register(0x9020, ("PV voltage higher than this value, controller would detect it as sunrise",), VOLTS, 100, READ_WRITE),
LIGHT_SIGNAL_TURN_OFF_DAY_DELAY_TIME:                   Register(0x9021, ("PV voltage higher than DTTV, and duration exceeds Light signal turn",\
                                                                  "off(day) delay time delay time, controller would detect it as daytime.",), MIN, 1, READ_WRITE),
LOAD_CONTROLING_MODES:                                  Register(0x903d, ("0000H Manual Control",\
                                                                  "0001H Light ON/OFF",\
                                                                  "0002H Light ON+ Timer/",\
                                                                  "0003H Time Control",), UNDEFINED_UNIT_TYPE, 1, READ_WRITE),
WORKING_TIME_LENGTH_1:                                  Register(0x903e, ("The length of load output timer1, D15-D8,hour, D7-D0, minute",), UNDEFINED_UNIT_TYPE, 1, READ_WRITE),
WORKING_TIME_LENGTH_2:                                  Register(0x903f, ("The length of load output timer2",\
                                                                  "D15-D8, hour",\
                                                                  "D7-D0, minute",), UNDEFINED_UNIT_TYPE, 1, READ_WRITE),
TURN_ON_TIMING_1_SEC:                                   Register(0x9042, ("",), SECOND, 1, READ_WRITE),
TURN_ON_TIMING_1_MIN:                                   Register(0x9043, ("",), MIN, 1, READ_WRITE),
TURN_ON_TIMING_1_HOUR:                                  Register(0x9044, ("",), HOUR, 1, READ_WRITE),
TURN_OFF_TIMING_1_SEC:                                  Register(0x9045, ("",), SECOND, 1, READ_WRITE),
TURN_OFF_TIMING_1_MIN:                                  Register(0x9046, ("",), MIN, 1, READ_WRITE),
TURN_OFF_TIMING_1_HOUR:                                 Register(0x9047, ("",), HOUR, 1, READ_WRITE),
TURN_ON_TIMING_2_SEC:                                   Register(0x9048, ("",), SECOND, 1, READ_WRITE),
TURN_ON_TIMING_2_MIN:                                   Register(0x9049, ("",), MIN, 1, READ_WRITE),
TURN_ON_TIMING_2_HOUR:                                  Register(0x904a, ("",), HOUR, 1, READ_WRITE),
TURN_OFF_TIMING_2_SEC:                                  Register(0x904b, ("",), SECOND, 1, READ_WRITE),
TURN_OFF_TIMING_2_MIN:                                  Register(0x904c, ("",), MIN, 1, READ_WRITE),
TURN_OFF_TIMING_2_HOUR:                                 Register(0x904d, ("",), HOUR, 1, READ_WRITE),
LENGTH_OF_NIGHT:                                        Register(0x9065, ("Set default values of the whole night length of time.",\
                                                                  "D15-D8,hour",\
                                                                  "D7-D0, minute",), UNDEFINED_UNIT_TYPE, 1, READ_WRITE),
BATTERY_RATED_VOLTAGE_CODE:                             Register(0x9067, ("0, auto recognize. 1-12V, 2-24V",), UNDEFINED_UNIT_TYPE, 1, READ_WRITE),
LOAD_TIMING_CONTROL_SELECTION:                          Register(0x9069, ("Selected timing period of the load.0, using timer 1, 1-using timer 2.",), UNDEFINED_UNIT_TYPE, 1, READ_WRITE),
DEFAULT_LOAD_ON_OFF_IN_MANUAL_MODE:                     Register(0x906a, ("0-off, 1-on",), UNDEFINED_UNIT_TYPE, 1, READ_WRITE),
EQUALIZE_DURATION:                                      Register(0x906b, ("Usually 60-120 minutes.",), MINUTE, 1, READ_WRITE),
BOOST_DURATION:                                         Register(0x906c, ("Usually 60-120 minutes.",), MINUTE, 1, READ_WRITE),
DISCHARGING_PERCENTAGE:                                 Register(0x906d, ("Usually 20%-80%. The percentage of battery's remaining capacity when stop charging",), PERCENTAGE, 1, READ_WRITE),
CHARGING_PERCENTAGE:                                    Register(0x906e, ("Depth of charge, 20%-100%.",), PERCENTAGE, 1, READ_WRITE),
MANAGEMENT_MODES_OF_BATTERY_CHARGING_AND_DISCHARGING:   Register(0x9070, ("Management modes of battery charge and discharge, voltage compensation : 0 and SOC : 1",), UNDEFINED_UNIT_TYPE, 1, READ_WRITE),
MANUAL_CONTROL_THE_LOAD:                                Register(0x2,    ("When the load is manual mode，1-manual on 0 -manual off",), UNDEFINED_UNIT_TYPE, 1, COILS_READ_WRITE),
ENABLE_LOAD_TEST_MODE:                                  Register(0x5,    ("1 Enable",\
                                                                  "0 Disable(normal)",), UNDEFINED_UNIT_TYPE, 1, COILS_READ_WRITE),
FORCE_THE_LOAD_ON_OFF:                                  Register(0x6,    ("1 Turn on",\
                                                                  "0 Turn off (used for temporary test of the load)",), UNDEFINED_UNIT_TYPE, 1, COILS_READ_WRITE),
OVER_TEMPERATURE_INSIDE_THE_DEVICE:                     Register(0x2000, ("1 The temperature inside the controller is higher than the over-temperature protection point.",\
                                                                  "0 Normal",), UNDEFINED_UNIT_TYPE, 1, DISCRETE_READ),
DAY_NIGHT:                                              Register(0x200C, ("1-Night, 0-Day",), UNDEFINED_UNIT_TYPE, 1, DISCRETE_READ)
}

