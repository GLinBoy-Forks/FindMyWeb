<script setup lang="ts">
import { ref } from "vue";
import { Icon } from "@iconify/vue";
import VueDatePicker from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";

const sidebarOpened = ref(true);
const buttonIcon = ref("mdi:menu-open");

const dateRange = ref<Date[]>([]);

const emit = defineEmits(["sidebarChange", "openSettings", "dateRangeChanged"]);

async function onSidebarButton() {
    sidebarOpened.value = !sidebarOpened.value;
    if (sidebarOpened.value) {
        buttonIcon.value = "mdi:menu-open";
    } else {
        buttonIcon.value = "mdi:menu";
    }
    emit("sidebarChange", sidebarOpened.value);
}

async function setDateRange(startDate: Date, endDate: Date) {
    dateRange.value = [startDate, endDate];
}

async function hideDatePicker() {
    dateRange.value = [];
}

async function onDateRangeUpdate(modelData: Date[]) {
    emit("dateRangeChanged", modelData[0], modelData[1]);
    dateRange.value = modelData;
}

defineExpose({ setDateRange, hideDatePicker });
</script>

<template>
    <div class="h-12 bg-amber-600 flex content-start w-full">
        <button
            class="size-10 justify-start flex-none"
            @click="onSidebarButton()"
        >
            <Icon
                class="size-full text-gray-800 align-middle"
                :icon="buttonIcon"
            />
        </button>
        <div class="justify-center mt-auto mb-auto ml-auto mr-auto">
            <VueDatePicker
                @update:model-value="onDateRangeUpdate"
                v-if="dateRange.length > 0"
                v-model="dateRange"
                range
                time-picker-inline
                dark
            />
        </div>
        <button
            class="size-10 justify-end flex-none"
            @click="emit('openSettings')"
        >
            <Icon
                class="size-full text-gray-800 align-middle"
                icon="mdi:cog-outline"
            />
        </button>
    </div>
</template>
