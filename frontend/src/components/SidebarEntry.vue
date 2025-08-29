<script setup lang="ts">
import { ref } from "vue";
import { Icon } from "@iconify/vue";

const isToggled = ref(false);

async function toggle(state: boolean) {
    isToggled.value = state;
}

const props = defineProps(["color", "name", "icon", "lastSeen", "active"]);
defineExpose({ toggle });

const emit = defineEmits(["configure"]);
</script>

<template>
    <button
        class="py-1.5 px-2 grid grid-cols-4 w-full gap-2 rounded-3xl shadow-2xl border-2 border-gray-900"
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
            class="size-9 col-start-4 col-end-4 self-center rounded-2xl ml-auto p-1.5 hover:bg-gray-800 block cursor-pointer"
            icon="mdi:cog-outline"
            :color="color"
            @click.stop="emit('configure')"
        />
    </button>
</template>
