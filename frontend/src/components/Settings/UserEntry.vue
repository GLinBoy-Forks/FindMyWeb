<script setup lang="ts">
import { Permissions, hasPermission } from "../../lib/FindMyWeb.ts";
const props = defineProps(["name", "superuser", "permissions"]);
const emit = defineEmits(["configure"]);

function get_user_type_name(): string {
    if (props.superuser) {
        return "Superuser";
    } else if (hasPermission(props.permissions, Permissions.ADMIN)) {
        return "Admin";
    } else {
        return "User";
    }
}
</script>
<template>
    <button
        class="flex flex-row gap-x-9 rounded-2xl border-2 border-gray-950 h-14"
        @click="props.superuser ? null : emit('configure', props.name)"
        :class="[
            props.superuser
                ? 'disabled cursor-not-allowed bg-gray-700/20'
                : 'cursor-pointer bg-gray-700 hover:bg-gray-800',
        ]"
    >
        <p class="mt-auto ml-4 mb-auto text-white text-xl font-bold">
            {{ props.name }}
        </p>
        <p class="mt-auto mb-auto mr-2 ml-auto text-amber-600 font-bold">
            {{ get_user_type_name() }}
        </p>
    </button>
</template>
