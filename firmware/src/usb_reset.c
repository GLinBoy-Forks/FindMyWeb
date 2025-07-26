#include "usb_reset.h"

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/retained_mem.h>
#include <zephyr/drivers/usb/usb_dc.h>
#include <zephyr/drivers/uart/cdc_acm.h>
#include <zephyr/sys/reboot.h>

static const struct device *gpregret1_dev = DEVICE_DT_GET(DT_NODELABEL(gpregret1));

static void reset_into_dfu(const struct device *dev, uint32_t rate) {
    char retention_value = 0x4e;

    if (rate != 1200) {
        return;
    }

    if (!device_is_ready(gpregret1_dev)) {
        return;
    }

    usb_dc_detach();

    retained_mem_write(gpregret1_dev, 0, &retention_value, 1);
    sys_reboot(SYS_REBOOT_COLD);
}


static int usb_reset_init() {
    const struct device *dev =
		device_get_binding("board_cdc_acm_uart");


    if (dev == NULL) {
        return -ENODEV;
   	}

   	return cdc_acm_dte_rate_callback_set(dev, reset_into_dfu);

}


SYS_INIT(usb_reset_init, APPLICATION, 0);
