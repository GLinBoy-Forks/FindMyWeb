#include "keystore/keystore.h"
#include <stdlib.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/shell/shell.h>
#include <zephyr/sys/base64.h>
#include <zephyr/sys/reboot.h>

LOG_MODULE_REGISTER(fruitytag_cmd);
static uint8_t temp_pub_key[KEYSTORE_PUBKEY_SIZE];

static void reboot_in(uint8_t sec) {
  k_msleep(sec * 1000);

  LOG_INF("Rebooting");
  sys_reboot(SYS_REBOOT_COLD);
}

static int handle_set_public_key(const struct shell* shell, size_t argc, char** argv) {
  int err;
  size_t b64_buf_size;

  err = base64_decode(temp_pub_key, KEYSTORE_PUBKEY_SIZE, &b64_buf_size, argv[1], strlen(argv[1]));
  if (err == -EINVAL) {
    shell_error(shell, "Not a base64 string");
    return err;
  } else if (err) {
    shell_error(shell, "Unkown error occured during decoding: %d", err);
    return err;
  } else if (b64_buf_size != KEYSTORE_PUBKEY_SIZE) {
    shell_error(shell, "Base64 string must decode to %d bytes given: %d", KEYSTORE_PUBKEY_SIZE, b64_buf_size);
    return err;
  }

  shell_print(shell, "Saving to keystore");

  err = keystore_set_pubkey(temp_pub_key, KEYSTORE_PUBKEY_SIZE);
  if (err) {
    shell_error(shell, "Couldn't save public key: %d", err);
    return err;
  }

  shell_print(shell, "Saved.");
  shell_print(shell, "Rebooting in 2s.");
  reboot_in(2);
  return 0;
}

static int handle_get_public_key(const struct shell* shell, size_t argc, char** argv) {
  int err;
  size_t b64_buf_size;

  err = keystore_get_pubkey(temp_pub_key, sizeof(temp_pub_key));
  if (err == -ENOENT) {
    shell_error(shell, "Device not configured yet");
    return err;
  } else if (err) {
    shell_error(shell, "Couldn't load pubkey: %d", err);
    return err;
  }

  err = base64_encode(NULL, 0, &b64_buf_size, temp_pub_key, sizeof(temp_pub_key));
  if (err && err != -ENOMEM) { // No mem is expected as size = 0
    shell_error(shell, "Couldn't get base64 string size: %d", err);
    return err;
  }

  char base64_str[b64_buf_size];

  err = base64_encode(base64_str, b64_buf_size, &b64_buf_size, temp_pub_key, sizeof(temp_pub_key));
  if (err) {
    shell_error(shell, "Couldn't convert public key to base64 string");
    return err;
  }

  shell_print(shell, "Key: %s", base64_str);

  return 0;
}

static int handle_factory_reset(const struct shell* shell, size_t argc, char** argv) {
  int err;
  shell_print(shell, "Factory resetting");

  err = keystore_reset();
  if (err) {
    shell_error(shell, "Couldn't reset keystore: %d", err);
    return err;
  }

  shell_print(shell, "Rebooting in 2s");
  reboot_in(2);
  return 0;
}

SHELL_STATIC_SUBCMD_SET_CREATE(fruitytag_key,
                               SHELL_CMD_ARG(set, NULL, "set a new public key (base64)",
                                             handle_set_public_key, 2, 0),
                               SHELL_CMD_ARG(get, NULL, "get the current public key",
                                             handle_get_public_key, 1, 0),
                               SHELL_SUBCMD_SET_END);

SHELL_STATIC_SUBCMD_SET_CREATE(fruitytag_cmds,
                               SHELL_CMD_ARG(key, &fruitytag_key, "get/set public key",
                                             handle_set_public_key, 2, 0),
                               SHELL_CMD_ARG(reset, NULL, "factory resets the device", handle_factory_reset, 1, 0),
                               SHELL_SUBCMD_SET_END);
SHELL_CMD_REGISTER(fruitytag, &fruitytag_cmds, "FruityTag commands", NULL);
