#include <errno.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef struct __attribute__((__packed__)) {
  uint8_t length;
  uint8_t type;
  uint16_t company_id;
  uint8_t payload_type;
  uint8_t payload_size;
  uint8_t state;
  uint8_t data[22];
  uint8_t first_two_bits;
  uint8_t hint;
} tag_advertisement;

typedef enum {
  TAG_BATT_FULL = 0b00000000,
  TAG_BATT_MEDIUM = 0b01000000,
  TAG_BATT_LOW = 0b10000000,
  TAG_BATT_CRITICAL = 0b11000000,
} tag_state;

typedef enum {
  TAG_NORMAL_PAYLOAD = 0x12,
} tag_payload_type;

#define TAG_PUBLIC_KEY_LENGTH 28
#define TAG_BT_ADDRESS_LENGTH 6

#define TAG_COMPANY_ID 0x004c // Apple

#define DEFAULT_TAG_ADVERTISEMENT {                                                                                                 \
  0x1e,                                                                                                                             \
  0xff,                                                                                                                             \
  TAG_COMPANY_ID,                                                                                                                   \
  TAG_NORMAL_PAYLOAD,                                                                                                               \
  0x19,                                                                                                                             \
  TAG_BATT_FULL,                                                                                                                    \
  { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 }, \
  0x00,                                                                                                                             \
  0x00                                                                                                                              \
}

int tag_set_public_key(tag_advertisement* adv_data, uint8_t* public_key, size_t public_key_len);
int tag_bt_address(uint8_t* address, size_t address_len, uint8_t* public_key, size_t public_key_len, bool rev_mac);
