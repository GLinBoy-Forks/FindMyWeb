<script setup lang="ts">
const props = defineProps(["name", "for"]);

</script setup>

<template>
    <label class="text-white text-lg md:text-xl font-bold" :for="props.for">{{ props.name }}:</label>
    <div class="flex justify-end ml-10">
        <slot></slot>
    </div>
</template>
