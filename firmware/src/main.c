#include "app_version.h"
#include "fruitytag/fruitytag.h"
#include "keystore/keystore.h"

#ifdef CONFIG_RAM_POWER_DOWN_LIBRARY
#include <ram_pwrdn.h>
#endif

#include <stdio.h>
#include <stdlib.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/settings/settings.h>
#include <zephyr/shell/shell.h>
#include <zephyr/sys/base64.h>
#include <zephyr/sys/reboot.h>

LOG_MODULE_REGISTER(app);

#define ERROR_BLINK_TIME 100, 100
#define NO_PUBKEY_BLINK_TIME 1000, 0
#define OK_BLINK_TIME 100, 15000

#if DT_HAS_ALIAS(led0)
#define LED0_NODE DT_ALIAS(led0)
static const struct gpio_dt_spec led = GPIO_DT_SPEC_GET(LED0_NODE, gpios);

int blink_forever(uint32_t time_on_ms, uint32_t time_off_ms) {
  // Todo: use a separate thread for blink
  int err;

  err = gpio_is_ready_dt(&led);
  if (!err) {
    LOG_ERR("Couldn't configure led: %d", err);
    return 0;
  }

  while (1) {
    err = gpio_pin_configure_dt(&led, GPIO_OUTPUT_ACTIVE);
    if (err < 0) {
      return 0;
    }
    k_msleep(time_on_ms);

    err = gpio_pin_configure_dt(&led, GPIO_OUTPUT_INACTIVE);
    if (err < 0) {
      return 0;
    }
    k_msleep(time_off_ms);
  }
}
#else
int blink_forever(uint32_t time_on_ms, uint32_t time_off_ms) { return 0; };
#endif

void reboot_in(uint8_t sec) {
  k_msleep(sec * 1000);

  LOG_INF("Rebooting");
  sys_reboot(SYS_REBOOT_COLD);
}

#ifdef CONFIG_SHELL

static int handle_set_public_key(const struct shell* shell, size_t argc, char** argv) {
  int err;
  size_t b64_buf_size;
  uint8_t* pub_key = malloc(KEYSTORE_PUBKEY_SIZE);

  err = base64_decode(pub_key, KEYSTORE_PUBKEY_SIZE, &b64_buf_size, argv[1], strlen(argv[1]));
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

  err = keystore_set_pubkey(pub_key, KEYSTORE_PUBKEY_SIZE);
  if (err) {
    shell_error(shell, "Couldn't save public key: %d", err);
    return err;
  }
  free(pub_key);

  shell_print(shell, "Saved.");
  shell_print(shell, "Rebooting in 2s.");
  reboot_in(2);
  return 0;
}

static int handle_get_public_key(const struct shell* shell, size_t argc, char** argv) {
  int err;
  size_t b64_buf_size;
  uint8_t* pub_key = malloc(KEYSTORE_PUBKEY_SIZE);

  err = keystore_get_pubkey(pub_key, KEYSTORE_PUBKEY_SIZE);
  if (err == -ENOENT) {
    shell_error(shell, "Device not configured yet");
    return err;
  } else if (err) {
    shell_error(shell, "Couldn't load pubkey: %d", err);
    return err;
  }

  err = base64_encode(NULL, 0, &b64_buf_size, pub_key, KEYSTORE_PUBKEY_SIZE);
  if (err && err != -ENOMEM) { // No mem is expected as size = 0
    shell_error(shell, "Couldn't get base64 string size: %d", err);
    return err;
  }

  char* base64_str = calloc(1, b64_buf_size);
  if (!base64_str) {
    shell_error(shell, "Couldn't allocate buffer for base64 string");
    return -ENOMEM;
  }

  err = base64_encode(base64_str, b64_buf_size, &b64_buf_size, pub_key, KEYSTORE_PUBKEY_SIZE);
  if (err) {
    shell_error(shell, "Couldn't convert public key to base64 string");
    return err;
  }

  shell_print(shell, "Key: %s", base64_str);
  free(base64_str);

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
#endif // CONFIG_SHELL

int main(void) {
  int err;
  fruity_tag tag;

  printk("FruityTag v%s\n", APP_VERSION_STRING); // Using printk so it will always be shown

  uint8_t* pub_key = malloc(KEYSTORE_PUBKEY_SIZE);

  err = settings_subsys_init();
  if (err) {
    LOG_ERR("Couldn't initialize settings subsys: %d", err);
    goto exit_and_blink;
  }

  err = keystore_register();
  if (err) {
    LOG_ERR("Couldn't register keystore: %d", err);
    goto exit_and_blink;
  }

  err = settings_load();
  if (err) {
    LOG_ERR("Couldn't load settings: %d", err);
    goto exit_and_blink;
  }

  err = keystore_get_pubkey(pub_key, KEYSTORE_PUBKEY_SIZE);
  if (err == -ENOENT) {
    LOG_ERR("Device not setup yet. Setup using `fruitytag key set <base64 key>`");
    free(pub_key);
    blink_forever(NO_PUBKEY_BLINK_TIME);
    return 0;
  }

  err = fruitytag_init(&tag, CONFIG_FRUITYTAG_ADVERTISEMENT_INTERVAL, pub_key, KEYSTORE_PUBKEY_SIZE);
  if (err) {
    LOG_ERR("Couldn't initalize fruity tag: %d", err);
    goto exit_and_blink;
  }

  err = fruitytag_advertise(&tag, true, true);
  if (err) {
    LOG_ERR("Couldn't start advertising: %d", err);
    goto exit_and_blink;
  }

exit_and_blink:
  free(pub_key);

#ifdef CONFIG_RAM_POWER_DOWN_LIBRARY
  power_down_unused_ram();
#endif

  if (err) {
    blink_forever(ERROR_BLINK_TIME);
  } else {
    blink_forever(OK_BLINK_TIME);
  }
  return 0;
}
