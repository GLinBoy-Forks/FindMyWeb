#include "adafruit_bootloader.h"
#include <zephyr/bluetooth/gatt.h>
#include <zephyr/bluetooth/uuid.h>

#define BT_UUID_OTA_BOOT_SERVICE_VAL \
  BT_UUID_128_ENCODE(0x6c6b72c0, 0x9748, 0x41fa, 0xb893, 0xa8ff961d73dd)

static const struct bt_uuid_128 boot_ota_uuid
    = BT_UUID_INIT_128(BT_UUID_OTA_BOOT_SERVICE_VAL);

static ssize_t write_ota_boot(struct bt_conn* conn,
                              const struct bt_gatt_attr* attr,
                              const void* buf, uint16_t len, uint16_t offset,
                              uint8_t flags) {
  uint8_t* data = (uint8_t*)buf;
  if (len > 0 && data[0] == 0x01) {
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
