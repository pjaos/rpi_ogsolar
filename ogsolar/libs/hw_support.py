import  platform

class HWSupport(object):
    """@brief Responsible for providing helper functionality to determine if a
              hardware platform is supported."""

    AMD64_MACHINE_TYPE = "x86_64"
    RPI_MACHINE_TYPES   = ["armv6l", "armv7l"]
    
    @staticmethod
    def GetMachineType():
        """@return The machine type of the hardware platform that were running on."""
        return platform.machine()

    @staticmethod
    def IsRaspberryPI():
        """@return True if running on RaspberryPI hardware."""
        if HWSupport.GetMachineType() in HWSupport.RPI_MACHINE_TYPES:
            return True
        return False

    @staticmethod
    def GetI2CDriver():
        """@brief Get the I2c driver that implements the following methods.
                  readBytes(devAddress, regAddress, byteCount)
                  writeBytes(devAddress, regAddress, byteList)
           @return The I2C driver"""

        if HWSupport.IsRaspberryPI():
            return RPI_I2CDriver()

        else:
            return None

class I2CError(Exception):
  pass

class I2CInterface(object):
    """@brief This is a wrapper class for the python I2C interface that is
              platform specific.
              This allows the same code to be used across platforms as long as
              this class supports the platform. 
       @param simulateHardware If True then the hardware will be simulated and
                               therefore do not raise hardware unsupported errors."""

    def __init__(self, simulateHardware):
        self._driver = None

        if not simulateHardware:
            self._driver = HWSupport.GetI2CDriver()
            if not self._driver:
                raise I2CError("%s is not a supported hardware platform (I2CInterface class)." % (HWSupport.GetMachineType()) )


class RPI_I2CDriver(object):
    """@brief Implement read and write using the raspberry pi I2c bus"""

    def __init__(self, i2CBusID=1):
        """@brief Constructor
           @param i2CBusID The I2c device number (E.G 1 = /dev/i2c-1 device exists."""
        import smbus
        self._i2cBus = smbus.SMBus(i2CBusID)

    def readBytes(self, devAddr, regAddr, size):
        """@brief Read data bytes or word on i2C bus,
           @param devAddr The address of the device to access.
           @param regAddr The register address in the device.
           @param size The number of bytes to read consecutivley."""
        return self._i2cBus.read_i2c_block_data(devAddr, regAddr, size)

    def writeBytes(self, devAddr, regAddr, valueList):
        """@brief Write byte values on the I2C bus.
           @param devAddr The address of the device to access.
           @param regAddr The register address in the device.
           @param valueList A list of bytes to write"""
        self._i2cBus.write_i2c_block_data(devAddr, regAddr, valueList)
