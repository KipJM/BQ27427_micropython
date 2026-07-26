"""
******************************************************************************
BQ27427_Basic
BQ27427 Library Extended Configuration Example

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

Demonstrates how to set up the BQ27427 and read state-of-charge (soc),
battery voltage, average current, remaining capacity, average power, and
state-of-health (soh).

This example is designed to work with the HTP4056 charger IC and
FLY 906090-6000mAh 3.7V battery.

Original License: MIT License
See LICENSE.txt for full license terms.
******************************************************************************
"""
import machine
import asyncio

import time

import BQ27427
import BQ27427h

# Design capacity of your battery, mAh
BATTERY_CAPACITY = 6000
BATTERY_ENERGY = int(BATTERY_CAPACITY * 3.7) # mWh
BATTERY_TERMINATE_VOLTAGE = 3000
BATTERY_TAPER_CURRENT = 1200 * 0.1 # HTP4056: 1.2A max charging, CV stops at 0.1 of charging current

# Change to your i2c controller + pins
i2c = machine.I2C(0, scl=5, sda=4, freq=400000, timeout=BQ27427.BQ72441_I2C_TIMEOUT * 1000) # microseconds

# - Can be removed
devices = i2c.scan()
for device in devices:
    print(hex(device))
# -

lipo = BQ27427.BQ27427(i2c)

async def setup_BQ27427():
    if not lipo.begin():
        raise IOError("Error: Unable to communicate with BQ27427.")

    print("Connected to BQ27427!")

    # make sure to use await!
    await lipo.enter_config(True)
    await lipo.set_capacity(BATTERY_CAPACITY)
    await lipo.set_design_energy(BATTERY_ENERGY)
    if await lipo.get_current_polarity(): # reverse polarity
        await lipo.change_current_polarity()
    await lipo.set_chem_id(BQ27427h.ChemistryProfile.CHEM_B) # change to your setup
    await lipo.set_terminate_voltage(BATTERY_TERMINATE_VOLTAGE) # soc is considered 0% at 3000mV
    # Taper Rate (Unit: 0.1h, basically 10*C) = Design Capacity / (0.1 * Taper Current)
    await lipo.set_taper_rate(int(10 * BATTERY_CAPACITY / BATTERY_TAPER_CURRENT)) # soc is considered 100% at this point
    await lipo.exit_config(True)
    # taper voltage etc. not configured

def print_battery_stats():
    print()
    print(lipo.get_soc(), "% Charged")
    print(lipo.get_voltage(), "mV")
    print(lipo.get_current(BQ27427h.CurrentMeasure.AVG), "mA")
    print(asyncio.run(lipo.get_capacity(BQ27427h.CapacityMeasure.REMAIN)), "/",
          asyncio.run(lipo.get_capacity(BQ27427h.CapacityMeasure.FULL)), "mAh")
    print(lipo.get_avg_power(), "mW")
    print(lipo.get_soh(), "% Health")

asyncio.run(setup_BQ27427())

while True:
    print_battery_stats()
    time.sleep(3)