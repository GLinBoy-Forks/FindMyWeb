#include "app_version.h"
#include "blink_handler/blink_handler.h"
#include "blink_timings.h"
#include "fruitytag/fruitytag.h"
#include "keystore/keystore.h"
#include <stdio.h>

#ifdef CONFIG_RAM_POWER_DOWN_LIBRARY
#include <ram_pwrdn.h>
#endif

#include "battery_thread/battery_thread.h"
#include <stdlib.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/bluetooth/controller.h>
#include <zephyr/bluetooth/hci.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/settings/settings.h>

LOG_MODULE_REGISTER(app);

static fruity_tag tag;

int main(void) {
  int err;

  printk("FruityTag v%s\n", APP_VERSION_STRING); // Using printk so it will always be shown

  uint8_t* pub_key = malloc(KEYSTORE_PUBKEY_SIZE);
  char bt_name[13];

  struct led_timing* blink_timing = &error_blink_timing;

  err = settings_subsys_init();
  if (err) {
    LOG_ERR("Couldn't initialize settings subsys: %d", err);
    goto blink_and_exit;
  }

  err = keystore_register();
  if (err) {
    LOG_ERR("Couldn't register keystore: %d", err);
    goto blink_and_exit;
  }

  err = settings_load();
  if (err) {
    LOG_ERR("Couldn't load settings: %d", err);
    goto blink_and_exit;
  }

  err = keystore_get_pubkey(pub_key, KEYSTORE_PUBKEY_SIZE);
  if (err == -ENOENT) {
    LOG_ERR("Device not setup yet. Setup using `fruitytag key set <base64 key>`");
    blink_timing = &not_setup_blink_timing;
    goto blink_and_exit;
  }

  err = fruitytag_init(&tag, CONFIG_FRUITYTAG_ADVERTISEMENT_INTERVAL);
  if (err) {
    LOG_ERR("Couldn't initalize fruity tag: %d", err);
    goto blink_and_exit;
  }

  err = fruitytag_update_pubkey(&tag, pub_key, KEYSTORE_PUBKEY_SIZE);
  if (err) {
    LOG_ERR("Couldn't update fruity tag: %d", err);
    goto blink_and_exit;
  }

  err = bt_enable(NULL);
  if (err) {
    LOG_ERR("Couldn't enable ble: %d", err);
    goto blink_and_exit;
  }

  snprintf(bt_name, sizeof(bt_name), "FruityTag-%02x", pub_key[0]);
  err = bt_set_name(bt_name);
  if (err) {
    LOG_ERR("Couldn't set name to %s", bt_name);
    goto blink_and_exit;
  }
  LOG_INF("name: %s", bt_name);

  err = fruitytag_start(&tag, true);
  if (err) {
    LOG_ERR("Couldn't start advertising: %d", err);
    goto blink_and_exit;
  }
  blink_timing = &ok_blink_timing;

blink_and_exit:
  free(pub_key);
  blink_handler_set_pattern(blink_timing);

#ifdef CONFIG_RAM_POWER_DOWN_LIBRARY
  power_down_unused_ram();
#endif

  return 0;
}

static void bt_connected(struct bt_conn* conn, uint8_t err) {
  if (err) {
    LOG_ERR("Connection failed, err 0x%02x %s", err, bt_hci_err_to_str(err));
  } else {
    LOG_INF("Connected");
    blink_handler_set_pattern(&connected_blink_timing);
  }
}

static void bt_disconnected(struct bt_conn* conn, uint8_t reason) {
  LOG_INF("Disconnected, reason 0x%02x %s", reason, bt_hci_err_to_str(reason));
}

static void bt_recycled() {
  int err;
  err = fruitytag_start(&tag, true);
  if (err) {
    LOG_ERR("Couldn't readvertise tag: %d", err);
    blink_handler_set_pattern(&error_blink_timing);
    return;
  }
  blink_handler_set_pattern(&ok_blink_timing);
}

BT_CONN_CB_DEFINE(conn_callbacks) = {
  .connected = bt_connected,
  .disconnected = bt_disconnected,
  .recycled = bt_recycled,
};

K_THREAD_DEFINE(battery_thread_id, 1024, battery_thread, &tag, NULL, NULL, 7, 0, 0);
