<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue';
import FindMyWeb from '../lib/FindMyWeb';
import 'iconify-icon-picker/style.css'

const FindMyWebAPI = new FindMyWeb();

const emit = defineEmits(["cancel", "save"]);

const username = ref("");
const password = ref("");
const isAdmin = ref(false);
const isSelf = ref(false);

const entryError = ref("");

const props = defineProps(["username", "isAdmin"]);

async function save() {
  let error = false;

  entryError.value = "";

  if(username.value.length <= 0) {
    entryError.value = "Username is empty";
    error = true;
  } else if(username.value.length > 32) {
    entryError.value = "Username is to long. Max length: 32";
    error = true;
  } else if(password.value.length <= 0 && !props.username) {
    entryError.value = "Password is empty";
    error = true;
  }

  if(error) {
    return;
  }
  try {
    if (props.username) {
      await FindMyWebAPI.updateUser(username.value, password.value, isAdmin.value);
    } else {
      await FindMyWebAPI.createUser(username.value, password.value, isAdmin.value);
    }
  } catch(error: any) {
    entryError.value = `${error.name}: ${error.detail()}`
    return;
  }
  emit("save");
}

async function deleteUser() {
  try {
    await FindMyWebAPI.deleteUser(username.value);
  } catch(error: any) {
    entryError.value = `${error.name}: ${error.detail()}`
    return;
  }
  emit("save");
}

async function init() {
  if(props.username) {
    username.value = props.username;
    isAdmin.value = props.isAdmin;
    if(props.username == await FindMyWebAPI.getUsername()) {
      isSelf.value = true;

    }
    return;
  }
}

onMounted(async () => {
    await init();
});

</script setup>

<template>
    <div class="h-full flex flex-row items-center justify-center">
        <div class="md:p-8 p-10 ml-4 mr-4 rounded-lg shadow-black shadow-2xl w-full md:w-[80%] lg:w-[60%] xl:w-[50%] 2xl:w-[40%] bg-gray-800 flex flex-col ring-4 ring-gray-900">
                <div v-if="props.username && !isSelf">
                    <Icon @click="deleteUser" class="mr-auto text-red-400 bg-gray-700 hover:bg-gray-900 rounded-2xl p-2 size-12 mb-4" icon="mdi:trash-can"/>
                </div>
                <div  class="grid grid-cols-[max-content_1fr] gap-x-4 gap-y-5">
                    <label class="text-white text-lg md:text-xl font-bold" for="name">Name:</label>
                    <input v-model="username" :disabled="props.username" class="text-white rounded-sm bg-gray-500 px-2 w-full" name="name" type="text">

                    <label v-if="!isSelf" class="text-white text-lg md:text-xl font-bold" for="password">Password:</label>
                    <input v-if="!isSelf" v-model="password" class="text-white rounded-sm bg-gray-500 px-2 w-full" name="password" type="password">

                    <label class="text-white text-lg md:text-xl font-bold" for="is_admin">Admin:</label>
                    <input v-model="isAdmin" :disabled="isSelf" class="text-white rounded-sm bg-gray-500 px-2 ml-auto size-6 cursor-pointer" name="is_admin" type="checkbox">

                    <button class="mr-auto mt-6 cursor-pointer" @click="emit('cancel')">
                        <p class="text-2xl text-white font-bold bg-gray-500 hover:bg-gray-700 rounded-lg px-2 py-2 shadow-md shadow-gray-900">Cancel</p>
                    </button>

                    <button class="ml-auto mt-6 cursor-pointer" @click="save">
                        <p class="text-2xl text-white font-bold bg-blue-600 hover:bg-blue-800 rounded-lg px-2 py-2 shadow-md shadow-gray-900 ring-2 ring-blue-800">Save</p>
                    </button>

                </div>
                <p class="text-red-400 font-bold ml-auto mt-3 text-end" v-if="entryError.length > 0">{{ entryError }}</p>

            </div>
        </div>

</template>
