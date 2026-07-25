"""
******************************************************************************
SparkFunBQ27427.cpp
BQ27427 Arduino Library Main Source File

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
See LICENSE.txt for full license terms.
******************************************************************************
"""
import time
from machine import I2C

from BQ27427_Definitions import *
from BQ27427h import *


# Initializes class variables
class BQ27427:
	# *****************************************************************************
	# ************************** Initialization Functions *************************
	# *****************************************************************************

	def __init__(self, i2c: I2C, device_address: int, seal_flag: bool, user_config_control: bool):
		self.i2c = i2c
		self.device_address = device_address
		self.seal_flag = seal_flag
		self.user_config_control = user_config_control

	def begin(self) -> bool:
		"""
		Verifies communication with the BQ27427.
		Must be called before using any other functions.

		:param i2c: I2C peripheral object. Changed from arduino impl.
		:return true if communication was successful.
		"""
		device_id = self.get_device_type()

		if device_id == BQ27427_DEVICE_ID:
			return True
		else:
			return False


	def set_capacity(self, capacity: int):
		# Write to STATE subclass (82) of BQ27427 extended memory.
		# Offset 0x06 (6)
		# Design capacity is a 2-byte piece of data - MSB first
		# Unit: mAh
		cap_msb = capacity >> 8
		cap_lsb = capacity & 0x00FF
		cap_data = bytes([cap_msb, cap_lsb])
		return self.write_extended_data(BQ27427_ID_STATE, 6, cap_data)

	def get_design_energy(self) -> int:
		return (self.read_extended_data(BQ27427_ID_STATE, 8) << 8) | self.read_extended_data(BQ27427_ID_STATE, 9)

	def set_design_energy(self, energy: int):
		# Write to STATE subclass (82) of BQ27427 extended memory.
		# Offset 0x08 (8)
		# Design energy is a 2-byte piece of data - MSB first
		# Unit: mWh

		en_msb = energy >> 8
		en_lsb = energy & 0x00FF
		en_data = bytes([en_msb, en_lsb])
		return self.write_extended_data(BQ27427_ID_STATE, 8, en_data)

	def get_terminate_voltage(self) -> int:
		return (self.read_extended_data(BQ27427_ID_STATE, 10) << 8) | self.read_extended_data(BQ27427_ID_STATE, 11)

	def set_terminate_voltage(self, voltage: int):
		# Write to STATE subclass (82) of BQ27427 extended memory.
		# Offset 0x0A (10)
		# Terminate voltage is a 2-byte piece of data - MSB first
		# Unit: mV
		# Min 2500, Max 3700
		if voltage < 2500:
			voltage	= 2500
		if voltage > 3700:
			voltage = 3700

		tv_msb = voltage >> 8
		tv_lsb = voltage & 0x00ff
		tv_data = bytes([tv_msb, tv_lsb])

		return self.write_extended_data(BQ27427_ID_STATE, 10, tv_data)

	def _get_discharge_current_threshold(self) -> int:
		return (self.read_extended_data(BQ27427_ID_CURRENT_THRESH, 0) << 8) | self.read_extended_data(BQ27427_ID_CURRENT_THRESH, 1)

	def set_discharge_current_threshold(self, value: int) -> bool:
		# Write to STATE subclass (81) of BQ27427 extended memory.
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
		return (self.read_extended_data(BQ27427_ID_CHEM_DATA, 8) << 8) | self.read_extended_data(BQ27427_ID_CHEM_DATA, 9)

	def set_taper_voltage(self, voltage: int) -> bool:
		# Write to STATE subclass (109) of BQ27427 extended memory.
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
		return (self.read_extended_data(BQ27427_ID_STATE, 21) << 8) | self.read_extended_data(BQ27427_ID_STATE, 22)

	def set_taper_rate(self, rate: int) -> bool:
		# Write to STATE subclass (82) of BQ27427 extended memory.
		# Offset 0x15 (21)
		# Termiante voltage is a 2-byte piece of data - MSB first
		# Unit: 0.1h
		# Max 2000

		if rate > 2000:
			rate = 2000

		tr_msb = rate >> 8
		tr_lsb = rate & 0x00ff
		tr_data = bytes([tr_msb, tr_lsb])

		return self.write_extended_data(BQ27427_ID_STATE, 21, tr_data)


	def get_current_polarity(self) -> bool:
		cal_bit_0 = self.read_extended_data(BQ27427_ID_CC_CAL, 5)
		return bool(cal_bit_0 & 0x80) # bit 7

	def change_current_polarity(self) -> bool:
		cal_bit_0 = self.read_extended_data(BQ27427_ID_CC_CAL, 5) # Read CC_CAL[0] value
		cal_bit_0 ^= 0x80 # Toggle bit 7 (0x80)
		cal_data = bytes([cal_bit_0])
		return self.write_extended_data(BQ27427_ID_CC_CAL, 5, cal_data)

	# *****************************************************************************
	# ********************** Battery Characteristics Functions ********************
	# *****************************************************************************

	def get_voltage(self) -> int:
		return self.read_word(BQ27427_COMMAND_VOLTAGE)

	def get_current(self, measure_type: CurrentMeasure = CurrentMeasure.AVG) -> int:
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
			raise Exception("Unknown measure type")

	def get_avg_power(self) -> int:
		value = self.read_word(BQ27427_COMMAND_AVG_POWER)

		# Convert uint16_t to int16_t
		if value >= 0x8000:
			value -= 0x10000
		return value

	def get_soc(self, measure_type: SocMeasure = SocMeasure.FILTERED) -> int:
		if measure_type == SocMeasure.FILTERED:
			return self.read_word(BQ27427_COMMAND_SOC)
		elif measure_type == SocMeasure.UNFILTERED:
			return self.read_word(BQ27427_COMMAND_SOC_UNFL)
		else:
			raise Exception("Unknown measure type")

	def get_soh(self, measure_type: SohMeasure = SohMeasure.PERCENT) -> int:
		soh_raw = self.read_word(BQ27427_COMMAND_SOH)
		soh_status = soh_raw >> 8
		soh_percent = soh_raw & 0x00FF
		if measure_type == SohMeasure.PERCENT:
			return soh_percent
		elif measure_type == SohMeasure.SOH_STAT:
			return soh_status
		else:
			raise Exception("Unknown measure type")

	def get_temperature(self, measure_type: TempMeasure = TempMeasure.BATTERY) -> int:
		if measure_type == TempMeasure.BATTERY:
			return self.read_word(BQ27427_COMMAND_TEMP)
		elif measure_type == TempMeasure.INTERNAL_TEMP:
			return self.read_word(BQ27427_COMMAND_INT_TEMP)
		else:
			raise Exception("Unknown measure type")

	# *****************************************************************************
 	# ************************** GPOUT Control Functions **************************
 	# *****************************************************************************

	def get_gpout_polarity(self) -> bool:
		return self.get_op_config() & BQ27427_OPCONFIG_GPIOPOL

	def set_gpout_polarity(self, active_high: bool) -> bool:
		old_op_config = self.get_op_config()

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
		return self.get_op_config() & BQ27427_OPCONFIG_BATLOWEN

	def set_gpout_function(self, function: GpoutFunction):
		old_op_config = self.get_op_config()

		if ((function and (old_op_config & BQ27427_OPCONFIG_BATLOWEN)) or
				((not function) and not (old_op_config & BQ27427_OPCONFIG_BATLOWEN))):
			return True

		new_op_config = old_op_config
		if function == GpoutFunction.BAT_LOW:
			new_op_config |= BQ27427_OPCONFIG_BATLOWEN
		else:
			new_op_config &= ~BQ27427_OPCONFIG_BATLOWEN

		return self.write_op_config(new_op_config)


	def get_soc1_set_threshold(self) -> int:
		return self.read_extended_data(BQ27427_ID_DISCHARGE, 0)

	def get_soc1_clear_threshold(self) -> int:
		return self.read_extended_data(BQ27427_ID_DISCHARGE, 1)

	def set_soc1_thresholds(self, set: int, clear: int) -> bool:
		thresholds = bytearray([
			min(max(set, 0), 100),
			min(max(clear, 0), 100)
		])
		return self.write_extended_data(BQ27427_ID_DISCHARGE, 0, thresholds)


	def get_socf_set_threshold(self) -> int:
		return self.read_extended_data(BQ27427_ID_DISCHARGE, 2)

	def get_socf_clear_threshold(self) -> int:
		return self.read_extended_data(BQ27427_ID_DISCHARGE, 3)

	def set_socf_thresholds(self, set: int, clear: int) -> bool:
		thresholds = bytearray([
			min(max(set, 0), 100),
			min(max(clear, 0), 100)
		])
		return self.write_extended_data(BQ27427_ID_DISCHARGE, 2, thresholds)


	def get_soc_flag(self) -> bool:
		return bool(self.get_flags() & BQ27427_FLAG_SOC1)

	def get_socf_flag(self) -> bool:
		return bool(self.get_flags() & BQ27427_FLAG_SOCF)

	def get_itpor_flag(self) -> bool:
		return bool(self.get_flags() & BQ27427_FLAG_ITPOR)

	def get_fc_flag(self) -> bool:
		return bool(self.get_flags() & BQ27427_FLAG_FC)

	def get_chg_flag(self) -> bool:
		return bool(self.get_flags() & BQ27427_FLAG_CHG)

	def get_dsg_flag(self) -> bool:
		return bool(self.get_flags() & BQ27427_FLAG_DSG)

	def get_soci_delta(self) -> int:
		return self.read_extended_data(BQ27427_ID_STATE, 26)

	def set_soci_delta(self, delta: int):
		soci = bytes([min(max(delta, 0), 100)])
		return self.write_extended_data(BQ27427_ID_STATE, 26, soci)

	def pulse_gpout(self) -> bool:
		return self.execute_control_word(BQ27427_CONTROL_PULSE_SOC_INT)

	# ****************************
	# *** Control Sub-Commands ***
	# ****************************

	def get_device_type(self) -> int:
		return self.read_control_word(BQ27427_CONTROL_DEVICE_TYPE)

	# TODO (KIP): Change all to asyncio non blocking waits
	# Also this can be way more simplified using config()
	def set_chem_id(self, chem_id: ChemistryProfile):
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
		chem_id = self.read_control_word(BQ27427_CONTROL_CHEM_ID)
		return ChemistryProfile(chem_id)

	def enter_config(self, user_control: bool = True) -> bool:
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
		if user_control:
			self.user_config_control = False

		if self.soft_reset():
			timeout = BQ72441_I2C_TIMEOUT
			while timeout > 0 and (self.get_flags() & BQ27427_FLAG_CFGUPMODE):
				time.sleep_ms(1)
				timeout -= 1

			if timeout > 0:
				if self.seal_flag:
					self.seal() # Seal back up if we IC was sealed coming in
				return True

		return False

	def get_flags(self) -> int:
		return self.read_word(BQ27427_COMMAND_FLAGS)

	def get_status(self) -> int:
		return self.read_control_word(BQ27427_CONTROL_STATUS)

	def reset(self) -> bool:
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
		stat = self.get_status()
		return stat & BQ27427_STATUS_SS

	def seal(self) -> bool:
		return bool(self.read_control_word(BQ27427_CONTROL_SEALED))

	def unseal(self) -> bool:
		# To unseal the BQ27427, write the key to the control
		# command. Then immediately write the same key to control again.
		if self.read_control_word(BQ27427_UNSEAL_KEY):
			return bool(self.read_control_word(BQ27427_UNSEAL_KEY))
		return False

	def get_op_config(self) -> int:
		return self.read_extended_data(BQ27427_ID_REGISTERS, 0)

	def write_op_config(self, value: int):
		op_config_msb = value >> 8
		op_config_lsb = value & 0x00FF
		op_config_data = bytes([op_config_msb, op_config_lsb])

		# OpConfig register location: BQ27427_ID_REGISTERS id, offset 0
		return self.write_extended_data(BQ27427_ID_REGISTERS, 0, op_config_data)

	def soft_reset(self) -> bool:
		return self.execute_control_word(BQ27427_CONTROL_SOFT_RESET)

	def read_word(self, sub_address: int) -> int:
		data = bytearray([0,0])
		self.i2c_read_bytes(sub_address, data)
		return (int(data[1]) << 8) | data[0]

	def read_control_word(self, function: int) -> int:
		"""
		Read a 16-bit subcommand() from the BQ27427's control()

		:param function is the subcommand of control() to be read
		:return 16-bit value of the subcommand's contents
		"""
		sub_command_msb = function >> 8
		sub_command_lsb = function & 0x00FF
		command = bytes([sub_command_lsb, sub_command_msb])
		data = bytearray([0, 0])

		self.i2c_write_bytes(0, command)

		if self.i2c_read_bytes(0, data):
			return int(data[1]) << 8 | data[0]

		return False

	def execute_control_word(self, function: int) -> bool:
		sub_command_msb = function >> 8
		sub_command_lsb = function & 0x00FF
		command = bytes([sub_command_lsb, sub_command_msb])
		data = bytearray([0,0]) # TODO unused i think??

		if self.i2c_write_bytes(0, command):
			return True
		return False

	# *****************************************************************************
	# ************************** Extended Data Commands ***************************
	# *****************************************************************************

	def block_data_control(self) -> bool:
		enable_byte = bytes([0x00])
		return self.i2c_write_bytes(BQ27427_EXTENDED_CONTROL, enable_byte)

	def block_data_class(self, id: int) -> bool:
		return self.i2c_write_bytes(BQ27427_EXTENDED_DATACLASS, bytes([id]))

	def block_data_offset(self, offset: int) -> bool:
		return self.i2c_write_bytes(BQ27427_EXTENDED_DATABLOCK, bytes([offset]))

	def block_data_checksum(self) -> int:
		csum = bytearray([0])
		self.i2c_read_bytes(BQ27427_EXTENDED_CHECKSUM, csum)
		return csum[0]


	def read_block_data(self, offset: int) -> int:
		ret = bytearray([0])
		address = offset + BQ27427_EXTENDED_BLOCKDATA
		self.i2c_read_bytes(address, ret)
		return ret[0]

	def write_block_data(self, offset: int, data: int) -> bool:
		"""
		Use BlockData() to write a byte to an offset of the loaded data

		:param offset is the position of the byte to be written
		       data is the value to be written
		:return true on success
		"""
		address = offset + BQ27427_EXTENDED_BLOCKDATA
		return self.i2c_write_bytes(address, bytes([data]))

	def compute_block_checksum(self) -> int:
		"""
		Read all 32 bytes of the loaded extended data and compute a
		checksum based on the values.

		:return 8-bit checksum value calculated based on loaded data
		"""

		data = bytearray([0 for _ in range(32)])
		self.i2c_read_bytes(BQ27427_EXTENDED_BLOCKDATA, data)

		csum = 0
		for i in range(32):
			csum += data[i]
		csum = 255 - csum

		return csum

	def write_block_checksum(self, csum: int) -> bool:
		"""
		Use the BlockDataCheckSum() command to write a checksum value

		:param csum is the 8-bit checksum to be written
		:return true on success
		"""

		return self.i2c_write_bytes(BQ27427_EXTENDED_CHECKSUM, bytes(csum))

	def read_extended_data(self, class_id: int, offset: int) -> int:
		# TODO
		pass

	def write_extended_data(self, class_id: int, offset: int, data: bytes) -> bool:
		# TODO
		pass

	def i2c_read_bytes(self, sub_address: int, data: bytearray) -> bool:
		self.i2c.readfrom_mem_into(self.device_address, sub_address, data)
		return True

	def i2c_write_bytes(self, sub_address: int, src: bytes) -> bool:
		self.i2c.writeto_mem(self.device_address, sub_address, src)
		return True