cmake_minimum_required(VERSION 3.20.0)

find_package(Zephyr HINTS $ENV{ZEPHYR_BASE})
project(fruitytag)

target_sources(app PRIVATE src/main.c)

if(CONFIG_NRF52_ADAFRUIT_BOOTLOADER)
    target_sources(app PRIVATE src/usb_reset.c)
endif()
