<script setup lang="ts">
import { Icon } from "@iconify/vue";
import { ref } from "vue";

const isToggled = ref(false);

const props = defineProps(["icon", "name", "route_name"]);
const emit = defineEmits(["toggle"]);

async function onToggle() {
    emit("toggle");
}

async function toggle(state: boolean) {
    isToggled.value = state;
}

defineExpose({ toggle, route: props.route_name });
</script>
<template>
    <div
        @click="onToggle()"
        class="flex flex-row gap-x-3 p-4 rounded-2xl cursor-pointer"
        :class="[isToggled ? 'bg-gray-900' : 'hover:bg-gray-800']"
    >
        <Icon class="size-10" :icon="props.icon" />
        <p class="mt-auto mb-auto">{{ props.name }}</p>
    </div>
</template>
