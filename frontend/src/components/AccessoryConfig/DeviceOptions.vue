<script setup lang="ts">

import { ref, type VNodeRef } from "vue";
import { AccessoryType } from '../../lib/FindMyWeb';
import FruityTagStatic from './FruityTagStatic.vue';
import FruityTagRolling from './FruityTagRolling.vue';


const configOption = ref<typeof FruityTagStatic | typeof FruityTagRolling | null>(null);
const props = defineProps(["accessoryType", "accessoryInfo", "isNewAccessory"]);
async function getOptions() {
  if (!configOption.value) {
    return null;
  }
  return await configOption.value.getOptions();
}

async function verify() {
  if (!configOption.value) {
    return;
  }
  await configOption.value.verify();
}
async function setRef(element: VNodeRef | undefined) {
  if (!element) {
    return;
  }
  // @ts-ignore: we always pass a known element
  if (await element.getType() != props.accessoryType) {
    configOption.value = null;
  } else {
    // @ts-ignore: we always pass a known element
    configOption.value = element;
  }
}
defineExpose({verify, getOptions});
</script setup>

<template>
    <FruityTagStatic :ref="setRef" :isNew="isNewAccessory" :info="accessoryInfo" v-if="accessoryType == AccessoryType.FRUITYTAG_STATIC"/>
    <FruityTagRolling :ref="setRef" :isNew="isNewAccessory" :info="accessoryInfo" v-else-if="accessoryType == AccessoryType.FRUITYTAG_ROLLING"/>
</template>
