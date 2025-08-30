#include "fruitytag.h"

#include <sys/types.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/bluetooth/controller.h>
#include <zephyr/bluetooth/gatt.h>
#include <zephyr/bluetooth/hci.h>
#include <zephyr/bluetooth/uuid.h>
#include <zephyr/logging/log.h>

#ifdef CONFIG_NRF52_ADAFRUIT_BOOTLOADER
#include "adafruit_bootloader/adafruit_bootloader.h"
#endif

#define MS_TO_ADV_INTERVAL(ms) ms / 0.625

LOG_MODULE_REGISTER(fruitytag, CONFIG_FRUITYTAG_LOG_LEVEL);

static fruity_tag* last_advertised_tag = NULL;

int fruitytag_init(fruity_tag* tag, uint32_t adv_time_ms, uint8_t* public_key, size_t public_key_len) {
  int err = 0;
  tag_advertisement new_adv_data = TAG_ADVERTISEMENT;

  tag->adv_time = MS_TO_ADV_INTERVAL(adv_time_ms);

  err = tag_set_public_key(&new_adv_data, public_key, TAG_PUBLIC_KEY_LENGTH);
  if (err) {
    LOG_ERR("Couldn't set public key: %d", err);
    return err;
  }

  err = tag_bt_address(tag->bt_address, sizeof(tag->bt_address), public_key, public_key_len);
  if (err) {
    LOG_ERR("Couldn't get mac address: %d", err);
    return err;
  }

  tag->adv = new_adv_data;

  return err;
}

int fruitytag_advertise(fruity_tag* tag, bool mac_reversed, bool init_bt) {
  int err = 0;

  if (init_bt) {
    if (mac_reversed) {
      uint8_t rev_mac[6];
      rev_mac[0] = tag->bt_address[5];
      rev_mac[1] = tag->bt_address[4];
      rev_mac[2] = tag->bt_address[3];
      rev_mac[3] = tag->bt_address[2];
      rev_mac[4] = tag->bt_address[1];
      rev_mac[5] = tag->bt_address[0];
      bt_ctlr_set_public_addr(rev_mac);
    } else {
      bt_ctlr_set_public_addr(tag->bt_address);
    }

    err = bt_enable(NULL);
    if (err) {
      LOG_ERR("Bluetooth init failed: %d", err);
      return 0;
    }
  }

  const struct bt_le_adv_param* adv_params = BT_LE_ADV_PARAM(BT_LE_ADV_OPT_USE_IDENTITY | BT_LE_ADV_OPT_CONN, tag->adv_time, tag->adv_time, NULL);

  uint8_t* adv_ptr = (uint8_t*)&tag->adv;
  // Skip the first two bytes as type and length get set by zephyr
  struct bt_data ad[] = {
    BT_DATA(BT_DATA_MANUFACTURER_DATA, adv_ptr + 2, sizeof(tag->adv) - 2),
  };

  err = bt_le_adv_start(adv_params, ad, ARRAY_SIZE(ad), NULL, 0);
  if (err) {
    LOG_ERR("Failed to start advertising: %d", err);
    return err;
  }

  if (last_advertised_tag != tag) {
    last_advertised_tag = tag;
  }

  return err;
}

int fruitytag_stop() {
  int err;
  err = bt_le_adv_stop();
  if (err) {
    LOG_ERR("Couldn't stop advertising: %d", err);
    return err;
  }
  err = bt_disable();
  if (err) {
    LOG_ERR("Couldn't disable bluetooth: %d", err);
    return err;
  }
  last_advertised_tag = NULL;

  return 0;
}

#ifdef CONFIG_NRF52_ADAFRUIT_BOOTLOADER
#define BT_UUID_OTA_BOOT_SERVICE_VAL \
  BT_UUID_128_ENCODE(0x6c6b72c0, 0x9748, 0x41fa, 0xb893, 0xa8ff961d73dd)

static const struct bt_uuid_128 boot_ota_uuid = BT_UUID_INIT_128(BT_UUID_OTA_BOOT_SERVICE_VAL);

static ssize_t write_ota_boot(struct bt_conn* conn,
                              const struct bt_gatt_attr* attr,
                              const void* buf, uint16_t len, uint16_t offset,
                              uint8_t flags) {
  uint8_t* data = (uint8_t*)buf;
  if (len > 0 && data[0] == 0x01) {
    LOG_INF("Rebooting to OTA bootloader");
    adafruit_reboot_into(DFU_MAGIC_OTA_RESET);
  }

  return len;
}

BT_GATT_SERVICE_DEFINE(ota_boot_svc,
                       BT_GATT_PRIMARY_SERVICE(&boot_ota_uuid),
                       BT_GATT_CHARACTERISTIC(&boot_ota_uuid.uuid,
                                              BT_GATT_CHRC_WRITE_WITHOUT_RESP,
                                              BT_GATT_PERM_WRITE,
                                              NULL, write_ota_boot, NULL), );
#endif // CONFIG_NRF52_ADAFRUIT_BOOTLOADER

static void bt_connected(struct bt_conn* conn, uint8_t err) {
  if (err) {
    LOG_ERR("Connection failed, err 0x%02x %s", err, bt_hci_err_to_str(err));
  } else {
    LOG_INF("Connected");
  }
}

static void bt_disconnected(struct bt_conn* conn, uint8_t reason) {
  LOG_INF("Disconnected, reason 0x%02x %s", reason, bt_hci_err_to_str(reason));
}

static void bt_recycled() {
  if (last_advertised_tag) {
    LOG_INF("Readvertising last tag");
    fruitytag_advertise(last_advertised_tag, false, false);
  }
}

BT_CONN_CB_DEFINE(conn_callbacks) = {
  .connected = bt_connected,
  .disconnected = bt_disconnected,
  .recycled = bt_recycled,
};
