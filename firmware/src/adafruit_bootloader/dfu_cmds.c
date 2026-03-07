#include "adafruit_bootloader.h"
#include <zephyr/shell/shell.h>

static int handle_dfu_ble(const struct shell* shell, size_t argc, char** argv) {
  shell_print(shell, "Rebooting into ble dfu mode");
  adafruit_reboot_into(DFU_MAGIC_OTA_RESET);
  return 0;
}

static int handle_dfu_serial(const struct shell* shell, size_t argc, char** argv) {
  shell_print(shell, "Rebooting into serial dfu mode");
  adafruit_reboot_into(DFU_MAGIC_SERIAL_ONLY_RESET);
  return 0;
}

static int handle_dfu_uf2(const struct shell* shell, size_t argc, char** argv) {
  shell_print(shell, "Rebooting into serial dfu mode");
  adafruit_reboot_into(DFU_MAGIC_UF2_RESET);
  return 0;
}

SHELL_STATIC_SUBCMD_SET_CREATE(dfu_cmds,
                               SHELL_CMD(ble, NULL, "enter ble dfu mode", handle_dfu_ble),
                               SHELL_CMD(serial, NULL, "enter serial dfu mode", handle_dfu_serial),
                               SHELL_CMD(uf2, NULL, "enter uf2 dfu mode", handle_dfu_uf2),
                               SHELL_SUBCMD_SET_END);
SHELL_CMD_REGISTER(dfu, &dfu_cmds, "DFU commands for devices with an Adafruit NRF52 bootloader", NULL);
