#include "fruitytag.h"
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/controller.h>
#include <zephyr/logging/log.h>

#define MS_TO_ADV_INTERVAL(ms) ms / 0.625

LOG_MODULE_REGISTER(fruitytag, CONFIG_FRUITYTAG_LOG_LEVEL);

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

int fruitytag_advertise(fruity_tag* tag, bool mac_reversed) {
  int err = 0;
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

  const struct bt_le_adv_param* adv_params = BT_LE_ADV_PARAM(BT_LE_ADV_OPT_USE_IDENTITY, tag->adv_time, tag->adv_time, NULL);

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
  return 0;
}
