cmake_minimum_required(VERSION 3.20.0)

set(BOARD promicro_nrf52840/nrf52840/uf2)
find_package(Zephyr HINTS $ENV{ZEPHYR_BASE})
project(fruitytag)

target_sources(app PRIVATE src/main.c)
target_sources(app PRIVATE src/usb_reset.c)
