"""
******************************************************************************
BQ27427.py
BQ27427 MicroPython Library Main Source File

Translated BQ27427 Micropython Library based on BQ27427 Arduino Library
Translated by: KIP
Translation date: July 2026
Repository: https://github.com/KipJM/BQ27427_micropython

Adapted BQ27427 Library based on SparkFun BQ27441 Arduino Library
Original Author: Jim Lindblom @ SparkFun Electronics
Original Date: May 9, 2016
Original Repo: https://github.com/sparkfun/SparkFun_BQ27441_Arduino_Library

Adapted by: Edrean Ernst
Adaptation Date: June 2025
Repository: https://github.com/edreanernst/BQ27427_Arduino_Library

Implementation of all features of the BQ27427 Battery Fuel Gauge.

This library modifies the original SparkFun BQ27441 library to support the
Texas Instruments BQ27427 fuel gauge.

Original License: MIT License
See LICENSE.md for full license terms.
******************************************************************************
"""
import time
from machine import I2C

from BQ27427_Definitions import *
from BQ27427h import *


class BQ27427:
	# *****************************************************************************
	# ************************** Initialization Functions *************************
	# *****************************************************************************

	def __init__(self, i2c: I2C, device_address: int = BQ27427_I2C_ADDRESS,
				 seal_flag: bool = False, user_config_control: bool = False):
		"""
		Initializes class variables.

		:param i2c: I2C peripheral object (already initialized by the caller;
			MicroPython's I2C.init() takes the place of Arduino's Wire.begin()).
		:param device_address: I2C address of the BQ27427 (default 0x55).
		:param seal_flag: Tracks that the IC was previously sealed. Global to
			identify that IC was previously sealed.
		:param user_config_control: Tracks that user has control over
			entering/exiting config.
		"""
		self.i2c = i2c
		self.device_address = device_address
		self.seal_flag = seal_flag
		self.user_config_control = user_config_control

	def begin(self) -> bool:
		"""
		Verifies communication with the BQ27427.
		Must be called before using any other functions.

		:return: true if communication was successful.
		"""
		device_id = self.get_device_type()

		if device_id == BQ27427_DEVICE_ID:
			return True
		else:
			return False

	def set_capacity(self, capacity: int) -> bool:
		"""
		Configures the design capacity of the connected battery.

		:param capacity: design capacity of battery (unsigned 16-bit value)
		:return: true if capacity successfully set.
		"""
		# Write to STATE subclass (82) of BQ27427 extended memory.
		# Offset 0x06 (6)
		# Design capacity is a 2-byte piece of data - MSB first
		# Unit: mAh
		cap_msb = capacity >> 8
		cap_lsb = capacity & 0x00FF
		cap_data = bytes([cap_msb, cap_lsb])
		return self.write_extended_data(BQ27427_ID_STATE, 6, cap_data)

	def get_design_energy(self) -> int:
		"""
		Reads and returns the design energy of the connected battery.

		:return: design energy in milliWattHours (mWh)
		"""
		return (self.read_extended_data(BQ27427_ID_STATE, 8) << 8) | self.read_extended_data(BQ27427_ID_STATE, 9)

	def set_design_energy(self, energy: int) -> bool:
		"""
		Configures the design energy of the connected battery.

		:param energy: design energy of battery (unsigned 16-bit value)
		:return: true if energy successfully set.
		"""
		# Write to STATE subclass (82) of BQ27427 extended memory.
		# Offset 0x08 (8)
		# Design energy is a 2-byte piece of data - MSB first
		# Unit: mWh
		en_msb = energy >> 8
		en_lsb = energy & 0x00FF
		en_data = bytes([en_msb, en_lsb])
		return self.write_extended_data(BQ27427_ID_STATE, 8, en_data)

	def get_terminate_voltage(self) -> int:
		"""
		Reads and returns the terminate voltage of the connected battery.

		:return: terminate voltage in millivolts (mV)
		"""
		return (self.read_extended_data(BQ27427_ID_STATE, 10) << 8) | self.read_extended_data(BQ27427_ID_STATE, 11)

	def set_terminate_voltage(self, voltage: int) -> bool:
		"""
		Configures terminate voltage (lowest operational voltage of battery
		powered circuit).

		:param voltage: terminate voltage of battery (unsigned 16-bit value),
			clamped to the range [2500, 3700] mV.
		:return: true if voltage successfully set.
		"""
		# Write to STATE subclass (82) of BQ27427 extended memory.
		# Offset 0x0A (10)
		# Terminate voltage is a 2-byte piece of data - MSB first
		# Unit: mV
		# Min 2500, Max 3700
		if voltage < 2500:
			voltage = 2500
		if voltage > 3700:
			voltage = 3700

		tv_msb = voltage >> 8
		tv_lsb = voltage & 0x00ff
		tv_data = bytes([tv_msb, tv_lsb])

		return self.write_extended_data(BQ27427_ID_STATE, 10, tv_data)

	def get_discharge_current_threshold(self) -> int:
		"""
		Reads and returns the discharge current threshold.

		:return: discharge current threshold in 0.1h units
		"""
		return (self.read_extended_data(BQ27427_ID_CURRENT_THRESH, 0) << 8) | self.read_extended_data(BQ27427_ID_CURRENT_THRESH, 1)

	def set_discharge_current_threshold(self, value: int) -> bool:
		"""
		Configures discharge current threshold.

		:param value: threshold value in 0.1h units (unsigned 16-bit value),
			clamped to a maximum of 2000.
		:return: true if threshold successfully set.
		"""
		# Write to CURRENT_THRESH subclass (81) of BQ27427 extended memory.
		# Offset 0x00 (0)
		# Discharge current threshold is a 2-byte piece of data - MSB first
		# Unit: 0.1h
		# Min 0, Max 2000
		if value > 2000:
			value = 2000

		dct_msb = value >> 8
		dct_lsb = value & 0x00ff

		dct_data = bytes([dct_msb, dct_lsb])
		return self.write_extended_data(BQ27427_ID_CURRENT_THRESH, 0, dct_data)

	def get_taper_voltage(self) -> int:
		"""
		Reads and returns the taper voltage of the connected battery.

		:return: taper voltage in millivolts (mV)
		"""
		return (self.read_extended_data(BQ27427_ID_CHEM_DATA, 8) << 8) | self.read_extended_data(BQ27427_ID_CHEM_DATA, 9)

	def set_taper_voltage(self, voltage: int) -> bool:
		"""
		Configures taper voltage.

		:param voltage: taper voltage of battery (unsigned 16-bit value),
			clamped to a maximum of 5000.
		:return: true if voltage successfully set.
		"""
		# Write to CHEM_DATA subclass (109) of BQ27427 extended memory.
		# Offset 0x08 (8)
		# Taper voltage is a 2-byte piece of data - MSB first
		# Unit: mV
		# Min 0, Max 5000
		if voltage > 5000:
			voltage = 5000

		tv_msb = voltage >> 8
		tv_lsb = voltage & 0x00ff
		tv_data = bytes([tv_msb, tv_lsb])
		return self.write_extended_data(BQ27427_ID_CHEM_DATA, 8, tv_data)

	def get_taper_rate(self) -> int:
		"""
		Reads and returns the taper rate of the connected battery.

		:return: taper rate in 0.1 h units
		"""
		return (self.read_extended_data(BQ27427_ID_STATE, 21) << 8) | self.read_extended_data(BQ27427_ID_STATE, 22)

	def set_taper_rate(self, rate: int) -> bool:
		"""
		Configures taper rate of connected battery.

		:param rate: taper rate in 0.1 h units (unsigned 16-bit value),
			clamped to a maximum of 2000.
		:return: true if taper rate successfully set.
		"""
		# Write to STATE subclass (82) of BQ27427 extended memory.
		# Offset 0x15 (21)
		# Taper rate is a 2-byte piece of data - MSB first
		# Unit: 0.1h
		# Max 2000
		if rate > 2000:
			rate = 2000

		tr_msb = rate >> 8
		tr_lsb = rate & 0x00ff
		tr_data = bytes([tr_msb, tr_lsb])

		return self.write_extended_data(BQ27427_ID_STATE, 21, tr_data)

	def get_current_polarity(self) -> bool:
		"""
		Reads the polarity of the current measurement.

		:return: true if current polarity is positive, false if negative.
		"""
		cal_bit_0 = self.read_extended_data(BQ27427_ID_CC_CAL, 5)
		return bool(cal_bit_0 & 0x80) # bit 7

	def change_current_polarity(self) -> bool:
		"""
		Changes the polarity of the current measurement.

		:return: true if current polarity successfully changed.
		"""
		cal_bit_0 = self.read_extended_data(BQ27427_ID_CC_CAL, 5)  # Read CC_CAL[0] value
		cal_bit_0 ^= 0x80 # Toggle bit 7 (0x80)
		cal_data = bytes([cal_bit_0])
		return self.write_extended_data(BQ27427_ID_CC_CAL, 5, cal_data)

	# *****************************************************************************
	# ********************** Battery Characteristics Functions ********************
	# *****************************************************************************

	def get_voltage(self) -> int:
		"""
		Reads and returns the battery voltage.

		:return: battery voltage in mV
		"""
		return self.read_word(BQ27427_COMMAND_VOLTAGE)

	def get_current(self, measure_type: CurrentMeasure = CurrentMeasure.AVG) -> int:
		"""
		Reads and returns the specified current measurement.

		:param measure_type: CurrentMeasure enum specifying current value to
			be read (AVG, STBY, or MAX). Defaults to AVG.
		:return: specified current measurement in mA. >0 indicates charging.
		"""
		current = 0
		if measure_type == CurrentMeasure.AVG:
			current = self.read_word(BQ27427_COMMAND_AVG_CURRENT)
		elif measure_type == CurrentMeasure.STBY:
			current = self.read_word(BQ27427_COMMAND_STDBY_CURRENT)
		elif measure_type == CurrentMeasure.MAX:
			current = self.read_word(BQ27427_COMMAND_MAX_CURRENT)
		else:
			raise ValueError("Invalid measure type.")

		# Convert uint16_t to int16_t
		if current >= 0x8000:
			current -= 0x10000
		return current

	def get_capacity(self, measure_type: CapacityMeasure = CapacityMeasure.REMAIN) -> int:
		"""
		Reads and returns the specified capacity measurement.

		:param measure_type: CapacityMeasure enum specifying capacity value
			to be read. Defaults to REMAIN.
		:return: specified capacity measurement in mAh.
		"""
		if measure_type == CapacityMeasure.REMAIN:
			return self.read_word(BQ27427_COMMAND_REM_CAPACITY)
		elif measure_type == CapacityMeasure.FULL:
			return self.read_word(BQ27427_COMMAND_FULL_CAPACITY)
		elif measure_type == CapacityMeasure.AVAIL:
			return self.read_word(BQ27427_COMMAND_NOM_CAPACITY)
		elif measure_type == CapacityMeasure.AVAIL_FULL:
			return self.read_word(BQ27427_COMMAND_AVAIL_CAPACITY)
		elif measure_type == CapacityMeasure.REMAIN_F:
			return self.read_word(BQ27427_COMMAND_REM_CAP_FIL)
		elif measure_type == CapacityMeasure.REMAIN_UF:
			return self.read_word(BQ27427_COMMAND_REM_CAP_UNFL)
		elif measure_type == CapacityMeasure.FULL_F:
			return self.read_word(BQ27427_COMMAND_FULL_CAP_FIL)
		elif measure_type == CapacityMeasure.FULL_UF:
			return self.read_word(BQ27427_COMMAND_FULL_CAP_UNFL)
		elif measure_type == CapacityMeasure.DESIGN:
			return ((self.read_extended_data(BQ27427_ID_STATE, 6) << 8) |
					self.read_extended_data(BQ27427_ID_STATE, 7))
		else:
			raise ValueError("Unknown measure type")

	def get_avg_power(self) -> int:
		"""
		Reads and returns measured average power.

		:return: average power in mAh. >0 indicates charging.
		"""
		value = self.read_word(BQ27427_COMMAND_AVG_POWER)

		# Convert uint16_t to int16_t
		if value >= 0x8000:
			value -= 0x10000
		return value

	def get_soc(self, measure_type: SocMeasure = SocMeasure.FILTERED) -> int:
		"""
		Reads and returns specified state of charge measurement.

		:param measure_type: SocMeasure enum specifying filtered or
			unfiltered measurement. Defaults to FILTERED.
		:return: specified state of charge measurement in %
		"""
		if measure_type == SocMeasure.FILTERED:
			return self.read_word(BQ27427_COMMAND_SOC)
		elif measure_type == SocMeasure.UNFILTERED:
			return self.read_word(BQ27427_COMMAND_SOC_UNFL)
		else:
			raise ValueError("Unknown measure type")

	def get_soh(self, measure_type: SohMeasure = SohMeasure.PERCENT) -> int:
		"""
		Reads and returns specified state of health measurement.

		:param measure_type: SohMeasure enum specifying percentage or status
			bits measurement. Defaults to PERCENT.
		:return: specified state of health measurement in %, or status bits
		"""
		soh_raw = self.read_word(BQ27427_COMMAND_SOH)
		soh_status = soh_raw >> 8
		soh_percent = soh_raw & 0x00FF
		if measure_type == SohMeasure.PERCENT:
			return soh_percent
		elif measure_type == SohMeasure.SOH_STAT:
			return soh_status
		else:
			raise ValueError("Unknown measure type")

	def get_temperature(self, measure_type: TempMeasure = TempMeasure.BATTERY) -> int:
		"""
		Reads and returns specified temperature measurement.

		:param measure_type: TempMeasure enum specifying internal or battery
			measurement. Defaults to BATTERY.
		:return: specified temperature measurement in degrees C (0.1 K units,
			as reported directly by the fuel gauge)
		"""
		if measure_type == TempMeasure.BATTERY:
			return self.read_word(BQ27427_COMMAND_TEMP)
		elif measure_type == TempMeasure.INTERNAL_TEMP:
			return self.read_word(BQ27427_COMMAND_INT_TEMP)
		else:
			raise ValueError("Unknown measure type")

	# *****************************************************************************
	# ************************** GPOUT Control Functions **************************
	# *****************************************************************************

	def get_gpout_polarity(self) -> bool:
		"""
		Get GPOUT polarity setting (active-high or active-low).

		:return: true if active-high, false if active-low
		"""
		return bool(self.get_op_config() & BQ27427_OPCONFIG_GPIOPOL)

	def set_gpout_polarity(self, active_high: bool) -> bool:
		"""
		Set GPOUT polarity to active-high or active-low.

		:param active_high: true if active-high, false if active-low
		:return: true on success
		"""
		old_op_config = self.get_op_config()

		# Check to see if update needed:
		if ((active_high and (old_op_config & BQ27427_OPCONFIG_GPIOPOL)) or
				((not active_high) and not (old_op_config & BQ27427_OPCONFIG_GPIOPOL))):
			return True

		new_op_config = old_op_config

		if active_high:
			new_op_config |= BQ27427_OPCONFIG_GPIOPOL
		else:
			new_op_config &= ~BQ27427_OPCONFIG_GPIOPOL

		return self.write_op_config(new_op_config)

	def get_gpout_function(self) -> bool:
		"""
		Get GPOUT function (BAT_LOW or SOC_INT).

		:return: true if BAT_LOW or false if SOC_INT
		"""
		return bool(self.get_op_config() & BQ27427_OPCONFIG_BATLOWEN)

	def set_gpout_function(self, function: GpoutFunction) -> bool:
		"""
		Set GPOUT function to BAT_LOW or SOC_INT.

		:param function: should be either GpoutFunction.BAT_LOW or
			GpoutFunction.SOC_INT
		:return: true on success
		"""
		old_op_config = self.get_op_config()
		is_bat_low = (function == GpoutFunction.BAT_LOW)

		if (is_bat_low and (old_op_config & BQ27427_OPCONFIG_BATLOWEN)) or \
				((not is_bat_low) and not (old_op_config & BQ27427_OPCONFIG_BATLOWEN)):
			return True

		new_op_config = old_op_config
		if is_bat_low:
			new_op_config |= BQ27427_OPCONFIG_BATLOWEN
		else:
			new_op_config &= ~BQ27427_OPCONFIG_BATLOWEN

		return self.write_op_config(new_op_config)

	def get_soc1_set_threshold(self) -> int:
		"""
		Get SOC1_Set Threshold - threshold to set the alert flag.

		:return: state of charge value between 0 and 100%
		"""
		return self.read_extended_data(BQ27427_ID_DISCHARGE, 0)

	def get_soc1_clear_threshold(self) -> int:
		"""
		Get SOC1_Clear Threshold - threshold to clear the alert flag.

		:return: state of charge value between 0 and 100%
		"""
		return self.read_extended_data(BQ27427_ID_DISCHARGE, 1)

	def set_soc1_thresholds(self, set: int, clear: int) -> bool:
		"""
		Set the SOC1 set and clear thresholds to a percentage.

		:param set: set threshold percentage, clamped to [0, 100]
		:param clear: clear threshold percentage, clamped to [0, 100].
			clear should be > set.
		:return: true on success
		"""
		thresholds = bytes([
			min(max(set, 0), 100),
			min(max(clear, 0), 100)
		])
		return self.write_extended_data(BQ27427_ID_DISCHARGE, 0, thresholds)

	def get_socf_set_threshold(self) -> int:
		"""
		Get SOCF_Set Threshold - threshold to set the alert flag.

		:return: state of charge value between 0 and 100%
		"""
		return self.read_extended_data(BQ27427_ID_DISCHARGE, 2)

	def get_socf_clear_threshold(self) -> int:
		"""
		Get SOCF_Clear Threshold - threshold to clear the alert flag.

		:return: state of charge value between 0 and 100%
		"""
		return self.read_extended_data(BQ27427_ID_DISCHARGE, 3)

	def set_socf_thresholds(self, set: int, clear: int) -> bool:
		"""
		Set the SOCF set and clear thresholds to a percentage.

		:param set: set threshold percentage, clamped to [0, 100]
		:param clear: clear threshold percentage, clamped to [0, 100].
			clear should be > set.
		:return: true on success
		"""
		thresholds = bytes([
			min(max(set, 0), 100),
			min(max(clear, 0), 100)
		])
		return self.write_extended_data(BQ27427_ID_DISCHARGE, 2, thresholds)

	def get_soc_flag(self) -> bool:
		"""
		Check if the SOC1 flag is set in flags().

		:return: true if flag is set
		"""
		return bool(self.get_flags() & BQ27427_FLAG_SOC1)

	def get_socf_flag(self) -> bool:
		"""
		Check if the SOCF flag is set in flags().

		:return: true if flag is set
		"""
		return bool(self.get_flags() & BQ27427_FLAG_SOCF)

	def get_itpor_flag(self) -> bool:
		"""
		Check if the ITPOR flag is set in flags().

		:return: true if flag is set
		"""
		return bool(self.get_flags() & BQ27427_FLAG_ITPOR)

	def get_fc_flag(self) -> bool:
		"""
		Check if the FC flag is set in flags().

		:return: true if flag is set
		"""
		return bool(self.get_flags() & BQ27427_FLAG_FC)

	def get_chg_flag(self) -> bool:
		"""
		Check if the CHG flag is set in flags().

		:return: true if flag is set
		"""
		return bool(self.get_flags() & BQ27427_FLAG_CHG)

	def get_dsg_flag(self) -> bool:
		"""
		Check if the DSG flag is set in flags().

		:return: true if flag is set
		"""
		return bool(self.get_flags() & BQ27427_FLAG_DSG)

	def get_soci_delta(self) -> int:
		"""
		Get the SOC_INT interval delta.

		:return: interval percentage value between 1 and 100
		"""
		return self.read_extended_data(BQ27427_ID_STATE, 26)

	def set_soci_delta(self, delta: int) -> bool:
		"""
		Set the SOC_INT interval delta to a value between 1 and 100.

		:param delta: interval percentage value between 1 and 100
		:return: true on success
		"""
		soci = bytes([min(max(delta, 0), 100)])
		return self.write_extended_data(BQ27427_ID_STATE, 26, soci)

	def pulse_gpout(self) -> bool:
		"""
		Pulse the GPOUT pin - must be in SOC_INT mode.

		:return: true on success
		"""
		return self.execute_control_word(BQ27427_CONTROL_PULSE_SOC_INT)

	# *****************************************************************************
	# *************************** Control Sub-Commands ****************************
	# *****************************************************************************

	def get_device_type(self) -> int:
		"""
		Read the device type - should be 0x0427.

		:return: 16-bit value read from DEVICE_TYPE subcommand
		"""
		return self.read_control_word(BQ27427_CONTROL_DEVICE_TYPE)

	# TODO (KIP): Change all to asyncio non blocking waits
	# Also this can be way more simplified using config()
	def set_chem_id(self, chem_id: ChemistryProfile) -> bool:
		"""
		Configures the chemistry profile of the connected battery.

		:param chem_id: ChemistryProfile enum specifying chemistry profile
			value to be set.
		:return: true if chemistry profile successfully set.
		"""
		# Original commented section abt entering config mode is omitted

		if self.is_sealed():
			self.seal_flag = True
			self.unseal() # Must be unsealed before making changes

		old_chem_id = self.read_control_word(BQ27427_CONTROL_CHEM_ID)

		if self.execute_control_word(BQ27427_CONTROL_SET_CFGUPDATE):
			timeout = BQ72441_I2C_TIMEOUT
			while timeout > 0 and not (self.get_flags() & BQ27427_FLAG_CFGUPMODE):
				time.sleep_ms(1)
				timeout -= 1

			if timeout > 0:
				if self.execute_control_word(chem_id):
					time.sleep_ms(100) # wait for the BQ27427 to process the command
					if self.soft_reset():
						timeout = BQ72441_I2C_TIMEOUT
						while timeout > 0 and (self.get_flags() & BQ27427_FLAG_CFGUPMODE):
							time.sleep_ms(1)
							timeout -= 1

						if timeout > 0:
							new_chem_id = self.read_control_word(BQ27427_CONTROL_CHEM_ID)
							if new_chem_id != old_chem_id:
								if self.seal_flag:
									self.seal()
								return True
							return False

					return False
				else:
					return False

		return False

	def get_chem_id(self) -> ChemistryProfile:
		"""
		Reads and returns the battery chemistry profile.

		:return: ChemistryProfile enum value
		"""
		chem_id = self.read_control_word(BQ27427_CONTROL_CHEM_ID)
		return ChemistryProfile(chem_id)

	def enter_config(self, user_control: bool = True) -> bool:
		"""
		Enter configuration mode - set user_control if calling from user code
		and you want control over when to exit_config.

		:param user_control: true if the caller is handling entering and
			exiting config mode (should be false in library calls).
		:return: true on success
		"""
		if user_control:
			self.user_config_control = True

		if self.is_sealed():
			self.seal_flag = True
			self.unseal() # Must be unsealed before making changes

		if self.execute_control_word(BQ27427_CONTROL_SET_CFGUPDATE):
			timeout = BQ72441_I2C_TIMEOUT
			while timeout > 0 and not (self.get_flags() & BQ27427_FLAG_CFGUPMODE):
				time.sleep_ms(1)
				timeout -= 1

			if timeout > 0:
				return True

		return False

	def exit_config(self, user_control: bool = False) -> bool:
		"""
		Exit configuration mode.

		:param user_control: whether the caller retains control of
			entering/exiting config mode after this call.
		:return: true on success
		"""
		if user_control:
			self.user_config_control = False

		if self.soft_reset():
			timeout = BQ72441_I2C_TIMEOUT
			while timeout > 0 and (self.get_flags() & BQ27427_FLAG_CFGUPMODE):
				time.sleep_ms(1)
				timeout -= 1

			if timeout > 0:
				if self.seal_flag:
					self.seal() # Seal back up if IC was sealed coming in
				return True

		return False

	def get_flags(self) -> int:
		"""
		Read the flags() command.

		:return: 16-bit representation of flags() command register
		"""
		return self.read_word(BQ27427_COMMAND_FLAGS)

	def get_status(self) -> int:
		"""
		Read the CONTROL_STATUS subcommand of control().

		:return: 16-bit representation of CONTROL_STATUS subcommand
		"""
		return self.read_control_word(BQ27427_CONTROL_STATUS)

	def reset(self) -> bool:
		"""
		Issue a factory reset to the BQ27427.

		:return: true on success
		"""
		if not self.user_config_control:
			self.enter_config(False) # Enter config mode if not already in it

		if self.execute_control_word(BQ27427_CONTROL_RESET):
			if not self.user_config_control:
				self.exit_config()
			return True
		else:
			return False

	# *********** Private Functions ***********

	def is_sealed(self) -> bool:
		"""
		Check if the BQ27427 is sealed or not.

		:return: true if the chip is sealed
		"""
		stat = self.get_status()
		return bool(stat & BQ27427_STATUS_SS)

	def seal(self) -> bool:
		"""
		Seal the BQ27427.

		:return: true on success
		"""
		return bool(self.read_control_word(BQ27427_CONTROL_SEALED))

	def unseal(self) -> bool:
		"""
		Unseal the BQ27427.

		To unseal the BQ27427, write the key to the control command. Then
		immediately write the same key to control again.

		:return: true on success
		"""
		if self.read_control_word(BQ27427_UNSEAL_KEY):
			return bool(self.read_control_word(BQ27427_UNSEAL_KEY))
		return False

	def get_op_config(self) -> int:
		"""
		Read the 16-bit opConfig register from extended data.

		:return: opConfig register contents
		"""
		return (self.read_extended_data(BQ27427_ID_REGISTERS, 0) << 8) | self.read_extended_data(BQ27427_ID_REGISTERS, 1)

	def write_op_config(self, value: int) -> bool:
		"""
		Write the 16-bit opConfig register in extended data.

		:param value: new 16-bit value for opConfig
		:return: true on success
		"""
		op_config_msb = value >> 8
		op_config_lsb = value & 0x00FF
		op_config_data = bytes([op_config_msb, op_config_lsb])

		# OpConfig register location: BQ27427_ID_REGISTERS id, offset 0
		return self.write_extended_data(BQ27427_ID_REGISTERS, 0, op_config_data)

	def soft_reset(self) -> bool:
		"""
		Issue a soft-reset to the BQ27427.

		:return: true on success
		"""
		return self.execute_control_word(BQ27427_CONTROL_SOFT_RESET)

	def read_word(self, sub_address: int) -> int:
		"""
		Read a 16-bit command word from the BQ27427.

		:param sub_address: the command to be read from
		:return: 16-bit value of the command's contents
		"""
		data = bytearray(2)
		self.i2c_read_bytes(sub_address, data)
		return (int(data[1]) << 8) | data[0]

	def read_control_word(self, function: int) -> int:
		"""
		Read a 16-bit subcommand() from the BQ27427's control().

		:param function: the subcommand of control() to be read
		:return: 16-bit value of the subcommand's contents
		"""
		sub_command_msb = function >> 8
		sub_command_lsb = function & 0x00FF
		command = bytes([sub_command_lsb, sub_command_msb])
		data = bytearray(2)

		self.i2c_write_bytes(0, command)

		if self.i2c_read_bytes(0, data):
			return int(data[1]) << 8 | data[0]

		return False

	def execute_control_word(self, function: int) -> bool:
		"""
		Execute a subcommand() from the BQ27427's control().

		:param function: the subcommand of control() to be executed
		:return: true on success
		"""
		sub_command_msb = function >> 8
		sub_command_lsb = function & 0x00FF
		command = bytes([sub_command_lsb, sub_command_msb])

		if self.i2c_write_bytes(0, command):
			return True
		return False

	# *****************************************************************************
	# ************************** Extended Data Commands ***************************
	# *****************************************************************************

	def block_data_control(self) -> bool:
		"""
		Issue a BlockDataControl() command to enable BlockData access.

		:return: true on success
		"""
		enable_byte = bytes([0x00])
		return self.i2c_write_bytes(BQ27427_EXTENDED_CONTROL, enable_byte)

	def block_data_class(self, id: int) -> bool:
		"""
		Issue a DataClass() command to set the data class to be accessed.

		:param id: the id number of the class
		:return: true on success
		"""
		return self.i2c_write_bytes(BQ27427_EXTENDED_DATACLASS, bytes([id]))

	def block_data_offset(self, offset: int) -> bool:
		"""
		Issue a DataBlock() command to set the data block to be accessed.

		:param offset: offset of the data block
		:return: true on success
		"""
		return self.i2c_write_bytes(BQ27427_EXTENDED_DATABLOCK, bytes([offset]))

	def block_data_checksum(self) -> int:
		"""
		Read the current checksum using BlockDataCheckSum().

		:return: the 8-bit checksum value
		"""
		csum = bytearray(1)
		self.i2c_read_bytes(BQ27427_EXTENDED_CHECKSUM, csum)
		return csum[0]

	def read_block_data(self, offset: int) -> int:
		"""
		Use BlockData() to read a byte from the loaded extended data.

		:param offset: offset of data block byte to be read
		:return: the 8-bit value read
		"""
		ret = bytearray(1)
		address = offset + BQ27427_EXTENDED_BLOCKDATA
		self.i2c_read_bytes(address, ret)
		return ret[0]

	def write_block_data(self, offset: int, data: int) -> bool:
		"""
		Use BlockData() to write a byte to an offset of the loaded data.

		:param offset: the position of the byte to be written
		:param data: the value to be written
		:return: true on success
		"""
		address = offset + BQ27427_EXTENDED_BLOCKDATA
		return self.i2c_write_bytes(address, bytes([data]))

	def compute_block_checksum(self) -> int:
		"""
		Read all 32 bytes of the loaded extended data and compute a
		checksum based on the values.

		:return: 8-bit checksum value calculated based on loaded data
		"""
		data = bytearray(32)
		self.i2c_read_bytes(BQ27427_EXTENDED_BLOCKDATA, data)

		csum = 0
		for i in range(32):
			csum += data[i]
		csum = 255 - (csum % 256)

		return csum

	def write_block_checksum(self, csum: int) -> bool:
		"""
		Use the BlockDataCheckSum() command to write a checksum value.

		:param csum: the 8-bit checksum to be written
		:return: true on success
		"""
		return self.i2c_write_bytes(BQ27427_EXTENDED_CHECKSUM, bytes([csum]))

	def read_extended_data(self, class_id: int, offset: int) -> int:
		"""
		Read a byte from extended data specifying a class ID and position offset.

		:param class_id: the id of the class to be read from
		:param offset: the byte position of the byte to be read
		:return: 8-bit value of specified data
		"""
		if not self.user_config_control:
			self.enter_config(False)

		if not self.block_data_control():  # enable block data memory control
			return False  # Return false if enable fails
		if not self.block_data_class(class_id):  # Write class ID using DataBlockClass()
			return False

		self.block_data_offset(offset // 32)  # Write 32-bit block offset (usually 0)

		self.compute_block_checksum()  # Compute checksum going in
		# old_csum = self.block_data_checksum()

		ret_data = self.read_block_data(offset % 32)  # Read from offset (limit to 0-31)

		if not self.user_config_control:
			self.exit_config()

		return ret_data

	def write_extended_data(self, class_id: int, offset: int, data: bytes) -> bool:
		"""
		Write a specified number of bytes to extended data specifying a
		class ID, position offset.

		:param class_id: the id of the class to be written to
		:param offset: the byte position of the first byte to be written
		:param data: the data buffer to be written
		:return: true on success
		"""
		length = len(data)
		if length > 32:
			return False

		if not self.user_config_control:
			if not self.enter_config(False):
				return False  # Return false if enter_config fails

		if not self.block_data_control():  # enable block data memory control
			return False  # Return false if enable fails
		if not self.block_data_class(class_id):  # Write class ID using DataBlockClass()
			return False

		self.block_data_offset(offset // 32)  # Write 32-bit block offset (usually 0)
		self.compute_block_checksum()  # Compute checksum going in
		# old_csum = self.block_data_checksum()

		# Write data bytes:
		for i in range(length):
			# Write to offset, mod 32 if offset is greater than 32
			# The block_data_offset above sets the 32-bit block
			if not self.write_block_data((offset % 32) + i, data[i]):
				return False  # Return false if write_block_data fails

		# Write new checksum using BlockDataChecksum (0x60)
		new_csum = self.compute_block_checksum()  # Compute the new checksum
		if not self.write_block_checksum(new_csum):
			return False  # Return false if checksum write fails

		if not self.user_config_control:
			time.sleep_ms(10)  # Wait for BQ27427 to process the write
			if not self.exit_config():
				return False  # Return false if exit_config fails

		return True

	# *****************************************************************************
	# ************************ I2C Read and Write Routines ************************
	# *****************************************************************************

	def i2c_read_bytes(self, sub_address: int, data: bytearray) -> bool:
		"""
		Read a specified number of bytes over I2C at a given sub_address.

		:param sub_address: the 8-bit address of the data to be read
		:param data: the (pre-sized) buffer to be filled with the read bytes
		:return: true on success
		"""
		self.i2c.readfrom_mem_into(self.device_address, sub_address, data)
		return True

	def i2c_write_bytes(self, sub_address: int, src: bytes) -> bool:
		"""
		Write a specified number of bytes over I2C to a given sub_address.

		:param sub_address: the 8-bit address of the data to be written to
		:param src: the data buffer to be written
		:return: true on success
		"""
		self.i2c.writeto_mem(self.device_address, sub_address, src)
		return True
