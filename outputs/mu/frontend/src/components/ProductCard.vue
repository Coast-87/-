<template>
  <router-link :to="`/product/${product.id}`" class="card group block">
    <!-- 图片区 -->
    <div class="relative aspect-[4/3] bg-gray-100 overflow-hidden">
      <img
        v-if="product.images && product.images.length"
        :src="product.images[0]"
        :alt="product.title"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-5xl text-gray-300">
        📦
      </div>

      <!-- 已售出/已下架角标 -->
      <div
        v-if="product.status === 'sold'"
        class="absolute inset-0 bg-black/40 flex items-center justify-center"
      >
        <span class="bg-red-500 text-white px-4 py-2 rounded-xl text-sm font-bold rotate-[-15deg] shadow-lg">
          已售出
        </span>
      </div>
      <div
        v-if="product.status === 'offline'"
        class="absolute inset-0 bg-black/40 flex items-center justify-center"
      >
        <span class="bg-gray-500 text-white px-4 py-2 rounded-xl text-sm font-bold rotate-[-15deg] shadow-lg">
          已下架
        </span>
      </div>

      <!-- 分类标签 -->
      <span class="absolute top-3 left-3 bg-white/90 backdrop-blur-sm text-xs font-medium px-2.5 py-1 rounded-lg text-gray-600 shadow-sm">
        {{ product.category }}
      </span>
    </div>

    <!-- 信息区 -->
    <div class="p-4" :class="{ 'opacity-50': product.status !== 'active' }">
      <h3 class="font-semibold text-gray-800 line-clamp-1 mb-1.5">{{ product.title }}</h3>
      
      <!-- AI 标签 -->
      <div v-if="product.ai_tags && product.ai_tags.length" class="flex flex-wrap gap-1 mb-2">
        <span
          v-for="tag in product.ai_tags.slice(0, 3)"
          :key="tag"
          class="text-xs bg-primary-50 text-primary-700 px-2 py-0.5 rounded-full font-medium"
        >
          {{ tag }}
        </span>
      </div>

      <!-- 价格 -->
      <div class="flex items-baseline gap-2">
        <span v-if="product.ai_price_min != null" class="text-lg font-bold text-accent-600">
          ¥{{ product.ai_price_min }}
        </span>
        <span v-if="product.ai_price_max != null && product.ai_price_max !== product.ai_price_min" class="text-sm text-gray-400">
          ~ ¥{{ product.ai_price_max }}
        </span>
      </div>

      <!-- 时间 -->
      <p class="text-xs text-gray-400 mt-2">
        {{ formatTime(product.created_at) }}
      </p>
    </div>
  </router-link>
</template>

<script setup>
defineProps({
  product: { type: Object, required: true },
});

function formatTime(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  const now = new Date();
  const diff = now - d;
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`;
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`;
  return d.toLocaleDateString("zh-CN");
}
</script>
