<script setup lang="ts">
import {
    onMounted,
    onBeforeUnmount,
    onDeactivated,
    onActivated,
    ref,
    useTemplateRef,
    defineAsyncComponent,
} from "vue";
import Error from "../components/Error.vue";
import Loading from "../components/Loading.vue";
import FindMyWeb, { type Accessory, FindMyWebError } from "../lib/FindMyWeb.ts";
import { locationDate } from "../lib/helpers.ts";

const Map = defineAsyncComponent({
    loader: () => import("../components/Map.vue"),
    loadingComponent: Loading,
    delay: 200,
    errorComponent: Error,
    timeout: 8000,
});

const SideBar = defineAsyncComponent({
    loader: () => import("../components/SideBar.vue"),
    loadingComponent: Loading,
    delay: 200,
    errorComponent: Error,
    timeout: 3000,
});

const AccessoryConfig = defineAsyncComponent({
    loader: () => import("./AccessoryConfig.vue"),
    loadingComponent: Loading,
    delay: 200,
    errorComponent: Error,
    timeout: 3000,
});

const Overlay = defineAsyncComponent({
    loader: () => import("../components/Overlay.vue"),
    loadingComponent: Loading,
    delay: 200,
    errorComponent: Error,
    timeout: 3000,
});

import Header from "../components/Header.vue";

import { useRouter } from "vue-router";

const router = useRouter();

const updateDuration = 5;

const FindMyWebAPI = new FindMyWeb();
const sidebar = useTemplateRef<typeof SideBar>("sidebar");
const map = useTemplateRef<typeof Map>("map");
const header = useTemplateRef<typeof Header>("header");
const overlay = useTemplateRef<typeof Overlay>("overlay");
const configureAccessory =
    useTemplateRef<typeof AccessoryConfig>("configureAccessory");
const accessoryToConfigure = ref(null);
const accessoryInfoToConfigure = ref(null);
const currentAccessory = ref<Accessory | null>(null);

let accessories: Accessory[] | null = null;

let refreshId: number | null = null;

async function accessoryByID(id: string): Promise<Accessory | null> {
    if (!accessories) {
        return null;
    }

    for (let i = 0; i < accessories.length; i++) {
        if (accessories[i].id != id) {
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

    const coordinates = [];

    for (let i = 0; i < accessories.length; i++) {
        const accessory = accessories[i];
        let locationResp = null;
        try {
            locationResp = await FindMyWebAPI.getLastLocation(accessory.id);
        } catch {
            continue;
        }
        const locationInfo = await FindMyWebAPI.getLocationInfo(
            accessory.id,
            locationResp.id,
        );
        coordinates.push([locationResp.lon, locationResp.lat]);

        await map.value.showMarker(
            accessory,
            locationInfo.location,
            locationInfo.info,
        );
    }
    await map.value.zoomToCoordinates(coordinates, 200);
}

async function onSelected(id: string | null) {
    if (!map || !map.value || !header.value) {
        return;
    }

    if (id != null) {
        currentAccessory.value = await accessoryByID(id);

        if (!currentAccessory.value || !currentAccessory.value.id) {
            currentAccessory.value = null;
            return;
        }

        const lastLocation = await FindMyWebAPI.getLastLocation(
            currentAccessory.value.id,
        );

        const endDate = await locationDate(lastLocation);
        if (!endDate) {
            return;
        }

        const startDate = new Date(endDate);

        startDate.setDate(endDate.getDate() - 1);

        await header.value.setDateRange(startDate, endDate);
        let locationResp = await FindMyWebAPI.getLocations(
            currentAccessory.value.id,
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
        currentAccessory.value.id,
        startDate,
        endDate,
    );
    await map.value.showTrace(currentAccessory.value, locationResp.locations);
}

async function onDownloadGPX(startDate: Date, endDate: Date) {
    if (
        !map ||
        !map.value ||
        !currentAccessory.value ||
        !currentAccessory.value.name
    ) {
        return;
    }
    const gpxData = await FindMyWebAPI.exportGPX(
        currentAccessory.value.id,
        startDate,
        endDate,
    );
    const url = window.URL.createObjectURL(gpxData.blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", gpxData.filename);
    document.body.appendChild(link);
    link.click();
}

async function loadTags() {
    try {
        const accessoriesResp = await FindMyWebAPI.getAccessories();
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

async function reloadAndShow() {
    await reloadTags();
    await showMarkers();
}

async function newAccessory() {
    await overlay.value.showOverlay("newAccessory");
}

async function startInterval() {
    await stopInterval();

    refreshId = setInterval(() => {
        reloadTags();
    }, updateDuration * 1000);
}

async function stopInterval() {
    if (refreshId) {
        clearInterval(refreshId);
        refreshId = null;
    }
}

async function init() {
    while (!map || !map.value) {
        await new Promise((res) => setTimeout(res, 100));
    }

    await reloadAndShow();
    await startInterval();
}

async function onSaveCancel() {
    await overlay.value.hideOverlay();
    reloadAndShow();
}

async function onConfigure(id: string) {
    let accessory;
    try {
        accessory = await FindMyWebAPI.getAccessory(id);
    } catch (error: Error) {
        console.error(`onConfigure: ${error.name}: ${error.detail()}`);
        await reloadTags();
        return;
    }

    if (!accessory) {
        await reloadTags();
        return;
    }
    accessoryToConfigure.value = accessory.accessory;
    accessoryInfoToConfigure.value = accessory.info;
    await overlay.value.showOverlay("configureAccessory");
}

async function onNewAccessory() {
    accessoryToConfigure.value = null;
    accessoryInfoToConfigure.value = null;
    await overlay.value.showOverlay("configureAccessory");
}

onBeforeUnmount(async () => {
    await stopInterval();
});

onDeactivated(async () => {
    await stopInterval();
});

onActivated(async () => {
    await startInterval();
});

onMounted(async () => {
    await init();
});
</script>

<template>
    <Transition
        enter-from-class="opacity-0"
        leave-to-class="opacity-0"
        enter-active-class="transition duration-300"
        leave-active-class="transition duration-300"
        mode="out-in"
    >
        <Overlay ref="overlay">
            <template v-slot:configureAccessory>
                <AccessoryConfig
                    ref="configureAccessory"
                    :accessory="accessoryToConfigure"
                    :info="accessoryInfoToConfigure"
                    @cancel="onSaveCancel"
                    @save="onSaveCancel"
                />
            </template>
        </Overlay>
    </Transition>
    <div class="flex flex-col h-dvh">
        <Header
            ref="header"
            @date-range-changed="onDateRangeChange"
            @open-settings="router.push({ name: 'Settings' })"
            @sidebar-change="(state) => sidebar?.updateSidebar(state)"
            @downloadGPX="onDownloadGPX"
        />
        <div class="h-full w-full relative">
            <SideBar
                @selected="onSelected"
                @configure="onConfigure"
                @new-accessory="onNewAccessory"
                ref="sidebar"
            />
            <div class="h-full w-full">
                <Map ref="map" />
            </div>
        </div>
    </div>
</template>
