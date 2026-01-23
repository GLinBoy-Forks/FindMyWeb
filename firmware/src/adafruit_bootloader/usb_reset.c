#include "adafruit_bootloader.h"
#include <zephyr/device.h>
#include <zephyr/drivers/uart/cdc_acm.h>
#include <zephyr/drivers/usb/usb_dc.h>

static void reset_into_dfu(const struct device* dev, uint32_t rate) {
  if (rate != 1200) {
    return;
  }

  // wait a bit before killing serial device so nrfutil doesn't complain
  k_msleep(10);

  usb_dc_detach();
  adafruit_reboot_into(DFU_MAGIC_SERIAL_ONLY_RESET);
}

static int usb_reset_init() {
  const struct device* dev = device_get_binding("board_cdc_acm_uart");

  if (dev == NULL) {
    return -ENODEV;
  }

  return cdc_acm_dte_rate_callback_set(dev, reset_into_dfu);
}

SYS_INIT(usb_reset_init, APPLICATION, 0);
