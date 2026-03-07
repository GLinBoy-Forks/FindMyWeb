# Flashing a board
If you don't have a board listed below follow the [Zephyr docs](https://docs.zephyrproject.org/latest/develop/west/build-flash-debug.html#flashing-west-flash) for flashing for your respective board.
When finished follow the [setup instructions](setup.md).

## Boards
### Pro Micro nRF52840 (promicro_nrf52840/nrf52840/uf2)
#### [adafruit-nrfutil](https://github.com/adafruit/Adafruit_nRF52_nrfutil) (extremly reliable)
1. Put the board in `DFU mode`
2. Update the [booloader](https://github.com/pdcook/nRFMicro-Arduino-Core/raw/refs/heads/main/bootloader/SuperMini_nRF52840/SuperMini_nRF52840_bootloader-1.0.0_s140_7.3.0.zip):
```
adafruit-nrfutil dfu serial -pkg SuperMini_nRF52840_bootloader-1.0.0_s140_7.3.0.zip -p <tty device> -b 115200 --touch 1200
```
3. Create a package
```
adafruit-nrfutil dfu genpkg --dev-type 0x0052 --sd-req 0x0123 --application zephyr.hex <package location (.zip)>
```
4. Flash the package
```
 adafruit-nrfutil dfu serial -pkg <package location (.zip)> -p <tty device> -b 115200 --singlebank
```
5. You only have to do 3 and 4 for subsequent builds. If you want to enter dfu mode from the shell just enter `dfu serial`

#### uf2
Flashing using uf2 only seems to work if you have an up-to-date bootloader. If unsure follow 1 and 2 from `adafruit-nrfutil`
1. Download the `uf2` file (if built: `build/zephyr/zephyr.uf2`)
2. Drag the file onto the boards partition while the board is in `DFU mode`

#### DFU mode
From [Zephyr docs](https://docs.zephyrproject.org/latest/boards/others/promicro_nrf52840/doc/index.html#flashing): 
1. Reset the board into the bootloader by bridging ground and RST 2 times quickly
2. The status LED should start a fade pattern, signalling the bootloader is running.
