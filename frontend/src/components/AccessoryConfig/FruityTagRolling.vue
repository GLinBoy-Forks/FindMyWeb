<script setup lang="ts">
import ConfigEntry from "./ConfigEntry.vue";
import { AccessoryType } from '../../lib/FindMyWeb.ts';
import { isBytes28Base64, isBytes32Base64, isBytes28Hex, isBytes32Hex, hexToBase64, plistToJson, readXMLFile } from '../../lib/helpers.ts';

import { onUpdated } from "vue";
import { ref, inject } from "vue";

import { VueDatePicker } from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";


const props = defineProps(["isNew", "info"]);

const masterKey = ref((props.info && props.info.master_key) ? props.info.master_key : "");
const seriesKey = ref((props.info && props.info.series_key) ? props.info.series_key : "");
const secondaryKey = ref((props.info && props.info.secondary_key) ? props.info.secondary_key : "");
const pairedAt = ref((props.info && props.info.paired_at) ? new Date(props.info.paired_at+"Z") : new Date());
const alignmentDate = ref((props.info && props.info.alignment_date) ? new Date(props.info.alignment_date+"Z") : null);
const alignmentIndex = ref((props.info) ? props.info.alignment_index : null);

const errorInject = inject("entryError");

async function getOptions() {
  return {
    type: AccessoryType.FRUITYTAG_ROLLING,
    master_key: masterKey.value.endsWith("=") ? masterKey.value : hexToBase64(masterKey.value),
    series_key: seriesKey.value.endsWith("=") ? seriesKey.value : hexToBase64(seriesKey.value),
    secondary_key: secondaryKey.value.endsWith("=") ? secondaryKey.value : hexToBase64(secondaryKey.value),
    paired_at: pairedAt.value ? new Date(pairedAt.value).toISOString(): null,
    alignment_date: alignmentDate.value ? new Date(alignmentDate.value).toISOString(): null,
    alignment_index: (typeof alignmentIndex.value == "number") ?  alignmentIndex.value: null
  };
}

async function getType() {
  return AccessoryType.FRUITYTAG_ROLLING;
}

async function verify() {
  if (!masterKey.value || !(isBytes28Base64(masterKey.value) || isBytes28Hex(masterKey.value))) {
    throw Error("Master key has to be 28 bytes in hex or base64");
  } else if(!seriesKey.value || !(isBytes32Base64(seriesKey.value) || isBytes32Hex(seriesKey.value))) {
    throw Error("Series key has to be 32 bytes in hex or base64");
  } else if(!secondaryKey.value || !(isBytes32Base64(secondaryKey.value) || isBytes32Hex(secondaryKey.value))) {
    throw Error("Secondary key has to be 32 bytes in hex or base64");
  } else if (!pairedAt.value) {
    throw Error("Paired at is not a valid date");
  } else if ((alignmentDate.value || alignmentIndex.value) && !(alignmentDate.value && alignmentIndex.value)) {
    throw Error("Must supply both an alignment date and an alignment index");
  }
}

async function loadFromPlist(evt: ChangeEvent) {
  try {
    const target = evt.target;
    const xml = await readXMLFile(target.files[0]);
    const json = plistToJson(xml.documentElement);

    const privKey = json.get("privateKey")?.get("key")?.get("data");
    const skn = json.get("sharedSecret")?.get("key")?.get("data");

    const sks = json.has("secondarySharedSecret") ?
      json.get("secondarySharedSecret")?.get("key")?.get("data") :
      json.get("secureLocationsSharedSecret")?.get("key")?.get("data");

    const paringDate = json.get("pairingDate");

    if (!privKey || atob(privKey).length < 28) {
      throw new Error("Invalid privateKey");
    }

    if (!skn || atob(skn).length != 32) {
      throw new Error("Invalid sharedSecret");
    }

    if (!skn || atob(sks).length != 32) {
      throw new Error("Invalid secondarySharedSecret / secureLocationsSharedSecret");
    }

    if (!paringDate || !(paringDate instanceof Date)) {
      throw new Error("Invalid paringDate");
    }

    masterKey.value = btoa(atob(privKey).slice(-28));
    seriesKey.value = skn;
    secondaryKey.value = sks;
    pairedAt.value = paringDate;
    errorInject.value = "";

  } catch (e) {
    errorInject.value = `Error while loading plist: ${e}`
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
    <VueDatePicker :max-date="new Date()" :time-config="{ enableSeconds: true }" :disabled="!isNew" v-model="pairedAt"></VueDatePicker>
</ConfigEntry>
<ConfigEntry name="Alignment date" for="alignmentDate">
    <VueDatePicker :max-date="new Date()" :time-config="{ enableSeconds: true }" v-model="alignmentDate"></VueDatePicker>
</ConfigEntry>
<ConfigEntry name="Alignment index" for="alignmentIndex">
    <input v-model="alignmentIndex" class="text-white rounded-sm bg-gray-500 px-2 w-full" name="alignmentIndex" type="number">
</ConfigEntry>
<div v-if="isNew" class="flex col-span-2">
  <label for="plist-file" class="text-white ml-auto rounded-sm bg-blue-600 hover:bg-blue-800 ring-2 ring-blue-800 shadow-md shadow-gray-900 p-2">Load from .plist</label>
  <input id="plist-file" @change="loadFromPlist" class="hidden" type="file"></input>
</div>
</template>
