<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 搜索栏 -->
    <div class="mb-8 space-y-4">
      <div class="flex flex-col sm:flex-row gap-3">
        <!-- 搜索框 -->
        <div class="flex-1 relative">
          <input
            v-model="keyword"
            type="text"
            placeholder="搜索商品标题、文案..."
            class="input-field pl-10"
            @keyup.enter="search"
          />
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
        </div>
        <button @click="search" class="btn-primary">搜索</button>
      </div>

      <!-- 分类筛选 -->
      <div class="flex flex-wrap gap-2">
        <button
          v-for="cat in categories"
          :key="cat"
          @click="selectedCategory = cat; fetchProducts()"
          class="px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200"
          :class="selectedCategory === cat
            ? 'bg-primary-600 text-white shadow-sm'
            : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
          "
        >
          {{ cat }}
        </button>
      </div>
    </div>

    <!-- 商品网格 -->
    <div v-if="products.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
      <ProductCard v-for="p in products" :key="p.id" :product="p" />
    </div>

    <!-- 空状态 -->
    <div v-else-if="!loading" class="text-center py-20">
      <div class="text-6xl mb-4">📭</div>
      <p class="text-gray-400 text-lg">暂无商品，快来发布第一件吧！</p>
      <router-link to="/publish" class="btn-primary inline-block mt-4">✨ AI 智能发品</router-link>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="text-center py-20">
      <div class="animate-spin w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full mx-auto"></div>
      <p class="text-gray-400 mt-3">加载中...</p>
    </div>

    <!-- 分页 -->
    <div v-if="total > pageSize" class="flex justify-center items-center gap-3 mt-10">
      <button
        @click="page--; fetchProducts()"
        :disabled="page <= 1"
        class="btn-secondary text-sm"
      >
        上一页
      </button>
      <span class="text-sm text-gray-500">
        第 {{ page }} 页 / 共 {{ Math.ceil(total / pageSize) }} 页
      </span>
      <button
        @click="page++; fetchProducts()"
        :disabled="page >= Math.ceil(total / pageSize)"
        class="btn-secondary text-sm"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getProducts } from "../api";
import ProductCard from "../components/ProductCard.vue";

const categories = ["全部", "数码", "书籍", "生活用品", "服饰", "美妆", "运动户外", "其他"];

const products = ref([]);
const loading = ref(false);
const keyword = ref("");
const selectedCategory = ref("全部");
const page = ref(1);
const pageSize = 12;
const total = ref(0);

async function fetchProducts() {
  loading.value = true;
  try {
    const params = {
      page: page.value,
      page_size: pageSize,
      status: "active",
    };
    if (selectedCategory.value !== "全部") {
      params.category = selectedCategory.value;
    }
    if (keyword.value.trim()) {
      params.keyword = keyword.value.trim();
    }
    const res = await getProducts(params);
    products.value = res.items;
    total.value = res.total;
  } catch (e) {
    console.error("获取商品列表失败", e);
  } finally {
    loading.value = false;
  }
}

function search() {
  page.value = 1;
  fetchProducts();
}

onMounted(fetchProducts);
</script>
