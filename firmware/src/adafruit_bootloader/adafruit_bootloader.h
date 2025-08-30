#include <zephyr/drivers/retained_mem.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/reboot.h>

// Modes as described in:
// https://github.com/adafruit/Adafruit_nRF52_Bootloader/blob/31c3081668c0ffe0215c125b88d3cb5c2447050e/src/main.c#L109
typedef enum {
  DFU_MAGIC_OTA_APPJUM = 0xB1,
  DFU_MAGIC_OTA_RESET = 0xA8,
  DFU_MAGIC_SERIAL_ONLY_RESET = 0x4e,
  DFU_MAGIC_UF2_RESET = 0x57,
  DFU_MAGIC_SKIP = 0x6d,
} ADAFRUIT_DFU_MODE;

void adafruit_reboot_into(ADAFRUIT_DFU_MODE mode);
