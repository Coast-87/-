<template>
  <nav class="bg-white shadow-sm border-b border-gray-100 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <router-link to="/market" class="flex items-center gap-2.5 group">
          <div class="w-9 h-9 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center text-white text-lg shadow-sm group-hover:shadow-md transition-shadow">
            🏪
          </div>
          <div>
            <h1 class="text-lg font-bold text-gray-800 leading-tight">校园跳蚤市场</h1>
            <p class="text-xs text-gray-400 leading-tight">AI 智能发品平台</p>
          </div>
        </router-link>

        <div class="flex items-center gap-3">
          <router-link to="/market" class="px-4 py-2 text-sm font-medium text-gray-600 hover:text-primary-600 rounded-lg hover:bg-primary-50 transition-colors" active-class="text-primary-600 bg-primary-50">
            🛍️ 市场
          </router-link>
          <router-link to="/publish" class="btn-primary text-sm flex items-center gap-1.5">
            <span>✨</span> AI 发品
          </router-link>

          <!-- 未登录 -->
          <template v-if="!userStore.isLoggedIn">
            <router-link to="/" class="px-4 py-2 text-sm font-medium text-gray-600 hover:text-primary-600 rounded-lg hover:bg-primary-50 transition-colors">
              🔑 登录
            </router-link>
          </template>

          <!-- 已登录 -->
          <template v-else>
            <router-link to="/profile" class="px-4 py-2 text-sm font-medium text-gray-600 hover:text-primary-600 rounded-lg hover:bg-primary-50 transition-colors" active-class="text-primary-600 bg-primary-50">
              👤 {{ userStore.user.username }}
            </router-link>
            <button @click="handleLogout" class="text-xs text-gray-400 hover:text-red-500 transition-colors">退出</button>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from "vue-router";
import { userStore } from "../stores/user";

const router = useRouter();

function handleLogout() {
  userStore.logout();
  router.push("/");
}
</script>
