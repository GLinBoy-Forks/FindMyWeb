#include "usb_reset.h"

#include <zephyr/device.h>
#include <zephyr/drivers/retained_mem.h>
#include <zephyr/drivers/uart/cdc_acm.h>
#include <zephyr/drivers/usb/usb_dc.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/reboot.h>

static const struct device *gpregret1_dev = DEVICE_DT_GET(DT_NODELABEL(gpregret1));

// Modes as described in:
// https://github.com/adafruit/Adafruit_nRF52_Bootloader/blob/31c3081668c0ffe0215c125b88d3cb5c2447050e/src/main.c#L109
#define DFU_MAGIC_OTA_APPJUM 0xB1 // 0xB1
#define DFU_MAGIC_OTA_RESET 0xA8
#define DFU_MAGIC_SERIAL_ONLY_RESET 0x4e
#define DFU_MAGIC_UF2_RESET 0x57
#define DFU_MAGIC_SKIP 0x6d

static void reset_into_dfu(const struct device *dev, uint32_t rate) {
    char retention_value = DFU_MAGIC_SERIAL_ONLY_RESET;

    if (rate != 1200) {
        return;
    }


    // wait a bit before killing serial device so nrfutil doesn't complain
    k_msleep(10);

    if (!device_is_ready(gpregret1_dev)) {
        return;
    }

    usb_dc_detach();

    retained_mem_write(gpregret1_dev, 0, &retention_value, 1);
    sys_reboot(SYS_REBOOT_COLD);
}


static int usb_reset_init() {
    const struct device *dev = device_get_binding("board_cdc_acm_uart");

    if (dev == NULL) {
        return -ENODEV;
    }

    return cdc_acm_dte_rate_callback_set(dev, reset_into_dfu);
}


SYS_INIT(usb_reset_init, APPLICATION, 0);
