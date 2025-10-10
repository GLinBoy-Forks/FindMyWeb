<script setup lang="ts">
import { ref } from "vue";
import FindMyWeb from "../../lib/FindMyWeb";
const FindMyWebAPI = new FindMyWeb();

const oldPassword = ref("");
const newPassword = ref("");

const entryError = ref("");

async function changePassword() {
    try {
        await FindMyWebAPI.updatePassword(oldPassword.value, newPassword.value);
        entryError.value = "";
        oldPassword.value = "";
        newPassword.value = "";
    } catch (error: any) {
        entryError.value = `${error.name}: ${error.detail()}`;
    }
}
</script>
<template>
    <div class="bg-gray-800 w-full">
        <div class="border-b-2 border-white py-3 ml-5 mr-5 flex-col">
            <h1 class="text-white font-bold text-2xl">Password</h1>
            <div class="w-full">
                <label
                    for="old_password"
                    class="block text-m font-medium text-white mt-3"
                >
                    Old Password
                </label>

                <input
                    type="password"
                    id="old_password"
                    v-model="oldPassword"
                    class="mt-1 w-full rounded-md border-gray-200 bg-slate-500 text-m text-gray-100 shadow-sm p-2"
                />

                <label
                    for="new_password"
                    class="block text-m font-medium text-white mt-3"
                >
                    New Password
                </label>

                <input
                    type="password"
                    id="new_password"
                    v-model="newPassword"
                    class="mt-1 w-full rounded-md border-gray-200 bg-slate-500 text-m text-gray-100 shadow-sm p-2"
                />
                <div class="flex justify-end">
                    <button class="mt-6 cursor-pointer" @click="changePassword">
                        <p
                            class="text-2xl text-white font-bold bg-blue-600 hover:bg-blue-800 rounded-lg px-2 py-2 shadow-md shadow-gray-900 ring-2 ring-blue-800"
                        >
                            Save
                        </p>
                    </button>
                </div>
                <p
                    class="text-red-400 font-bold ml-auto mt-3 text-end"
                    v-if="entryError.length > 0"
                >
                    {{ entryError }}
                </p>
            </div>
        </div>
    </div>
</template>
