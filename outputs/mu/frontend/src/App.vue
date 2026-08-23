<template>
  <div class="min-h-screen flex flex-col">
    <NavBar v-if="$route.name !== 'Welcome'" />
    <main class="flex-1" :class="{ 'welcome-main': $route.name === 'Welcome' }">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <footer v-if="$route.name !== 'Welcome'" class="bg-white border-t border-gray-100 py-6 text-center text-gray-400 text-sm">
      <p>🏪 校园跳蚤市场 · AI 智能发品平台 · Made with ❤️</p>
    </footer>
  </div>
</template>

<script setup>
import NavBar from "./components/NavBar.vue";
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.welcome-main {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
