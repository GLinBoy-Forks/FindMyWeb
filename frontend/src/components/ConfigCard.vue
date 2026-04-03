<script setup lang="ts"></script>

<template>
    <div class="h-full flex flex-row items-center justify-center">
        <div
            class="md:p-8 p-10 ml-4 mr-4 rounded-lg shadow-black shadow-2xl w-full md:w-[80%] lg:w-[60%] xl:w-[50%] 2xl:w-[40%] bg-gray-800 flex flex-col ring-4 ring-gray-900"
        >
            <slot></slot>
        </div>
    </div>
</template>
