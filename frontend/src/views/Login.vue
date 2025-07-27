<script setup lang="ts">
import FindMyWeb from "../lib/FindMyWeb";
import { useRouter } from "vue-router";
import { Icon } from "@iconify/vue";
import { ref } from "vue";

const router = useRouter();
const isLoading = ref(false);
const FindMyWebAPI = new FindMyWeb();

let username: string = "";
let password: string = "";

async function login() {
    try {
        isLoading.value = true;
        await FindMyWebAPI.login(username, password);
    } catch (error) {
        alert(error);
        isLoading.value = false;
        return;
    }
    router.push({ name: "Dashboard" });
}
</script>

<template>
    <section v-on:keyup.enter="login()">
        <div class="h-dvh">
            <main class="flex items-center justify-center">
                <div class="max-w-xl">
                    <h1 class="mt-6 text-5xl font-bold text-amber-500">
                        Welcome to FindMyWeb
                    </h1>
                    <div class="mt-8 grid grid-cols-1 gap-6">
                        <div class="sm:col-span-1">
                            <label
                                for="username"
                                class="block text-m font-medium text-white"
                            >
                                Username
                            </label>

                            <input
                                type="text"
                                id="username"
                                v-model="username"
                                class="mt-1 w-full rounded-md border-gray-200 text-m bg-slate-500 text-gray-100 shadow-sm p-2"
                            />
                        </div>

                        <div class="col-span-1">
                            <label
                                for="password"
                                class="block text-m font-medium text-white"
                            >
                                Password
                            </label>

                            <input
                                type="password"
                                id="password"
                                v-model="password"
                                class="mt-1 w-full rounded-md border-gray-200 bg-slate-500 text-m text-gray-100 shadow-sm p-2"
                            />
                        </div>

                        <div class="col-span-1">
                            <div
                                class="relative mt-1 w-full h-10 rounded-full text-m text-gray-300 border-gray-200 hover:bg-blue-700 bg-blue-600 shadow-sm p-2"
                            >
                                <input
                                    type="submit"
                                    id="submit"
                                    name="submit"
                                    v-on:click="login()"
                                    value="Login"
                                    class="w-full h-full"
                                    :class="isLoading ? 'opacity-50' : ''"
                                />
                                <Icon
                                    v-if="isLoading"
                                    class="absolute size-full top-0 left-0"
                                    icon="line-md:loading-loop"
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    </section>
</template>

<style scoped></style>
