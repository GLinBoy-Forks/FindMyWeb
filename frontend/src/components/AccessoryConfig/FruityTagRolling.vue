<script setup lang="ts">
import ConfigEntry from "./ConfigEntry.vue";
import { AccessoryType } from '../../lib/FindMyWeb.ts';
import { isBase64 } from '../../lib/helpers.ts';

import { onUpdated } from "vue";
import { ref } from "vue";

import { VueDatePicker } from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";


const props = defineProps(["isNew", "info"]);

const masterKey = ref((props.info && props.info.master_key) ? props.info.master_key : "");
const seriesKey = ref((props.info && props.info.series_key) ? props.info.series_key : "");
const secondaryKey = ref((props.info && props.info.secondary_key) ? props.info.secondary_key : "");
const pairedAt = ref((props.info && props.info.paired_at) ? props.info.paired_at : new Date());
const alignmentDate = ref((props.info) ? props.info.alignment_date : null);
const alignmentIndex = ref((props.info) ? props.info.alignment_index : null);


async function getOptions() {
  return {
    type: AccessoryType.FRUITYTAG_ROLLING,
    master_key: masterKey.value,
    series_key: seriesKey.value,
    secondary_key: secondaryKey.value,
    paired_at: pairedAt.value ? new Date(pairedAt.value).toISOString(): null,
    alignment_date: alignmentDate.value ? new Date(alignmentDate.value).toISOString(): null,
    alignment_index: (typeof alignmentIndex.value == "number") ?  alignmentIndex.value: null
  };
}

async function getType() {
  return AccessoryType.FRUITYTAG_ROLLING;
}

async function verify() {
  if (!masterKey.value || !isBase64(masterKey.value)) {
    throw Error("Master key is not a base64 string");
  } else if(!seriesKey.value || !isBase64(seriesKey.value)) {
    throw Error("Series key is not a base64 string");
  } else if(!secondaryKey.value || !isBase64(secondaryKey.value)) {
    throw Error("Secondary key is not a base64 string");
  } else if (!pairedAt.value) {
    throw Error("Paired at is not a valid date");
  } else if ((alignmentDate.value || alignmentIndex.value) && !(alignmentDate.value && alignmentIndex.value)) {
    throw Error("Must supply both an alignment date and an alignment index");
  }
}
defineExpose({ getOptions, getType, verify });

</script setup>
<template>
<ConfigEntry name="Master Key" for="masterKey">
    <input v-model="masterKey" :disabled="!isNew" class="text-white rounded-sm bg-gray-500 px-2 w-full" name="masterKey" type="text">
</ConfigEntry>
<ConfigEntry name="Series Key" for="seriesKey">
    <input v-model="seriesKey" :disabled="!isNew" class="text-white rounded-sm bg-gray-500 px-2 w-full" name="seriesKey" type="text">
</ConfigEntry>
<ConfigEntry name="Secondary Key" for="secondaryKey">
    <input v-model="secondaryKey" :disabled="!isNew" class="text-white rounded-sm bg-gray-500 px-2 w-full" name="secondaryKey" type="text">
</ConfigEntry>
<ConfigEntry name="Paired at" for="pairedAt">
    <VueDatePicker :max-date="new Date()" :disabled="!isNew" v-model="pairedAt"></VueDatePicker>
</ConfigEntry>
<ConfigEntry name="Alignment date" for="alignmentDate">
    <VueDatePicker :max-date="new Date()" v-model="alignmentDate"></VueDatePicker>
</ConfigEntry>
<ConfigEntry name="Alignment index" for="alignmentIndex">
    <input v-model="alignmentIndex" class="text-white rounded-sm bg-gray-500 px-2 w-full" name="alignmentIndex" type="number">
</ConfigEntry>


</template>
