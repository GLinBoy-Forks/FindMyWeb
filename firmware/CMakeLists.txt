cmake_minimum_required(VERSION 3.20.0)

find_package(Zephyr HINTS $ENV{ZEPHYR_BASE})
project(fruitytag)

target_include_directories(app PRIVATE src)

target_sources(app PRIVATE src/main.c)
target_sources(app PRIVATE src/tag/tag.c)
target_sources(app PRIVATE src/keystore/keystore.c)
target_sources(app PRIVATE src/fruitytag/fruitytag.c)

target_sources(app PRIVATE src/battery_thread/battery_thread.c)

target_sources(app PRIVATE src/blink_handler/blink_handler.c)

if(CONFIG_NRF52_ADAFRUIT_BOOTLOADER)
    target_sources(app PRIVATE src/adafruit_bootloader/adafruit_bootloader.c)
    target_sources(app PRIVATE src/adafruit_bootloader/ble_srv_ota_reset.c)
    target_sources(app PRIVATE src/usb_reset.c)
endif()

if(CONFIG_SHELL)
    target_sources(app PRIVATE src/cmds.c)
endif()
