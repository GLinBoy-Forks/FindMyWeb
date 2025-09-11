#include "battery_thread.h"
#include "fruitytag/fruitytag.h"
#include <zephyr/devicetree.h>

#if DT_HAS_ALIAS(fuel_gauge0)
#include <zephyr/bluetooth/services/bas.h>
#include <zephyr/drivers/fuel_gauge.h>
#include <zephyr/kernel.h>
#ifdef CONFIG_PM_DEVICE
#include <zephyr/pm/device_runtime.h>
#endif

void battery_thread(void* tag_data, void*, void*) {
  int err;
  fruity_tag* tag = (fruity_tag*)tag_data;

  const struct device* const fuel_gauge = DEVICE_DT_GET(DT_ALIAS(fuel_gauge0));

  if (fuel_gauge == NULL) {
    bt_bas_bls_set_battery_present(BT_BAS_BLS_BATTERY_NOT_PRESENT);
    return;
  }

  if (!device_is_ready(fuel_gauge)) {
    bt_bas_bls_set_battery_present(BT_BAS_BLS_BATTERY_NOT_PRESENT);
    return;
  }

  union fuel_gauge_prop_val batt_val;

  while (1) {
#ifdef CONFIG_PM_DEVICE
    pm_device_runtime_get(fuel_gauge);
#endif

    err = fuel_gauge_get_prop(fuel_gauge, FUEL_GAUGE_RELATIVE_STATE_OF_CHARGE, &batt_val);
    if (err) {
      bt_bas_bls_set_battery_present(BT_BAS_BLS_BATTERY_NOT_PRESENT);
      return;
    };
    bt_bas_set_battery_level(batt_val.relative_state_of_charge);
    fruitytag_update_battery(tag, batt_val.relative_state_of_charge);
#ifdef CONFIG_PM_DEVICE
    pm_device_runtime_put(fuel_gauge);
#endif
    k_msleep(20000);
  }
}
#else
void battery_thread(void* tag_data, void*, void*) { return; }
#endif
