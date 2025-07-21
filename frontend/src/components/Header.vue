<script setup lang="ts">
import { ref } from "vue";
import { Icon } from "@iconify/vue";

const sidebarOpened = ref(true);
const buttonIcon = ref("mdi:menu-open");

const emit = defineEmits(["sidebarChange", "openSettings"]);

async function onSidebarButton() {
    sidebarOpened.value = !sidebarOpened.value;
    if (sidebarOpened.value) {
        buttonIcon.value = "mdi:menu-open";
    } else {
        buttonIcon.value = "mdi:menu";
    }
    emit("sidebarChange", sidebarOpened.value);
}
</script>

<template>
    <div class="h-12 bg-amber-600 flex content-start w-full">
        <button class="size-10" @click="onSidebarButton()">
            <Icon
                class="size-full text-gray-800 align-middle"
                :icon="buttonIcon"
            />
        </button>
        <button class="size-10 ml-auto" @click="emit('openSettings')">
            <Icon
                class="size-full text-gray-800 align-middle"
                icon="mdi:cog-outline"
            />
        </button>
    </div>
</template>
