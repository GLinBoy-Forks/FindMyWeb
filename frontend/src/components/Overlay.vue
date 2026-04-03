<script setup lang="ts">
import { ref } from "vue";

const currentSlot = ref(null);

async function showOverlay(name: string) {
    currentSlot.value = name;
}

async function hideOverlay() {
    currentSlot.value = null;
}

defineExpose({ showOverlay, hideOverlay });
</script>

<template>
    <div
        v-if="currentSlot"
        class="fixed w-dvw h-dvh top-0 left-0 right-0 bottom-0 bg-black/80 z-20"
    >
        <slot :name="currentSlot"></slot>
    </div>
</template>
