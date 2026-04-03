<script setup lang="ts">
import { ref } from "vue";
import { Icon } from "@iconify/vue";
import { BatteryLevel } from "../lib/FindMyWeb";

const isToggled = ref(false);

async function toggle(state: boolean) {
    isToggled.value = state;
}

const props = defineProps([
    "id",
    "color",
    "name",
    "icon",
    "lastSeen",
    "active",
    "batteryLevel",
]);

function getBatteryIcon(): string {
    const batteryLevel: BatteryLevel = BatteryLevel[props.batteryLevel];

    switch (batteryLevel) {
        case BatteryLevel.Full:
            return "mdi:battery";
        case BatteryLevel.Medium:
            return "mdi:battery-60";
        case BatteryLevel.Low:
            return "mdi:battery-20";
        case BatteryLevel.Critical:
            return "mdi:battery-alert-variant-outline";
    }
    return "mdi:battery-remove-outline";
}

function getBatteryColor(): string {
    switch (props.batteryLevel) {
        case BatteryLevel.Full:
            return "#198000";
        case BatteryLevel.Medium:
            return "#0a580b";
        case BatteryLevel.Low:
            return "#e9777f";
        case BatteryLevel.Critical:
            return "#ff0000";
    }
    return "#ffffff";
}

defineExpose({ toggle });

const emit = defineEmits(["configure"]);
</script>

<template>
    <button
        class="py-1.5 px-2 grid grid-cols-5 w-full gap-2 rounded-3xl shadow-2xl border-2 border-gray-900"
        :class="[
            isToggled
                ? 'bg-gray-900 hover:bg-gray-900/80'
                : 'bg-gray-800/60' + (active ? ' hover:bg-gray-800/80' : ''),
            active ? 'cursor-pointer' : 'cursor-not-allowed disabled',
        ]"
    >
        <Icon
            class="size-14 col-start-1 col-end-1 align-middle"
            :icon="icon"
            :color="color"
            :class="[!active ? 'opacity-55' : '']"
        />
        <p
            class="col-start-2 col-end-2 text-wrap text-white"
            :class="[!active ? 'opacity-55' : '']"
        >
            {{ props.name }}
        </p>
        <p
            class="col-start-3 col-end-3 text-white"
            :class="[!active ? 'opacity-55' : '']"
        >
            {{ props.lastSeen }}
        </p>
        <Icon
            :rotate="3"
            :horizontal-flip="true"
            :class="[!active ? 'opacity-55' : '']"
            class="size-9 col-start-4 col-end-4 self-center ml-auto mr-auto"
            :icon="getBatteryIcon()"
            :color="getBatteryColor()"
        />

        <Icon
            class="size-9 col-start-5 col-end-5 self-center rounded-2xl ml-auto p-1.5 hover:bg-gray-800 block cursor-pointer"
            icon="mdi:cog-outline"
            :color="color"
            @click.stop="emit('configure')"
        />
    </button>
</template>
