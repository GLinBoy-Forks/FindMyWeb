<script setup lang="ts">
import { Icon } from "@iconify/vue";

const props = defineProps(["name"]);
const emit = defineEmits(["configure"]);
</script>
<template>
    <div
        class="flex flex-row gap-x-9 rounded-2xl border-2 border-gray-950 bg-gray-700"
    >
        <p class="mt-auto ml-4 mb-auto text-white text-xl font-bold">
            {{ props.name }}
        </p>

        <Icon
            @click="emit('configure', props.name)"
            class="ml-auto text-red-400 bg-gray-700 hover:bg-gray-900 rounded-2xl p-2 mt-2 mb-2 mr-2 size-14"
            icon="mdi:cog-outline"
        />
    </div>
</template>
