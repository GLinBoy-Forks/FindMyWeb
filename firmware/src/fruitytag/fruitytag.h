#pragma once
#include "tag/tag.h"
#include <stdbool.h>
#include <sys/types.h>

typedef struct {
  uint32_t adv_time;

  uint8_t bt_address[6];
  bool bt_address_rev;

  tag_advertisement adv;
} fruity_tag;

int fruitytag_init(fruity_tag* tag, uint32_t adv_time_ms, bool addr_reversed);
int fruitytag_start(fruity_tag* tag, bool restart);
int fruitytag_update(fruity_tag* tag, uint8_t* public_key, ssize_t public_key_len, int8_t battery_percent);
int fruitytag_stop();
