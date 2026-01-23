#include "fruitytag.h"

#include <sys/types.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/bluetooth/hci.h>
#include <zephyr/logging/log.h>

#define MS_TO_ADV_INTERVAL(ms) ms / 0.625

LOG_MODULE_REGISTER(fruitytag, CONFIG_FRUITYTAG_LOG_LEVEL);

static fruity_tag* last_advertised_tag = NULL;

int fruitytag_init(fruity_tag* tag, uint32_t adv_time_ms) {
  int err = 0;
  tag_advertisement default_adv = DEFAULT_TAG_ADVERTISEMENT;
  tag->adv = default_adv;

  tag->adv_time = MS_TO_ADV_INTERVAL(adv_time_ms);
  tag->bt_id = BT_ID_DEFAULT;
  return err;
}

int fruitytag_start(fruity_tag* tag, bool restart) {
  int err = 0;

  uint8_t* adv_ptr = (uint8_t*)&tag->adv;
  // Skip the first two bytes as type and length get set by zephyr
  struct bt_data ad[] = {
    BT_DATA(BT_DATA_MANUFACTURER_DATA, adv_ptr + 2, sizeof(tag->adv) - 2),
  };

  if (restart) {
    const struct bt_le_adv_param adv_params = {
      .id = BT_ID_DEFAULT,
      .sid = 0,
      .secondary_max_skip = 0,
      .options = BT_LE_ADV_OPT_USE_IDENTITY | BT_LE_ADV_OPT_CONN,
      .interval_min = tag->adv_time,
      .interval_max = tag->adv_time,
      .peer = NULL,
    };

    err = bt_le_adv_stop();
    if (err) {
      LOG_WRN("Couldn't stop advertising. Continuing...");
    }

    err = bt_le_adv_start(&adv_params, ad, ARRAY_SIZE(ad), NULL, 0);
    if (err) {
      LOG_ERR("Couldn't start advertising: %d", err);
      return err;
    }

  } else {
    err = bt_le_adv_update_data(ad, ARRAY_SIZE(ad), NULL, 0);
    if (err) {
      LOG_ERR("Couldn't update advertising: %d", err);
      return err;
    }
  }
  if (last_advertised_tag != tag) {
    last_advertised_tag = tag;
  }

  return err;
}

int fruitytag_update_battery(fruity_tag* tag, uint8_t battery_percent) {
  if (0 <= battery_percent && battery_percent <= 10) {
    tag->adv.state = TAG_BATT_CRITICAL;
  } else if (10 < battery_percent && battery_percent <= 25) {
    tag->adv.state = TAG_BATT_LOW;
  } else if (25 < battery_percent && battery_percent <= 75) {
    tag->adv.state = TAG_BATT_MEDIUM;
  } else if (battery_percent > 75) {
    tag->adv.state = TAG_BATT_FULL;
  }
  return 0;
}

int fruitytag_update_pubkey(fruity_tag* tag, uint8_t* public_key, ssize_t public_key_len) {
  int err = 0;
  err = tag_set_public_key(&tag->adv, public_key, public_key_len);
  if (err) {
    LOG_ERR("Couldn't set public key: %d", err);
    return err;
  }

  if (tag->bt_id != BT_ID_DEFAULT) {
    err = bt_id_delete(tag->bt_id);
    if (err) {
      LOG_WRN("Couldn't delete old identity: %d\n", err);
    }
  }

  bt_addr_le_t addr;
  addr.type = BT_ADDR_LE_RANDOM;

  err = tag_bt_address(addr.a.val, sizeof(addr.a.val), public_key, public_key_len, true);
  if (err) {
    LOG_ERR("Couldn't get bt address: %d", err);
    return err;
  }

  err = bt_id_create(&addr, NULL);
  if (err < 0) {
    LOG_ERR("Couldn't create new identity for %x:%x:%x:%x:%x:%x: %d\n", addr.a.val[0], addr.a.val[1], addr.a.val[2], addr.a.val[3], addr.a.val[4], addr.a.val[5], err);
    return err;
  }
  tag->bt_id = err;

  return err;
}

int fruitytag_stop() {
  int err;
  err = bt_le_adv_stop();
  if (err) {
    LOG_ERR("Couldn't stop advertising: %d", err);
    return err;
  }

  last_advertised_tag = NULL;

  return 0;
}
