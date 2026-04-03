<script setup lang="ts">
import { ref, onUpdated, onMounted, useTemplateRef } from 'vue'
import { Icon } from '@iconify/vue';
import FindMyWeb, { AccessoryType, FindMyWebError } from '../lib/FindMyWeb';
import ConfigEntry from "../components/AccessoryConfig/ConfigEntry.vue";
import DeviceOptions from "../components/AccessoryConfig/DeviceOptions.vue";

import ConfigCard from "../components/ConfigCard.vue";
import IconPicker from 'iconify-icon-picker'
import 'iconify-icon-picker/style.css'

const FindMyWebAPI = new FindMyWeb();

const emit = defineEmits(["cancel", "save"]);
const props = defineProps(["accessory", "info", "isNew"]);

const selectedIcon = ref('mdi:radar');
const selectedColor = ref('#ffffff');
const showIconSelector = ref(false);
const accessoryName = ref("");

const entryError = ref("");
const accessoryID = ref(null);
const accessoryInfo = ref(null);
const accessoryType = ref(null);
const isLoading = ref(false);
const isNewAccessory = ref(false);

const deviceOptions = useTemplateRef<typeof DeviceOptions>("deviceOptions");


async function verify() {
  isLoading.value = true;
  let error = false;
  if (accessoryType.value == null) {
    entryError.value = "No type provided";
    error = true;
  } else if (!selectedIcon.value) {
    entryError.value = "No icon provided";
    error = true;
  } else if (!selectedColor.value) {
    entryError.value = "No color provided";
    error = true;
  } else if(accessoryName.value.length <= 0) {
    entryError.value = "Name is empty";
    error = true;
  } else if(accessoryName.value.length > 32) {
    entryError.value = "Name is to long. Max length: 32";
    error = true;
  }

  try {
    if (deviceOptions.value) {
      await deviceOptions.value.verify();
    }
  } catch (ex: Exception) {
    entryError.value = ex.message;
    error = true;
  }

  if(error) {
    isLoading.value = false;
  }
  return error;
}

async function save() {
  entryError.value = "";

  const error = await verify();
  if (error) {
    return;
  }

  try {
    const accessoryOptions = {
      name: accessoryName.value,
      color: selectedColor.value,
      icon: selectedIcon.value,
      options: await deviceOptions.value.getOptions(),
    };
    if (!isNewAccessory.value) {
      await FindMyWebAPI.updateAccessory(accessoryID.value, accessoryOptions);
    } else {
      await FindMyWebAPI.createAccessory(accessoryOptions);
    }
  } catch (error: any) {
    if (error instanceof FindMyWebError) {
      entryError.value = `${error.name}: ${String(error.detail())}`
    } else {
      entryError.value = `${error.name}: ${error.message}`
    }

    isLoading.value = false;
    return;
  }

  emit("save");
  isLoading.value = false;
}

async function deleteAccessory() {
  await FindMyWebAPI.removeAccessory(accessoryID.value);
  emit("save");
}

async function update() {
  if(props.accessory) {
    isNewAccessory.value = false;
    accessoryName.value = props.accessory.name;
    accessoryType.value = props.accessory.type;
    selectedColor.value = props.accessory.color;
    selectedIcon.value = props.accessory.icon;
    accessoryID.value = props.accessory.id;
    accessoryInfo.value = props.info;
  } else {
    selectedIcon.value = "mdi:radar";
    selectedColor.value = "#ffffff";
    accessoryType.value = null;
    accessoryInfo.value = null;
    accessoryName.value = "";
    accessoryID.value = null;
    isNewAccessory.value = true;
  }
}
onUpdated(async () => { await update(); });
onMounted(async () => { await update(); });
</script setup>

<template>
<ConfigCard>
    <div v-if="!showIconSelector">
        <div v-if="!isNewAccessory">
            <Icon @click="deleteAccessory" class="mr-auto text-red-400 bg-gray-700 hover:bg-gray-900 rounded-2xl p-2 size-12 mb-4 cursor-pointer" icon="mdi:trash-can"/>
        </div>
        <div  class="inline-grid grid-cols-[auto_1fr] w-full gap-x-4 gap-y-5">

            <ConfigEntry name="Type" for="type">
                <select class="bg-white rounded-sm p-2 disabled:bg-gray-500" :disabled="!isNewAccessory" v-model="accessoryType" name="type" id="cars">
                    <option disabled>Please select one:</option>
                    <option v-for="type in AccessoryType" :value="type">{{type}}</option>
                </select>
            </ConfigEntry>

            <ConfigEntry name="Name" for="name">
                <input v-model="accessoryName" class="text-white rounded-sm bg-gray-500 px-2 w-full" name="name" type="text">
            </ConfigEntry>

            <ConfigEntry name="Icon">
                <Icon id="selectedIcon" class="size-10 cursor-pointer" @click="showIconSelector=true" :icon="selectedIcon" />
            </ConfigEntry>

            <ConfigEntry name="Color" for="color">
                <input v-model="selectedColor" class="text-white rounded-sm bg-gray-500 ml-auto cursor-pointer" name="color" type="color">
            </ConfigEntry>

            <DeviceOptions ref="deviceOptions" :accessoryInfo="accessoryInfo" :accessoryType="accessoryType" :isNewAccessory="isNewAccessory" />

            <button class="mr-auto mt-6 cursor-pointer" @click="emit('cancel')">
                <p class="text-2xl text-white font-bold bg-gray-500 hover:bg-gray-700 rounded-lg px-2 py-2 shadow-md shadow-gray-900">Cancel</p>
            </button>
            <div class="text-white relative shadow-md shadow-gray-900 ml-auto mt-6">
                <Icon
                    v-if="isLoading"
                    class="absolute size-full top-0 left-0"
                    icon="line-md:loading-loop"
                />
                <button :disabled="isLoading" @click="save" class="cursor-pointer">
                    <p class="text-2xl font-bold bg-blue-600 hover:bg-blue-800 rounded-lg px-2 py-2 ring-2 ring-blue-800" :class="isLoading ? 'opacity-20' : ''">Save</p>
                </button>
            </div>
        </div>
        <div class="text-red-400 font-bold ml-auto mt-3 text-end whitespace-pre-wrap" v-if="entryError.length > 0">{{ entryError }}</div>
    </div>
    <IconPicker id="iconPicker" v-if="showIconSelector" v-model="selectedIcon" @on-select="showIconSelector=false" />
</ConfigCard>
</template>

<style scoped>
#selectedIcon {
    color: v-bind(selectedColor);
}

#iconPicker {
	--iconPicker-text: #ffffff;
	--iconPicker-border: #e0e0e0;
	--iconPicker-primary: #0066cc;
	--iconPicker-primary-fg: #0052a3;
	--iconPicker-primary-hover: #0052a3;
	--iconPicker-radius: 0.375em;
	--iconPicker-gap: 0.25em;
	--iconPicker-input-height: 2.5em;
	--iconPicker-selected-bg: #aaaaaa;
	--iconPicker-font-base: 16px;
	--iconPicker-transition: all 0.2s ease;
}

</style>
