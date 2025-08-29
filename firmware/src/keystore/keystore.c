// Todo: use https://docs.zephyrproject.org/latest/services/storage/secure_storage/index.html
#include "keystore/keystore.h"
#include <errno.h>
#include <inttypes.h>
#include <stdlib.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/settings/settings.h>
#include <zephyr/sys/mutex.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/reboot.h>

LOG_MODULE_REGISTER(keystore, CONFIG_KEYSTORE_LOG_LEVEL);

static const char pubkey_store_name[] = "keystore/pubkey";

static uint8_t* public_key = NULL;
static bool key_set = false;

static void keystore_clear_pubkey() {
  if (!public_key) {
    public_key = (uint8_t*)malloc(KEYSTORE_PUBKEY_SIZE);
  }
  memset(public_key, 0, KEYSTORE_PUBKEY_SIZE);
  key_set = false;
}

static int keystore_settings_set(const char* name, size_t len, settings_read_cb read_cb, void* cb_arg) {
  const char* next;
  int rc;

  if (settings_name_steq(name, "pubkey", &next) && !next) {
    if (len != KEYSTORE_PUBKEY_SIZE) {
      return -EINVAL;
    }
    keystore_clear_pubkey();

    rc = read_cb(cb_arg, public_key, KEYSTORE_PUBKEY_SIZE);

    if (rc >= 0) {
      LOG_HEXDUMP_DBG(public_key, len, "Found public key:");
      key_set = true;
      return 0;
    }
    return rc;
  }

  return -ENOENT;
}

struct settings_handler keystore_conf = {
  .name = "keystore",
  .h_set = keystore_settings_set
};

int keystore_register() {
  keystore_clear_pubkey();
  return settings_register(&keystore_conf);
}

int keystore_set_pubkey(uint8_t* new_pub_key, size_t len) {
  LOG_HEXDUMP_DBG(new_pub_key, len, "New public key:");

  int err;

  if (len != KEYSTORE_PUBKEY_SIZE) {
    return -EINVAL;
  }

  err = settings_save_one(pubkey_store_name, new_pub_key, KEYSTORE_PUBKEY_SIZE);
  if (err) {
    LOG_ERR("Cannot save settings: %d", err);
    return err;
  }

  keystore_clear_pubkey();

  memcpy(public_key, new_pub_key, KEYSTORE_PUBKEY_SIZE);
  return 0;
}

int keystore_get_pubkey(uint8_t* pub_key, size_t len) {
  ssize_t actual_size;

  if (len != KEYSTORE_PUBKEY_SIZE) {
    return -EINVAL;
  }

  if (!key_set) {
    keystore_clear_pubkey();

    actual_size = settings_load_one(pubkey_store_name, public_key, KEYSTORE_PUBKEY_SIZE);

    if (actual_size < 0) {
      LOG_ERR("Couldn't load public key: %d", actual_size);
      keystore_clear_pubkey();
      return actual_size;
    } else if (actual_size != KEYSTORE_PUBKEY_SIZE) {
      LOG_ERR("Couldn't load public key doesn't match required length: %d", actual_size);
      keystore_clear_pubkey();
      return -ENOENT;
    }
    key_set = true;
  }

  memcpy(pub_key, public_key, KEYSTORE_PUBKEY_SIZE);
  return 0;
}

int keystore_reset() {
  int err;
  keystore_clear_pubkey();

  err = settings_delete(pubkey_store_name);
  if (err) {
    LOG_ERR("Couldn't delete pubkey: %d", err);
    return err;
  }

  return 0;
}
