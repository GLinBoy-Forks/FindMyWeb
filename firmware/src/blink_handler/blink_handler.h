#pragma once
#include <stdint.h>

struct led_timing {
  uint32_t time_on_ms;
  uint32_t time_off_ms;
};

void blink_handler_set_pattern(struct led_timing* timing);
