<script setup lang="ts">
import { ref, onMounted, onUpdated, useTemplateRef } from "vue";
import { useRouter } from "vue-router";
import { Icon } from "@iconify/vue";

import SettingsEntry from "../components/Settings/SettingsEntry.vue";
import FindMyWeb from "../lib/FindMyWeb";

const FindMyWebAPI = new FindMyWeb();

const router = useRouter();
const settingsEntries = useTemplateRef("settingsEntries");

let previousEntry: typeof SettingsEntry | null = null;

let settingsOptions = ref({
    "settings-profile": {
        icon: "mdi:user",
        name: "Profile",
    },
});

async function onToggle(route_name: string, index: number) {
    router.push({ name: route_name });
}

async function init() {
    console.log(await FindMyWebAPI.isAdmin());
    if (await FindMyWebAPI.isAdmin()) {
        // @ts-ignore: Needed to add `settings-admin` dynamically
        settingsOptions.value["settings-admin"] = {
            icon: "mdi:administrator",
            name: "Admin",
        };
    }
    await update();
}

async function update() {
    if (previousEntry) {
        previousEntry.toggle(false);
    }

    const route = router.currentRoute.value.name;
    for (let i = 0; i < settingsEntries.value.length; i++) {
        if (route === settingsEntries.value[i].route) {
            previousEntry = settingsEntries.value[i];
            break;
        }
    }
    if (!previousEntry) {
        router.push({ name: "settings-profile" });
    }
    previousEntry.toggle(true);
}

onMounted(async () => {
    await init();
});

onUpdated(async () => {
    await update();
});
</script>

<template>
    <div class="flex flex-col h-dvh">
        <div class="h-12 bg-amber-600 flex content-start w-full">
            <button class="size-10" @click="router.push({ name: 'Dashboard' })">
                <Icon
                    class="size-full text-gray-800 align-middle"
                    icon="mdi:arrow-back"
                />
            </button>
        </div>
        <div class="h-full flex flex-row">
            <div
                class="h-full w-50 z-10 bg-gray-700/90 bg-opacity-40 overflow-y-scroll"
            >
                <div class="flex flex-col gap-y-3 ml-2 mr-2 mt-2 text-white">
                    <SettingsEntry
                        ref="settingsEntries"
                        v-for="(config, route, index) in settingsOptions"
                        @toggle="onToggle(route, index)"
                        :route_name="route"
                        :icon="config.icon"
                        :name="config.name"
                        :key="index"
                    />
                </div>
            </div>
            <router-view name="settings" />
        </div>
    </div>
</template>
