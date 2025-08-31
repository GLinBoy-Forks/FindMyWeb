#include <zephyr/devicetree.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/kernel.h>

#if DT_HAS_ALIAS(led0)
#include "blink_handler.h"

#define LED0_NODE DT_ALIAS(led0)
static const struct gpio_dt_spec led = GPIO_DT_SPEC_GET(LED0_NODE, gpios);

K_MSGQ_DEFINE(led_timing_queue, sizeof(struct led_timing), 1, 1);

static void blink_handler_thread(void) {
  int err;
  struct led_timing current_timing;

  err = gpio_is_ready_dt(&led);
  if (!err) {
    return;
  }

  k_msgq_get(&led_timing_queue, &current_timing, K_FOREVER);

  while (1) {

    err = gpio_pin_configure_dt(&led, GPIO_OUTPUT_ACTIVE);
    if (err < 0) {
      return;
    }
    k_msgq_get(&led_timing_queue, &current_timing, K_MSEC(current_timing.time_on_ms));

    err = gpio_pin_configure_dt(&led, GPIO_OUTPUT_INACTIVE);
    if (err < 0) {
      return;
    }
    k_msgq_get(&led_timing_queue, &current_timing, K_MSEC(current_timing.time_off_ms));
  }
}

void blink_handler_set_pattern(struct led_timing* timing) {
  while (k_msgq_put(&led_timing_queue, timing, K_NO_WAIT) != 0) {
    k_msgq_purge(&led_timing_queue);
  }
}

K_THREAD_DEFINE(blink_handler_id, 1024, blink_handler_thread, NULL, NULL, NULL,
                7, 0, 0);
#else
void blink_handler_set_pattern(struct led_timing* timing) {
}
#endif
