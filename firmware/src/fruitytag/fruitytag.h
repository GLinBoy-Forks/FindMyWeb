#include "tag/tag.h"
#include <stdbool.h>

typedef struct {
  uint32_t adv_time;
  uint8_t bt_address[6];
  tag_advertisement adv;
} fruity_tag;

int fruitytag_init(fruity_tag* tag, uint32_t adv_time_ms, uint8_t* public_key, size_t public_key_len);
int fruitytag_advertise(fruity_tag* tag, bool mac_reversed);
int fruitytag_stop();
