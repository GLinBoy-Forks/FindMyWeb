<script setup lang="ts">
import FindMyWeb, { Accessory } from "../lib/FindMyWeb.ts";
import Map from "../components/Map.vue";
import SideBar from "../components/SideBar.vue";
import Header from "../components/Header.vue";
import AccessoryConfig from "./AccessoryConfig.vue";

import { onMounted, ref, useTemplateRef } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const updateDuration = 5;

const FindMyWebAPI = new FindMyWeb();
const sidebar = useTemplateRef<typeof SideBar>("sidebar");
const map = useTemplateRef<typeof Map>("map");
const header = useTemplateRef<typeof Header>("header");
const showOverlay = ref(false);

const overlayAccessory = ref<Accessory | null>(null);

const currentAccessory = ref<Accessory | null>(null);

let accessories: Accessory[] | null = null;

async function accessoryByName(name: string): Promise<Accessory | null> {
    if (!accessories) {
        return null;
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
        if (!accessory.name) {
            continue;
        }

        const locationResp = await FindMyWebAPI.getLocation(accessory.name);

        if (!locationResp.location) {
            continue;
        }

        await map.value.showMarker(accessory, locationResp.location);
    }
}

async function onSelected(name: string | null) {
    if (!map || !map.value || !header.value) {
        return;
    }

    if (name != null) {
        currentAccessory.value = await accessoryByName(name);

        if (!currentAccessory.value || !currentAccessory.value.name) {
            currentAccessory.value = null;
            return;
        }
        const startDate = new Date();

        startDate.setHours(0, 0, 0, 0);

        const endDate = new Date();
        await header.value.setDateRange(startDate, endDate);
        let locationResp = await FindMyWebAPI.getLocations(
            currentAccessory.value.name,
            startDate,
            endDate,
        );

        await map.value.showTrace(
            currentAccessory.value,
            locationResp.locations,
        );
    } else {
        currentAccessory.value = null;
        await header.value.hideDatePicker();
        await showMarkers();
    }
}

async function onDateRangeChange(startDate: Date, endDate: Date) {
    if (
        !map ||
        !map.value ||
        !currentAccessory.value ||
        !currentAccessory.value.name
    ) {
        return;
    }
    let locationResp = await FindMyWebAPI.getLocations(
        currentAccessory.value.name,
        startDate,
        endDate,
    );
    await map.value.showTrace(currentAccessory.value, locationResp.locations);
}

async function loadTags() {
    try {
        const accessoriesResp = await FindMyWebAPI.getAccessories();
        // @ts-ignore: API should never return empty response
        accessories = accessoriesResp.accessories;
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
            ref="header"
            @date-range-changed="onDateRangeChange"
            @open-settings="router.push({ name: 'Settings' })"
            @sidebar-change="(state) => sidebar?.updateSidebar(state)"
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
