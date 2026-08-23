<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 加载中 -->
    <div v-if="loading" class="text-center py-20">
      <div class="animate-spin w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full mx-auto"></div>
    </div>

    <template v-else-if="product">
      <!-- 面包屑 -->
      <div class="flex items-center gap-2 text-sm text-gray-400 mb-6">
        <router-link to="/" class="hover:text-primary-600">市场</router-link>
        <span>/</span>
        <span class="text-gray-600">{{ product.title }}</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <!-- 图片区 -->
        <div class="space-y-3">
          <div class="aspect-square rounded-2xl overflow-hidden bg-gray-100">
            <img
              v-if="product.images && product.images.length"
              :src="currentImage"
              class="w-full h-full object-cover"
            />
            <div v-else class="w-full h-full flex items-center justify-center text-7xl text-gray-300">
              📦
            </div>
          </div>
          <!-- 缩略图 -->
          <div v-if="product.images && product.images.length > 1" class="flex gap-2">
            <button
              v-for="(img, i) in product.images"
              :key="i"
              @click="currentImage = img"
              class="w-16 h-16 rounded-lg overflow-hidden border-2 transition-colors"
              :class="currentImage === img ? 'border-primary-500' : 'border-gray-200'"
            >
              <img :src="img" class="w-full h-full object-cover" />
            </button>
          </div>
        </div>

        <!-- 信息区 -->
        <div class="space-y-5">
          <!-- 状态标签 -->
          <div class="flex items-center gap-2">
            <span
              class="px-3 py-1 rounded-full text-xs font-bold"
              :class="statusBadgeClass"
            >
              {{ statusLabel }}
            </span>
            <span class="text-sm text-gray-400">{{ formatTime(product.created_at) }}</span>
          </div>

          <h1 class="text-2xl font-bold text-gray-800">{{ product.title }}</h1>

          <!-- AI 标签 -->
          <div v-if="product.ai_tags && product.ai_tags.length" class="flex flex-wrap gap-2">
            <span
              v-for="tag in product.ai_tags"
              :key="tag"
              class="text-sm bg-primary-50 text-primary-700 px-3 py-1 rounded-full font-medium"
            >
              {{ tag }}
            </span>
          </div>

          <!-- 价格 -->
          <div class="bg-accent-50 rounded-2xl p-4">
            <p class="text-sm text-accent-600 mb-1">💡 AI 推荐价格</p>
            <div class="flex items-baseline gap-2">
              <span v-if="product.ai_price_min != null" class="text-3xl font-bold text-accent-600">
                ¥{{ product.ai_price_min }}
              </span>
              <span v-if="product.ai_price_max != null && product.ai_price_max !== product.ai_price_min" class="text-lg text-accent-400">
                ~ ¥{{ product.ai_price_max }}
              </span>
            </div>
          </div>

          <!-- 分类 & 成色 -->
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-gray-50 rounded-xl p-3">
              <p class="text-xs text-gray-400 mb-1">📂 分类</p>
              <p class="font-medium text-gray-700">{{ product.category }}</p>
            </div>
            <div class="bg-gray-50 rounded-xl p-3">
              <p class="text-xs text-gray-400 mb-1">⭐ 成色</p>
              <p class="font-medium text-gray-700">{{ product.condition }}</p>
            </div>
          </div>

          <!-- 文案 -->
          <div v-if="product.ai_copy">
            <h3 class="font-semibold text-gray-700 mb-2">📝 商品描述</h3>
            <div class="bg-gray-50 rounded-xl p-4 text-gray-600 leading-relaxed whitespace-pre-wrap">
              {{ product.ai_copy }}
            </div>
          </div>

          <!-- 联系方式 -->
          <div v-if="product.contact" class="border border-primary-200 bg-primary-50/50 rounded-2xl p-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xs text-gray-400 mb-1">📞 卖家联系方式</p>
                <p class="font-semibold text-gray-800">{{ product.contact }}</p>
              </div>
              <button
                @click="copyContact"
                class="btn-primary text-sm flex items-center gap-1.5"
              >
                <span>{{ copied ? '✓' : '📋' }}</span>
                {{ copied ? '已复制' : '一键复制' }}
              </button>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="flex gap-3 pt-2">
            <button
              v-if="canManage && product.status === 'active'"
              @click="markSold"
              :disabled="statusUpdating"
              class="btn-secondary flex-1"
            >
              🏷️ 标记已卖出
            </button>
            <button
              v-if="canManage && product.status === 'active'"
              @click="markOffline"
              :disabled="statusUpdating"
              class="btn-secondary flex-1 text-gray-400"
            >
              📦 下架
            </button>
            <button
              v-if="canManage && product.status !== 'active'"
              @click="relist"
              :disabled="statusUpdating"
              class="btn-primary flex-1"
            >
              🔄 重新上架
            </button>
            <button
              v-if="canManage"
              @click="showDeleteModal = true"
              class="btn-secondary flex-1 text-red-500"
            >
              🗑️ 删除
            </button>
            <button
              v-if="userStore.isAdmin && !product.is_flagged"
              @click="flagProduct"
              class="btn-secondary flex-1 text-orange-500"
            >
              🚩 标记违规
            </button>
            <button
              v-if="userStore.isAdmin && product.is_flagged"
              @click="unflagProduct"
              class="btn-secondary flex-1 text-green-600"
            >
              ✅ 放行恢复
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- 商品不存在 -->
    <div v-else class="text-center py-20">
      <div class="text-6xl mb-4">😕</div>
      <p class="text-gray-400 text-lg">商品不存在或已被删除</p>
      <router-link to="/" class="btn-primary inline-block mt-4">返回市场</router-link>
    </div>

    <!-- ========== 删除商品确认弹窗 ========== -->
    <Teleport to="body">
      <div
        v-if="showDeleteModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="showDeleteModal = false"
      >
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 z-10">
          <h3 class="text-lg font-bold text-gray-800 mb-2">🗑️ 删除商品</h3>
          <p class="text-sm text-gray-500 mb-5">
            确定删除「{{ product && product.title }}」吗？删除后无法恢复。
          </p>
          <div class="flex gap-3">
            <button @click="showDeleteModal = false" class="flex-1 btn-secondary">取消</button>
            <button
              @click="handleDelete"
              :disabled="deleteLoading"
              class="flex-1 btn-danger"
            >
              {{ deleteLoading ? '删除中...' : '确认删除' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getProduct, updateProduct, deleteProduct, adminFlag, adminUnflag } from "../api";
import { userStore } from "../stores/user";

const route = useRoute();
const router = useRouter();
const product = ref(null);
const loading = ref(true);
const currentImage = ref("");
const copied = ref(false);
const statusUpdating = ref(false);
const showDeleteModal = ref(false);
const deleteLoading = ref(false);

const canManage = computed(() => {
  if (!product.value || !userStore.isLoggedIn) return false;
  return userStore.isAdmin || userStore.user?.id === product.value.user_id;
});

const statusLabel = computed(() => {
  if (!product.value) return "";
  const map = { active: "在售中", sold: "已售出", offline: "已下架" };
  return map[product.value.status] || product.value.status;
});

const statusBadgeClass = computed(() => {
  if (!product.value) return "";
  const map = {
    active: "bg-green-100 text-green-700",
    sold: "bg-red-100 text-red-700",
    offline: "bg-gray-100 text-gray-500",
  };
  return map[product.value.status] || "";
});

function formatTime(dateStr) {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleString("zh-CN");
}

async function fetchProduct() {
  loading.value = true;
  try {
    const data = await getProduct(route.params.id);
    product.value = data;
    if (data.images && data.images.length) {
      currentImage.value = data.images[0];
    }
  } catch (e) {
    console.error("获取商品失败", e);
    product.value = null;
  } finally {
    loading.value = false;
  }
}

async function copyContact() {
  if (product.value?.contact) {
    try {
      await navigator.clipboard.writeText(product.value.contact);
      copied.value = true;
      setTimeout(() => (copied.value = false), 2000);
    } catch {
      // fallback
      const ta = document.createElement("textarea");
      ta.value = product.value.contact;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      copied.value = true;
      setTimeout(() => (copied.value = false), 2000);
    }
  }
}

async function updateStatus(status) {
  statusUpdating.value = true;
  try {
    await updateProduct(route.params.id, { status });
    product.value.status = status;
  } catch (e) {
    console.error("更新状态失败", e);
    alert("操作失败，请重试");
  } finally {
    statusUpdating.value = false;
  }
}

function markSold() { updateStatus("sold"); }
function markOffline() { updateStatus("offline"); }
function relist() { updateStatus("active"); }

async function flagProduct() {
  if (!confirm("确认将该商品标记为违规？将被强制下架")) return;
  try {
    await adminFlag(route.params.id);
    product.value.is_flagged = 1;
    product.value.status = "offline";
    alert("已标记违规并下架");
  } catch (e) {
    alert(e?.response?.data?.detail || "操作失败，请重试");
  }
}

async function unflagProduct() {
  try {
    await adminUnflag(route.params.id);
    product.value.is_flagged = 0;
    product.value.status = "active";
    alert("已放行并恢复上架");
  } catch (e) {
    alert(e?.response?.data?.detail || "操作失败，请重试");
  }
}

async function handleDelete() {
  deleteLoading.value = true;
  try {
    await deleteProduct(route.params.id);
    showDeleteModal.value = false;
    router.push("/profile");
  } catch (e) {
    const detail = e.response?.data?.detail;
    alert(typeof detail === "string" ? detail : "删除失败，请重试");
    deleteLoading.value = false;
  }
}

onMounted(fetchProduct);
</script>
