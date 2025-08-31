#include "blink_handler/blink_handler.h"

struct led_timing error_blink_timing = {
  .time_on_ms = 100,
  .time_off_ms = 100
};

struct led_timing not_setup_blink_timing = {
  .time_on_ms = 1000,
  .time_off_ms = 0
};

struct led_timing ok_blink_timing = {
  .time_on_ms = 100,
  .time_off_ms = 15000
};

struct led_timing connected_blink_timing = {
  .time_on_ms = 500,
  .time_off_ms = 500
};
