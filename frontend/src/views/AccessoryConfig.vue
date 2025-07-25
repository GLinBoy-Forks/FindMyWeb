<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue';
import FindMyWeb from '../lib/FindMyWeb';
import IconPicker from 'iconify-icon-picker'
import 'iconify-icon-picker/style.css'

const FindMyWebAPI = new FindMyWeb();

const emit = defineEmits(["cancel", "save"]);

const selectedIcon = ref('mdi:radar');
const selectedColor = ref('#ffffff');
const showIconSelector = ref(false);

const accessoryName = ref("");
const privateKey = ref("");

const entryError = ref("");

const advertisementKey = ref("");

const base64regex = /^([0-9a-zA-Z+/]{4})*(([0-9a-zA-Z+/]{2}==)|([0-9a-zA-Z+/]{3}=))?$/;

const props = defineProps(["accessoryToConfigure"]);

async function save() {
  let error = false;

  entryError.value = "";

  if(accessoryName.value.length <= 0) {
    entryError.value = "Name is empty";
    error = true;
  } else if(accessoryName.value.length > 32) {
    entryError.value = "Name is to long. Max length: 32";
    error = true;
  } else if(privateKey.value.length != 40) {
    entryError.value = "Not a valid private key";
    error = true;
  } else if (!base64regex.test(privateKey.value)) {
    entryError.value = "Private key must be base64 encoded";
    error = true;
  }

  if(error) {
    return;
  }

  try {
    const accessoryOptions = {
      name: accessoryName.value,
      color: selectedColor.value,
      icon: selectedIcon.value,
      private_key: privateKey.value,
    };
    if (props.accessoryToConfigure) {
      await FindMyWebAPI.updateAccessory(accessoryOptions);
    } else {
      await FindMyWebAPI.createAccessory(accessoryOptions);
    }
  } catch(error: any) {
    entryError.value = `${error.name}: ${error.detail()}`
    return;
  }
  emit("save");
}

async function deleteAccessory() {
  await FindMyWebAPI.removeAccessory(props.accessoryToConfigure.name);
  emit("save");
}

async function init() {
  if(props.accessoryToConfigure) {
    const accessory = props.accessoryToConfigure;
    privateKey.value = accessory.private_key;
    accessoryName.value = accessory.name;
    selectedColor.value = accessory.color;
    selectedIcon.value = accessory.icon;

    const advertisementResponse = await FindMyWebAPI.getAdvertisementKey(accessory.name);
    const newAdvertisementKey = advertisementResponse.advertisement_key;

    if(newAdvertisementKey) {
      advertisementKey.value = newAdvertisementKey;
    }

    return;
  }

  const privateKeyResponse = await FindMyWebAPI.getPrivateKey();
  const newPrivateKey = privateKeyResponse.private_key;

  if(!newPrivateKey) {
    return;
  }

  privateKey.value = newPrivateKey;

}



onMounted(async () => {
    await init();
});

</script setup>

<template>
    <div class="h-full flex flex-row items-center justify-center">
        <div class="md:p-8 p-10 ml-4 mr-4 rounded-lg shadow-black shadow-2xl w-full md:w-[80%] lg:w-[60%] xl:w-[50%] 2xl:w-[40%] bg-gray-800 flex flex-col ring-4 ring-gray-900">
            <div v-if="!showIconSelector">
                <div v-if="props.accessoryToConfigure">
                    <Icon @click="deleteAccessory" class="mr-auto text-red-400 bg-gray-700 hover:bg-gray-900 rounded-2xl p-2 size-12 mb-4" icon="mdi:trash-can"/>
                </div>
                <div  class="grid grid-cols-[max-content_1fr] gap-x-4 gap-y-5">

                    <label class="text-white text-lg md:text-xl font-bold" for="icon">Icon:</label>
                    <Icon id="selectedIcon" class="text-white ml-auto size-10" @click="showIconSelector=true" :icon="selectedIcon" />

                    <label class="text-white text-lg md:text-xl font-bold" for="color">Color:</label>
                    <input v-model="selectedColor" class="text-white rounded-sm bg-gray-500 ml-auto" name="color" type="color">

                    <label class="text-white text-lg md:text-xl font-bold" for="name">Name:</label>
                    <input v-model="accessoryName" class="text-white rounded-sm bg-gray-500 px-2 w-full" name="name" type="text">

                    <label class="text-white text-lg md:text-xl font-bold" for="private_key">Private Key:</label>
                    <input v-model="privateKey" :disabled="props.accessoryToConfigure" class="text-white rounded-sm bg-gray-500 px-2 w-full" name="private_key" type="text">

                    <label v-if="advertisementKey.length > 0" class="text-white text-lg md:text-xl font-bold" for="advertisement_key">Advertisement Key:</label>
                    <input v-if="advertisementKey.length > 0" v-model="advertisementKey" :disabled="props.accessoryToConfigure" class="text-white rounded-sm bg-gray-500 px-2 w-full" name="advertisement_key" type="text">

                    <button class="mr-auto mt-6" @click="emit('cancel')">
                        <p class="text-2xl text-white font-bold bg-gray-500 hover:bg-gray-700 rounded-lg px-2 py-2 shadow-md shadow-gray-900">Cancel</p>
                    </button>

                    <button class="ml-auto mt-6" @click="save">
                        <p class="text-2xl text-white font-bold bg-blue-600 hover:bg-blue-800 rounded-lg px-2 py-2 shadow-md shadow-gray-900 ring-2 ring-blue-800">Save</p>
                    </button>

                </div>
                <p class="text-red-400 font-bold ml-auto mt-3 text-end" v-if="entryError.length > 0">{{ entryError }}</p>

            </div>

            <IconPicker id="iconPicker" v-if="showIconSelector" v-model="selectedIcon" @on-select="showIconSelector=false" />


        </div>

    </div>
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
