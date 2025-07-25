<script setup lang="ts"></script>

<template>
    <main>
        <RouterView v-slot="{ Component }">
            <KeepAlive :include="['Dashboard']">
                <component :is="Component" />
            </KeepAlive>
        </RouterView>
    </main>
</template>

<script>
export default {
    name: "App",
};
</script>
