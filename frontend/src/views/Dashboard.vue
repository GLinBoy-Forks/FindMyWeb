<script setup lang="ts">
import FindMyWeb, { Accessory } from "../lib/FindMyWeb.ts";
import Map from "../components/Map.vue";
import SideBar from "../components/SideBar.vue";
import Header from "../components/Header.vue";
import AccessoryConfig from "./AccessoryConfig.vue";

import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const updateDuration = 5;

const FindMyWebAPI = new FindMyWeb();
const sidebar = ref(null);
const map = ref(null);
const showOverlay = ref(false);

const overlayAccessory = ref(null);

let accessories: Accessory[] | null = null;

async function accessoryByName(name: string) {
    if (!accessories) {
        return;
    }

    for (let i = 0; i < accessories.length; i++) {
        if (accessories[i].name != name) {
            continue;
        }
        return accessories[i];
    }
    return null;
}

async function showMarkers() {
    if (!map || !map.value || !accessories) {
        return;
    }

    await map.value.clear();

    for (let i = 0; i < accessories.length; i++) {
        const accessory = accessories[i];
        const locationResp = await FindMyWebAPI.getLocation(accessory.name);

        if (!locationResp.locations || locationResp.locations.length <= 0) {
            continue;
        }

        await map.value.showMarker(accessory, locationResp.locations[0]);
    }
}

async function onSelected(name: string | null) {
    if (!map || !map.value) {
        return;
    }

    if (name != null) {
        let accessory = await accessoryByName(name);

        if (!accessory || !accessory.name) {
            return;
        }

        let locationResp = await FindMyWebAPI.getLocations(accessory.name);

        await map.value.showTrace(accessory, locationResp.locations);
    } else {
        await showMarkers();
    }
}

async function loadTags() {
    try {
        accessories = (await FindMyWebAPI.getAccessories()).accessories;
    } catch (error) {
        alert(error);
        router.push({ name: "Login" });
        return;
    }
}

async function reloadTags() {
    if (!sidebar || !sidebar.value) {
        return;
    }

    await loadTags();
    sidebar.value.updateTags(accessories);
}

async function newAccessory() {
    showOverlay.value = true;
}

async function init() {
    if (!map || !map.value) {
        return;
    }

    await reloadTags();
    await showMarkers();
    setInterval(() => {
        reloadTags();
    }, updateDuration * 1000);
}

async function onSaveCancel() {
    await reloadTags();
    await showMarkers();
    showOverlay.value = false;
    overlayAccessory.value = null;
}

async function onConfigure(name: string) {
    let accessoryResponse;
    try {
        accessoryResponse = await FindMyWebAPI.getAccessory(name);
    } catch (error: any) {
        console.log(`${error.name}: ${error.detail()}`);
        await reloadTags();
        return;
    }
    const accessory = accessoryResponse.accessory;

    if (!accessory) {
        await reloadTags();
        return;
    }

    overlayAccessory.value = accessory;
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
        <AccessoryConfig
            :accessory-to-configure="overlayAccessory"
            @cancel="onSaveCancel"
            @save="onSaveCancel"
        />
    </div>
    <div class="flex flex-col h-dvh">
        <Header
            @open-settings="router.push({ name: 'Settings' })"
            @sidebar-change="(state) => sidebar.updateSidebar(state)"
        />
        <div class="h-full w-full relative">
            <SideBar
                @selected="onSelected"
                @new-accessory="newAccessory"
                @configure="onConfigure"
                ref="sidebar"
            />
            <div class="h-full w-full">
                <Map ref="map" />
            </div>
        </div>
    </div>
</template>
