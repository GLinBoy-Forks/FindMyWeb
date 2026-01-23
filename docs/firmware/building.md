# Building a FindMy compatible tracker
For more infos look at the [Zephyr docs](https://docs.zephyrproject.org/latest/develop/west/build-flash-debug.html)
## Prerequisites
1. A board compatible with [Zephyr](https://docs.zephyrproject.org/latest/boards/index.html)
2. [Zephyr SDK](https://docs.zephyrproject.org/latest/develop/getting_started/index.html) (or [nRF Connect SDK](https://docs.nordicsemi.com/bundle/ncs-latest/page/nrf/installation/install_ncs.html) if you want to build for devices which have a Nordic Semiconductor MCU)


## Building
1. Enable the sdk:
```
source <zephyr sdk location>/.venv/bin/activate
source <zephyr sdk location>/zephyr/zephyr-env.sh
```
2. Get the necessary files:
```
git clone https://codeberg.org/Misom/FindMyWeb
cd FinMyWeb/firmware
```
3. Build the firmware for your board
```
west build -b <your-board-name> .
```
4. [Flash](flashing.md) the firmware
