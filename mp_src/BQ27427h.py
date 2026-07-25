"""
******************************************************************************
SparkFunBQ27427.h
BQ27427 Arduino Library Main Header File

Adapted BQ27427 Library based on SparkFun BQ27441 Arduino Library
Original Author: Jim Lindblom @ SparkFun Electronics
Original Date: May 9, 2016
Original Repo: https://github.com/sparkfun/SparkFun_BQ27441_Arduino_Library

Adapted by: Edrean Ernst
Adaptation Date: June 2025
Repository: https://github.com/edreanernst/BQ27427_Arduino_Library

Definition of the BQ27427 library, which implements all features of the
BQ27427 Battery Fuel Gauge.

This library modifies the original SparkFun BQ27441 library to support the
Texas Instruments BQ27427 fuel gauge.

Original License: MIT License
See LICENSE.txt for full license terms.
******************************************************************************
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from enum import IntEnum
else:
	IntEnum = int

from BQ27427_Definitions import *

BQ72441_I2C_TIMEOUT = const(2000)

# Chemistry profiles
class ChemistryProfile(IntEnum):
	CHEM_A = BQ27427_CONTROL_CHEM_A  # 4.35V
	CHEM_B = BQ27427_CONTROL_CHEM_B  # 4.2V
	CHEM_C = BQ27427_CONTROL_CHEM_C   # 4.4V


# Parameters for the current() function, to specify which current to read
class CurrentMeasure(IntEnum):
	AVG  = 0  # Average Current (DEFAULT)
	STBY = 1  # Standby Current
	MAX  = 2   # Max Current

# Parameters for the capacity() function, to specify which capacity to read
class CapacityMeasure(IntEnum):
	REMAIN = 0     # Remaining Capacity (DEFAULT)
	FULL = 1       # Full Capacity
	AVAIL = 2      # Available Capacity
	AVAIL_FULL = 3 # Full Available Capacity
	REMAIN_F = 4   # Remaining Capacity Filtered
	REMAIN_UF = 5  # Remaining Capacity Unfiltered
	FULL_F = 6     # Full Capacity Filtered
	FULL_UF = 7    # Full Capacity Unfiltered
	DESIGN = 8      # Design Capacity

# Parameters for the soc() function
class SocMeasure(IntEnum):
	FILTERED = 0  # State of Charge Filtered (DEFAULT)
	UNFILTERED = 1 # State of Charge Unfiltered

# Parameters for the soh() function
class SohMeasure(IntEnum):
	PERCENT = 0  # State of Health Percentage (DEFAULT)
	SOH_STAT = 1  # State of Health Status Bits

# Parameters for the temperature() function
class TempMeasure(IntEnum):
	BATTERY = 0      # Battery Temperature (DEFAULT)
	INTERNAL_TEMP = 1 # Internal IC Temperature

# Parameters for the setGPOUTFunction() funciton
class GpoutFunction(IntEnum):
	SOC_INT = 0 # Set GPOUT to SOC_INT functionality
	BAT_LOW = 1  # Set GPOUT to BAT_LOW functionality