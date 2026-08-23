<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div v-if="!userStore.isLoggedIn" class="text-center py-20">
      <div class="text-6xl mb-4">🔒</div>
      <p class="text-gray-400 text-lg mb-4">请先登录后查看个人中心</p>
      <router-link to="/login" class="btn-primary inline-block">去登录</router-link>
    </div>

    <template v-else>
      <!-- 用户信息卡片 -->
      <div class="card p-6 mb-6">
        <div class="flex items-center gap-4">
          <!-- 可点击上传头像 -->
          <div class="relative group cursor-pointer" @click="$refs.avatarInput.click()" title="点击更换头像">
            <div v-if="userStore.user.avatar" class="w-16 h-16 rounded-2xl overflow-hidden shadow-sm">
              <img :src="userStore.user.avatar" class="w-full h-full object-cover" />
            </div>
            <div v-else class="w-16 h-16 bg-gradient-to-br from-primary-500 to-accent-500 rounded-2xl flex items-center justify-center text-white text-2xl font-bold shadow-sm">
              {{ userStore.user.username[0].toUpperCase() }}
            </div>
            <!-- 悬浮遮罩 -->
            <div class="absolute inset-0 rounded-2xl bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
              <span class="text-white text-xl">📷</span>
            </div>
            <input ref="avatarInput" type="file" accept="image/*" class="hidden" @change="handleAvatarUpload" />
          </div>
          <div>
            <h2 class="text-xl font-bold text-gray-800">{{ userStore.user.username }}</h2>
            <p class="text-sm text-gray-400">
              {{ userStore.isAdmin ? '🔧 管理员' : '👤 普通用户' }} ·
              注册于 {{ formatDate(userStore.user.created_at) }}
            </p>
            <p v-if="userStore.user.phone" class="text-sm text-gray-400">
              📱 {{ userStore.user.phone }}
            </p>
          </div>
          <div class="ml-auto flex gap-2">
            <button @click="showPwdModal = true" class="btn-secondary text-sm">🔐 修改密码</button>
            <router-link v-if="userStore.isAdmin" to="/admin" class="btn-secondary text-sm">🔧 管理面板</router-link>
            <button @click="handleLogout" class="btn-secondary text-sm text-red-500">退出登录</button>
          </div>
        </div>
      </div>

      <!-- ========== 修改密码浮窗 ========== -->
      <Teleport to="body">
        <Transition name="modal">
          <div
            v-if="showPwdModal"
            class="fixed inset-0 z-50 flex items-center justify-center p-4"
            @click.self="closePwdModal"
          >
            <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
            <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 z-10">
              <div class="flex items-center justify-between mb-5">
                <h3 class="text-lg font-bold text-gray-800">🔐 修改密码</h3>
                <button
                  @click="closePwdModal"
                  class="w-8 h-8 rounded-full flex items-center justify-center text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
                >
                  ✕
                </button>
              </div>
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">旧密码</label>
                  <input
                    v-model="pwdForm.oldPassword"
                    type="password"
                    class="input-field"
                    placeholder="请输入当前密码"
                    @keyup.enter="handleChangePassword"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">新密码</label>
                  <input
                    v-model="pwdForm.newPassword"
                    type="password"
                    class="input-field"
                    :class="{ 'border-red-400 ring-2 ring-red-200': pwdError }"
                    placeholder="至少8位，需包含字母+数字（或字母+符号、数字+符号）"
                    @input="pwdError = ''"
                    @keyup.enter="handleChangePassword"
                  />
                  <p v-if="pwdError" class="text-red-500 text-xs mt-1">{{ pwdError }}</p>
                </div>
                <div v-if="pwdSuccess" class="text-green-600 text-sm bg-green-50 rounded-lg px-3 py-2">{{ pwdSuccess }}</div>
                <div v-if="pwdFail" class="text-red-500 text-sm bg-red-50 rounded-lg px-3 py-2">{{ pwdFail }}</div>
                <div class="flex gap-3 pt-2">
                  <button @click="closePwdModal" class="flex-1 btn-secondary">取消</button>
                  <button
                    @click="handleChangePassword"
                    :disabled="pwdLoading"
                    class="flex-1 btn-primary"
                  >
                    {{ pwdLoading ? '修改中...' : '确认修改' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- ========== 删除商品确认弹窗 ========== -->
      <Teleport to="body">
        <Transition name="modal">
          <div
            v-if="deleteTarget"
            class="fixed inset-0 z-50 flex items-center justify-center p-4"
            @click.self="deleteTarget = null"
          >
            <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
            <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 z-10">
              <h3 class="text-lg font-bold text-gray-800 mb-2">🗑️ 删除商品</h3>
              <p class="text-sm text-gray-500 mb-5">
                确定删除「{{ deleteTarget.title }}」吗？删除后无法恢复。
              </p>
              <div class="flex gap-3">
                <button @click="deleteTarget = null" class="flex-1 btn-secondary">取消</button>
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
        </Transition>
      </Teleport>

      <!-- 统计 -->
      <div class="grid grid-cols-3 gap-4 mb-6">
        <div class="card p-4 text-center">
          <p class="text-2xl font-bold text-primary-600">{{ totalActive }}</p>
          <p class="text-xs text-gray-400">在售中</p>
        </div>
        <div class="card p-4 text-center">
          <p class="text-2xl font-bold text-red-500">{{ totalSold }}</p>
          <p class="text-xs text-gray-400">已售出</p>
        </div>
        <div class="card p-4 text-center">
          <p class="text-2xl font-bold text-gray-400">{{ totalOffline }}</p>
          <p class="text-xs text-gray-400">已下架</p>
        </div>
      </div>

      <!-- 状态筛选 -->
      <div class="flex gap-2 mb-4">
        <button v-for="s in statusTabs" :key="s.value" @click="filterStatus = s.value; fetchProducts()"
          class="px-4 py-1.5 rounded-full text-sm font-medium transition-all"
          :class="filterStatus === s.value ? 'bg-primary-600 text-white' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'">
          {{ s.label }}
        </button>
      </div>

      <!-- 商品列表 -->
      <div v-if="products.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="p in products" :key="p.id" class="card p-4 flex gap-3">
          <div class="w-20 h-20 rounded-xl bg-gray-100 flex-shrink-0 overflow-hidden">
            <img v-if="p.images && p.images.length" :src="p.images[0]" class="w-full h-full object-cover" />
            <div v-else class="w-full h-full flex items-center justify-center text-2xl text-gray-300">📦</div>
          </div>
          <div class="flex-1 min-w-0">
            <h4 class="font-medium text-gray-800 truncate">{{ p.title }}</h4>
            <p class="text-xs text-gray-400">{{ p.category }} · {{ p.condition }}</p>
            <div class="flex items-center gap-2 mt-1">
              <span class="text-sm font-bold text-accent-600">¥{{ p.ai_price_min || '?' }}</span>
              <span :class="statusClass(p.status)" class="text-xs px-2 py-0.5 rounded-full">{{ statusLabel(p.status) }}</span>
              <span v-if="p.is_flagged" class="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full">⚠️ 违规</span>
            </div>
            <div class="flex gap-2 mt-2">
              <router-link :to="'/product/' + p.id" class="text-xs text-primary-600 hover:underline">查看</router-link>
              <button v-if="p.status === 'active'" @click="updateStatus(p.id, 'sold')" class="text-xs text-green-600 hover:underline">标记已售</button>
              <button v-if="p.status === 'active'" @click="updateStatus(p.id, 'offline')" class="text-xs text-gray-400 hover:underline">下架</button>
              <button v-if="p.status !== 'active'" @click="updateStatus(p.id, 'active')" class="text-xs text-primary-600 hover:underline">重新上架</button>
              <button @click="confirmDelete(p)" class="text-xs text-red-400 hover:text-red-600 hover:underline">删除</button>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="!loading" class="text-center py-12 text-gray-400">
        <p>暂无商品</p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getMyProducts, updateProduct, deleteProduct, changePassword, uploadAvatar } from "../api";
import { userStore } from "../stores/user";

const router = useRouter();

const filterStatus = ref("");
const statusTabs = [
  { label: "全部", value: "" },
  { label: "在售中", value: "active" },
  { label: "已售出", value: "sold" },
  { label: "已下架", value: "offline" },
];

const products = ref([]);
const loading = ref(false);
const totalActive = ref(0);
const totalSold = ref(0);
const totalOffline = ref(0);

// 修改密码
const showPwdModal = ref(false);
const pwdForm = ref({ oldPassword: "", newPassword: "" });
const pwdLoading = ref(false);
const pwdError = ref("");
const pwdSuccess = ref("");
const pwdFail = ref("");

// 删除商品
const deleteTarget = ref(null);
const deleteLoading = ref(false);

function statusLabel(s) { return { active: "在售", sold: "已售", offline: "已下架" }[s] || s; }
function statusClass(s) { return { active: "bg-green-100 text-green-700", sold: "bg-red-100 text-red-700", offline: "bg-gray-100 text-gray-500" }[s] || ""; }
function formatDate(d) { return d ? new Date(d).toLocaleDateString("zh-CN") : ""; }

function handleLogout() {
  userStore.logout();
  router.push("/");
}

async function handleAvatarUpload(e) {
  const file = e.target.files[0];
  if (!file) return;
  // 前端校验
  if (!file.type.startsWith("image/")) {
    alert("请选择图片文件");
    return;
  }
  if (file.size > 10 * 1024 * 1024) {
    alert("图片大小不能超过 10MB");
    return;
  }
  try {
    const res = await uploadAvatar(file);
    userStore.updateAvatar(res.avatar);
  } catch (err) {
    const detail = err.response?.data?.detail;
    alert(typeof detail === "string" ? detail : "头像上传失败，请重试");
  }
}

function closePwdModal() {
  showPwdModal.value = false;
  pwdForm.value = { oldPassword: "", newPassword: "" };
  pwdError.value = "";
  pwdSuccess.value = "";
  pwdFail.value = "";
}

async function fetchStats() {
  try {
    const [a, s, o] = await Promise.all([
      getMyProducts({ status: "active", page_size: 1 }),
      getMyProducts({ status: "sold", page_size: 1 }),
      getMyProducts({ status: "offline", page_size: 1 }),
    ]);
    totalActive.value = a.total;
    totalSold.value = s.total;
    totalOffline.value = o.total;
  } catch (e) {
    console.error("统计刷新失败", e);
  }
}

async function fetchProducts() {
  loading.value = true;
  try {
    const params = {};
    if (filterStatus.value) params.status = filterStatus.value;
    const res = await getMyProducts(params);
    products.value = res.items;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
  await fetchStats();
}

async function updateStatus(id, status) {
  try {
    await updateProduct(id, { status });
    fetchProducts();
  } catch (e) {
    alert("操作失败");
  }
}

function confirmDelete(p) {
  deleteTarget.value = p;
}

async function handleDelete() {
  if (!deleteTarget.value) return;
  deleteLoading.value = true;
  try {
    await deleteProduct(deleteTarget.value.id);
    deleteTarget.value = null;
    await fetchProducts();
  } catch (e) {
    const detail = e.response?.data?.detail;
    alert(typeof detail === "string" ? detail : "删除失败，请重试");
  } finally {
    deleteLoading.value = false;
  }
}

function validatePassword(v) {
  if (v.length < 8) return "密码至少 8 位";
  const hasLetter = /[a-zA-Z]/.test(v);
  const hasDigit = /\d/.test(v);
  const hasSpecial = /[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;\/]/.test(v);
  const types = [hasLetter, hasDigit, hasSpecial].filter(Boolean).length;
  if (types < 2) return "密码需包含字母、数字、符号中的至少两种";
  return "";
}

async function handleChangePassword() {
  pwdError.value = "";
  pwdSuccess.value = "";
  pwdFail.value = "";

  if (!pwdForm.value.oldPassword) {
    pwdFail.value = "请输入旧密码";
    return;
  }
  const err = validatePassword(pwdForm.value.newPassword);
  if (err) {
    pwdError.value = err;
    return;
  }

  pwdLoading.value = true;
  try {
    const res = await changePassword(pwdForm.value.oldPassword, pwdForm.value.newPassword);
    pwdSuccess.value = res.message || "密码修改成功";
    setTimeout(() => { closePwdModal(); }, 1500);
  } catch (e) {
    const detail = e.response?.data?.detail;
    if (detail && typeof detail === "string") {
      pwdFail.value = detail;
    } else if (e.response?.status === 422) {
      const errs = e.response.data?.detail;
      pwdFail.value = Array.isArray(errs) && errs.length ? (errs[0].msg || "输入格式有误") : "输入格式有误";
    } else {
      pwdFail.value = "修改失败，请重试";
    }
  } finally {
    pwdLoading.value = false;
  }
}

onMounted(fetchProducts);
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.25s ease;
}
.modal-enter-active > div:last-child,
.modal-leave-active > div:last-child {
  transition: transform 0.25s ease, opacity 0.25s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from > div:last-child {
  transform: scale(0.92) translateY(10px);
  opacity: 0;
}
.modal-leave-to > div:last-child {
  transform: scale(0.92) translateY(10px);
  opacity: 0;
}
</style>


