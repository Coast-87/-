<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div v-if="!userStore.isAdmin" class="text-center py-20">
      <div class="text-6xl mb-4">🚫</div>
      <p class="text-gray-400 text-lg">需要管理员权限</p>
      <router-link to="/" class="btn-primary inline-block mt-4">返回首页</router-link>
    </div>

    <template v-else>
      <h2 class="text-2xl font-bold text-gray-800 mb-6">🔧 管理员管控面板</h2>

      <!-- Tab 切换 -->
      <div class="flex gap-2 mb-6">
        <button v-for="t in tabs" :key="t.value" @click="switchTab(t.value)"
          class="px-5 py-2 rounded-xl text-sm font-medium transition-all"
          :class="activeTab === t.value ? 'bg-primary-600 text-white shadow-sm' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'">
          {{ t.label }}
        </button>
      </div>

      <!-- 商品列表（违规/全部） -->
      <template v-if="activeTab !== 'users'">
        <div class="space-y-3">
          <div v-for="p in products" :key="p.id" class="card p-4 flex items-center gap-4">
            <div class="w-16 h-16 rounded-xl bg-gray-100 flex-shrink-0 overflow-hidden">
              <img v-if="p.images && p.images.length" :src="p.images[0]" class="w-full h-full object-cover" />
              <div v-else class="w-full h-full flex items-center justify-center text-xl text-gray-300">📦</div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <h4 class="font-medium text-gray-800 truncate">{{ p.title }}</h4>
                <span v-if="p.is_flagged" class="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full flex-shrink-0">⚠️ 违规</span>
                <span :class="statusClass(p.status)" class="text-xs px-2 py-0.5 rounded-full flex-shrink-0">{{ statusLabel(p.status) }}</span>
              </div>
              <p class="text-xs text-gray-400 mt-1">{{ p.category }} · {{ p.condition }} · ¥{{ p.ai_price_min }}~¥{{ p.ai_price_max }}</p>
              <p class="text-xs text-gray-400">发布者ID: {{ p.user_id || '未知' }} · {{ formatDate(p.created_at) }}</p>
            </div>
            <div class="flex gap-2 flex-shrink-0">
              <button v-if="!p.is_flagged" @click="flag(p.id)" class="text-xs py-1.5 px-3 bg-orange-50 text-orange-600 rounded-lg hover:bg-orange-100">🚩 标记违规</button>
              <button v-if="p.is_flagged" @click="unflag(p.id)" class="btn-secondary text-xs py-1.5 px-3">✅ 放行</button>
              <button v-if="p.status === 'active'" @click="offline(p.id)" class="btn-secondary text-xs py-1.5 px-3 text-orange-600">📦 下架</button>
              <router-link :to="`/product/${p.id}`" class="btn-secondary text-xs py-1.5 px-3">查看</router-link>
              <button @click="remove(p.id)" class="text-xs py-1.5 px-3 bg-red-50 text-red-600 rounded-lg hover:bg-red-100">🗑 删除</button>
            </div>
          </div>
        </div>

        <div v-if="!products.length && !loading" class="text-center py-12 text-gray-400">暂无数据</div>

        <!-- 分页 -->
        <div v-if="total > pageSize" class="flex justify-center items-center gap-3 mt-8">
          <button @click="page--; fetchData()" :disabled="page <= 1" class="btn-secondary text-sm">上一页</button>
          <span class="text-sm text-gray-500">第 {{ page }} / {{ Math.ceil(total / pageSize) }} 页</span>
          <button @click="page++; fetchData()" :disabled="page >= Math.ceil(total / pageSize)" class="btn-secondary text-sm">下一页</button>
        </div>
      </template>

      <!-- 用户管理 -->
      <template v-else>
        <!-- 新增账号 -->
        <div class="card p-4 mb-4">
          <button @click="showCreate = !showCreate" class="btn-primary text-sm">
            {{ showCreate ? "❌ 收起表单" : "➕ 新增账号" }}
          </button>
          <div v-if="showCreate" class="mt-4 grid grid-cols-1 sm:grid-cols-4 gap-3">
            <input v-model="newUser.username" placeholder="用户名（中文/英文/数字，2-20位）" class="input-field" />
            <input v-model="newUser.password" type="password" placeholder="初始密码" class="input-field" />
            <select v-model="newUser.role" class="input-field">
              <option value="admin">👑 管理员</option>
              <option value="user">普通用户</option>
            </select>
            <button @click="createUser" class="btn-primary text-sm">创建账号</button>
          </div>
          <p v-if="showCreate" class="text-xs text-gray-400 mt-2">密码规则：至少8位，需包含字母+数字、字母+符号、或数字+符号中至少两种组合。新用户登录后可自行修改密码。</p>
        </div>

        <!-- 用户列表 -->
        <div class="space-y-3">
          <div v-for="u in users" :key="u.id" class="card p-4 flex items-center gap-4">
            <div class="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center text-xl flex-shrink-0">
              {{ u.role === 'admin' ? '👑' : '👤' }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <h4 class="font-medium text-gray-800 truncate">{{ u.username }}<span v-if="u.id === userStore.user?.id" class="text-xs text-gray-400">（我）</span></h4>
                <span v-if="u.role === 'admin'" class="text-xs bg-purple-100 text-purple-600 px-2 py-0.5 rounded-full flex-shrink-0">👑 管理员</span>
                <span v-else class="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full flex-shrink-0">普通用户</span>
              </div>
              <p class="text-xs text-gray-400 mt-1">在售商品 {{ u.product_count }} 件 · 注册时间 {{ formatDate(u.created_at) }}</p>
            </div>
            <div class="flex gap-2 flex-shrink-0">
              <button v-if="u.role === 'user'" @click="setRole(u, 'admin')" class="text-xs py-1.5 px-3 bg-purple-50 text-purple-600 rounded-lg hover:bg-purple-100">👑 设为管理员</button>
              <button v-if="u.role === 'admin' && u.id !== userStore.user?.id" @click="setRole(u, 'user')" class="btn-secondary text-xs py-1.5 px-3">取消管理员</button>
              <button v-if="u.id !== userStore.user?.id" @click="removeUser(u)" class="text-xs py-1.5 px-3 bg-red-50 text-red-600 rounded-lg hover:bg-red-100">🗑 删除账号</button>
            </div>
          </div>
        </div>

        <div v-if="!users.length && !loading" class="text-center py-12 text-gray-400">暂无数据</div>
      </template>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getFlaggedProducts, getAllProducts, adminOffline, adminDelete, adminUnflag, adminFlag, getAdminUsers, adminCreateUser, adminSetRole, adminDeleteUser } from "../api";
import { userStore } from "../stores/user";

const tabs = [
  { label: "🚩 违规标记", value: "flagged" },
  { label: "📋 全部商品", value: "all" },
  { label: "👥 用户管理", value: "users" },
];
const activeTab = ref("flagged");
const products = ref([]);
const users = ref([]);
const loading = ref(false);
const page = ref(1);
const pageSize = 20;
const total = ref(0);

const showCreate = ref(false);
const newUser = ref({ username: "", password: "", role: "admin" });

function switchTab(t) {
  activeTab.value = t;
  page.value = 1;
  fetchData();
}

function statusLabel(s) { return { active: "在售", sold: "已售", offline: "已下架" }[s] || s; }
function statusClass(s) { return { active: "bg-green-100 text-green-700", sold: "bg-red-100 text-red-700", offline: "bg-gray-100 text-gray-500" }[s] || ""; }
function formatDate(d) { return d ? new Date(d).toLocaleString("zh-CN") : ""; }
function errDetail(e) {
  const d = e.response?.data?.detail;
  if (Array.isArray(d)) return d[0]?.msg || JSON.stringify(d);
  return d || "操作失败";
}

async function fetchData() {
  loading.value = true;
  try {
    if (activeTab.value === "users") {
      const res = await getAdminUsers({ page: page.value, page_size: pageSize });
      users.value = res.items;
      total.value = res.total;
    } else {
      const fn = activeTab.value === "flagged" ? getFlaggedProducts : getAllProducts;
      const res = await fn({ page: page.value, page_size: pageSize });
      products.value = res.items;
      total.value = res.total;
    }
  } catch (e) {
    console.error(e);
    alert(errDetail(e));
  } finally {
    loading.value = false;
  }
}

async function offline(id) {
  if (!confirm("确认下架该商品？")) return;
  await adminOffline(id);
  fetchData();
}

async function remove(id) {
  if (!confirm("确认永久删除该商品？此操作不可撤销！")) return;
  await adminDelete(id);
  fetchData();
}

async function flag(id) {
  if (!confirm("确认将该商品标记为违规？将被强制下架")) return;
  await adminFlag(id);
  fetchData();
}

async function unflag(id) {
  await adminUnflag(id);
  fetchData();
}

async function createUser() {
  const u = newUser.value;
  if (!u.username.trim() || !u.password) { alert("请填写用户名和密码"); return; }
  try {
    const res = await adminCreateUser({ username: u.username.trim(), password: u.password, role: u.role });
    alert(`账号创建成功：${res.username}（${res.role === "admin" ? "管理员" : "普通用户"}），初始密码即刚才填写的密码`);
    newUser.value = { username: "", password: "", role: "admin" };
    showCreate.value = false;
    fetchData();
  } catch (e) {
    alert(errDetail(e));
  }
}

async function setRole(u, role) {
  const tip = role === "admin" ? `确认将「${u.username}」设为管理员？` : `确认取消「${u.username}」的管理员权限？`;
  if (!confirm(tip)) return;
  try {
    await adminSetRole(u.id, role);
    fetchData();
  } catch (e) {
    alert(errDetail(e));
  }
}

async function removeUser(u) {
  if (!confirm(`确认删除账号「${u.username}」？\n其名下 ${u.product_count} 件商品将被一并删除，此操作不可撤销！`)) return;
  try {
    await adminDeleteUser(u.id);
    fetchData();
  } catch (e) {
    alert(errDetail(e));
  }
}

onMounted(fetchData);
</script>
