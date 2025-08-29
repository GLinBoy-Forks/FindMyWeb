cmake_minimum_required(VERSION 3.20.0)

find_package(Zephyr HINTS $ENV{ZEPHYR_BASE})
project(fruitytag)

target_include_directories(app PRIVATE src)

target_sources(app PRIVATE src/main.c)
target_sources(app PRIVATE src/tag/tag.c)
target_sources(app PRIVATE src/keystore/keystore.c)
target_sources(app PRIVATE src/fruitytag/fruitytag.c)

if(CONFIG_NRF52_ADAFRUIT_BOOTLOADER)
    target_sources(app PRIVATE src/usb_reset.c)
endif()
