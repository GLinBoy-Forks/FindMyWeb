<script setup lang="ts">
import { ref, useTemplateRef } from "vue";
import { Icon } from "@iconify/vue";

import SidebarEntry from "./SidebarEntry.vue";
import FindMyWeb, { Accessory } from "../lib/FindMyWeb.ts";
import { locationDateString } from "../lib/helpers.ts";

const emit = defineEmits(["selected", "newAccessory", "configure"]);

const show_sidebar = ref(true);
const sidebarEntries =
    useTemplateRef<Array<typeof SidebarEntry>>("sidebarEntries");

const FindMyWebAPI = new FindMyWeb();

let toggled: number | null = null;

let tags = ref<Array<any>>([]);

async function updateSidebar(new_state: boolean) {
    show_sidebar.value = new_state;
}

async function updateTags(allTags: Accessory[]) {
    if (!allTags) {
        tags.value = [];
        return;
    }

    const newTags = [];

    for (let i = 0; i < allTags.length; i++) {
        const tag = allTags[i];
        if (!tag.name) {
            continue;
        }

        const locationResp = await FindMyWebAPI.getLocation(tag.name);
        let lastSeenStr = "Never";
        if (locationResp.location) {
            lastSeenStr = await locationDateString(locationResp.location);
        }
        // @ts-ignore: Dynamic indexing
        newTags.push({
            name: tag.name,
            icon: tag.icon,
            color: tag.color,
            lastSeen: lastSeenStr,
        });
    }
    tags.value = newTags;
}

async function onSelect(tag: any, index: number) {
    if (!sidebarEntries.value) {
        return;
    }
    let newSelected = sidebarEntries.value[index];
    if (toggled == null || toggled != index) {
        if (toggled != null) {
            sidebarEntries.value[toggled].toggle(false);
        }

        newSelected.toggle(true);
        toggled = index;
        emit("selected", tag.name);
    } else {
        newSelected.toggle(false);
        toggled = null;
        emit("selected", null);
    }
}

async function onConfigure(key: string) {
    emit("configure", key);
}

defineExpose({ updateSidebar, updateTags });
</script>

<template>
    <div
        v-show="show_sidebar"
        class="absolute w-4/5 md:w-2/5 xs:w-1/3 xl:w-1/4 h-full z-10 bg-gray-700/90 bg-opacity-40 overflow-y-auto"
    >
        <div class="flex flex-col gap-y-3 justify-start mx-5 my-5">
            <SidebarEntry
                ref="sidebarEntries"
                v-for="(tag, index) in tags"
                @click="onSelect(tag, index)"
                @configure="onConfigure(tag.name)"
                :name="tag.name"
                :icon="tag.icon"
                :color="tag.color"
                :last-seen="tag.lastSeen"
                :key="tag.name"
            />
            <button
                class="my-5 py-1.5 px-1.5 w-full hover:bg-gray-800/60 rounded-3xl shadow-2xl border-2 border-gray-900"
                @click="emit('newAccessory')"
            >
                <Icon
                    class="size-14 mx-auto my-auto"
                    icon="mdi:add"
                    color="#ffffff"
                />
            </button>
        </div>
    </div>
</template>
