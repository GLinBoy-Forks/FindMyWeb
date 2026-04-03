<script setup lang="ts">
import ConfigEntry from "./ConfigEntry.vue";
import { AccessoryType } from '../../lib/FindMyWeb';
import { ref } from "vue";
import { isBase64 } from '../../lib/helpers.ts';

const props = defineProps(["isNew", "info"]);
const masterKey = ref((props.info && props.info.master_key) ? props.info.master_key : "");

async function getOptions() {
  return {
    type: AccessoryType.FRUITYTAG_STATIC,
    master_key: masterKey.value,
  };
}
async function getType() {
  return AccessoryType.FRUITYTAG_STATIC;
}
async function verify() {
  if (!masterKey.value || !isBase64(masterKey.value)) {
    throw Error("Master key is not a base64 string");
  }
}

defineExpose({ getOptions, getType, verify });
</script setup>
<template>
<ConfigEntry name="Master Key" for="masterKey">
    <input v-model="masterKey" :disabled="!isNew" class="text-white rounded-sm bg-gray-500 px-2 w-full" name="masterKey" type="text">
</ConfigEntry>
</template>
