#include "adafruit_bootloader.h"

static const struct device* gpregret1_dev = DEVICE_DT_GET(DT_NODELABEL(gpregret1));

void adafruit_reboot_into(ADAFRUIT_DFU_MODE mode) {
  if (!device_is_ready(gpregret1_dev)) {
    return;
  }

  retained_mem_write(gpregret1_dev, 0, &mode, 1);
  sys_reboot(SYS_REBOOT_COLD);
}
