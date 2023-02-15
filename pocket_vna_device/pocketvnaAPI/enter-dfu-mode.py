from __future__ import print_function

import errno, sys
import pocketvna

##  dfu-programmer
## Next sequence is working for me for reprogramming a device:
## Enter into DFU mode. For example using this code
## Execute following sequence
## > ./dfu-programmer atxmega32a4u  erase
## > ./dfu-programmer atxmega32a4u  flash ../firmware_hex/SmartVNA1.5.hex
## > ./dfu-programmer atxmega32a4u  reset
## Profit
##

## Flip (on windows) (http://www.microchip.com/developmenttools/ProductDetails.aspx?PartNO=FLIP)
## * Select ATXmega32A4U as target device
## * Make sure EEPROM is selected
## * Select HEX file
## * Put a device into DFU mode (in our application or through python script)
## * If Flip software has not detected a device click on “Select a comunication medium” => “USB”
## * Push “Run”. All 4 steps should (erase/blank check/Program/Verify) should be completed and highlighted with green.
## * Click on “Start Application” (with --reset) checked


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def makeDriver():
    try:
        return pocketvna.Driver()
    except:
        eprint("Can not create Driver object")
        return None


def closeDriver(driver):
    if driver.valid():
        driver.close()
    pocketvna.close_api()


def exit_failure(driver, msg):
    closeDriver(driver)
    eprint(msg)
    sys.exit(os.EX_SOFTWARE)


# Working code
driver = makeDriver()

if driver and driver.count() > 0 and driver.connect_to(0):
    try:
        driver.dfu_mode()
        print(
            "Entered. Now you can reprogram device with dfu-programmer or with flip software"
        )
        closeDriver(driver)
    except:
        exit_failure(driver, "Failed Entering DFU mode")
else:
    exit_failure(driver, "Looks no device is connected")
    sys.exit(os.EX_SOFTWARE)
