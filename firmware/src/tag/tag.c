#include "tag.h"

int tag_set_public_key(tag_advertisement* adv_data, uint8_t* public_key, size_t public_key_len) {
  if (public_key_len != TAG_PUBLIC_KEY_LENGTH) {
    return -EINVAL;
  }

  memcpy(&adv_data->data, &public_key[6], sizeof(adv_data->data));
  adv_data->first_two_bits = public_key[0] >> 6;
  return 0;
}

int tag_bt_address(uint8_t* address, size_t address_len, uint8_t* public_key, size_t public_key_len) {
  if (public_key_len != TAG_PUBLIC_KEY_LENGTH) {
    return -EINVAL;
  }
  if (address_len != TAG_BT_ADDRESS_LENGTH) {
    return -EINVAL;
  }

  address[0] = public_key[0] | 0b11000000;
  address[1] = public_key[1];
  address[2] = public_key[2];
  address[3] = public_key[3];
  address[4] = public_key[4];
  address[5] = public_key[5];

  return 0;
}
