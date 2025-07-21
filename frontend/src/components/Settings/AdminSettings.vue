<script setup lang="ts">
import { onMounted, ref } from "vue";
import { Icon } from "@iconify/vue";
import UserEntry from "./UserEntry.vue";
import FindMyWeb, { UserInfo } from "../../lib/FindMyWeb";
import UserConfig from "../../views/UserConfig.vue";

const FindMyWebAPI = new FindMyWeb();

const users = ref<Array<UserInfo>>([]);
const showOverlay = ref<boolean>(false);
// @ts-ignore: can also be null
const overlayUser = ref<InstanceType<UserInfo>>(null);

async function loadUsers() {
    const fetchedUsers = (await FindMyWebAPI.getUsers()).users;
    users.value = [];
    if (!fetchedUsers) {
        return;
    }

    for (let i = 0; i < fetchedUsers.length; i++) {
        // @ts-ignore: Refs can't be typed easily
        users.value.push(fetchedUsers[i]);
    }
}

async function init() {
    await loadUsers();
}

async function onSaveCancel() {
    await loadUsers();
    showOverlay.value = false;
}

async function configureUser(index: number | null) {
    if (!index) {
        // @ts-ignore: can also be null
        overlayUser.value = null;
        showOverlay.value = true;
        return;
    }
    overlayUser.value = users.value[index];
    showOverlay.value = true;
}

onMounted(async () => {
    await init();
});
</script>

<template>
    <div
        v-if="showOverlay"
        id="overlay"
        class="fixed w-dvw h-dvh top-0 left-0 right-0 bottom-0 bg-black/80 z-20"
    >
        <UserConfig
            :username="overlayUser ? overlayUser.name : null"
            :is-admin="overlayUser ? overlayUser.is_admin : null"
            @cancel="onSaveCancel"
            @save="onSaveCancel"
        />
    </div>
    <div class="bg-gray-800 w-full">
        <div class="border-b-2 border-white py-3 ml-5 mr-5 flex-col">
            <h1 class="text-white font-bold text-2xl mb-3">Users</h1>
            <div class="w-full flex flex-col gap-y-3">
                <UserEntry
                    @configure="configureUser(index)"
                    v-for="(user, index) in users"
                    :name="user.name"
                    :key="index"
                />
                <button
                    @click="configureUser(null)"
                    class="my-5 py-1.5 px-1.5 w-full bg-gray-700 hover:bg-gray-800 rounded-3xl shadow-2xl border-2 border-gray-950"
                >
                    <Icon
                        class="size-10 mx-auto my-auto"
                        icon="mdi:add"
                        color="#ffffff"
                    />
                </button>
            </div>
        </div>
    </div>
</template>
