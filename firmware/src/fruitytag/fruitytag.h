#pragma once
#include "tag/tag.h"
#include <stdbool.h>
#include <sys/types.h>

typedef struct {
  uint32_t adv_time;

  uint8_t bt_id;

  tag_advertisement adv;
} fruity_tag;

int fruitytag_init(fruity_tag* tag, uint32_t adv_time_ms);
int fruitytag_start(fruity_tag* tag, bool restart);
int fruitytag_update_battery(fruity_tag* tag, uint8_t battery_percent);
int fruitytag_update_pubkey(fruity_tag* tag, uint8_t* public_key, ssize_t public_key_len);
int fruitytag_stop();
