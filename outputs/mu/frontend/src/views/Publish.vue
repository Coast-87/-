<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 标题 -->
    <div class="text-center mb-8">
      <h2 class="text-2xl font-bold text-gray-800">✨ AI 智能发品助手</h2>
      <p class="text-gray-500 mt-2">上传 1-3 张照片，AI 自动帮你分析商品、估价并生成文案</p>
    </div>

    <!-- 步骤指示器 -->
    <div class="flex items-center justify-center gap-2 mb-8">
      <div v-for="(s, i) in steps" :key="i" class="flex items-center gap-2">
        <div
          class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all"
          :class="currentStep >= i
            ? 'bg-primary-600 text-white shadow-md'
            : 'bg-gray-200 text-gray-400'"
        >
          {{ currentStep > i ? '✓' : i + 1 }}
        </div>
        <span class="text-sm" :class="currentStep >= i ? 'text-gray-700 font-medium' : 'text-gray-400'">{{ s }}</span>
        <div v-if="i < steps.length - 1" class="w-8 h-0.5" :class="currentStep > i ? 'bg-primary-400' : 'bg-gray-200'"></div>
      </div>
    </div>

    <!-- 违规拦截提示 -->
    <div v-if="errorMsg" class="bg-red-50 border border-red-300 rounded-xl px-4 py-3 mb-6 flex items-start gap-3">
      <span class="text-xl">🚫</span>
      <div class="flex-1">
        <p class="text-red-700 font-medium text-sm">内容审核未通过</p>
        <p class="text-red-500 text-xs mt-0.5">{{ errorMsg }}</p>
      </div>
      <button @click="errorMsg = ''" class="text-red-400 hover:text-red-600 text-sm">✕</button>
    </div>

    <!-- Step 1: 上传图片 -->
    <div v-if="currentStep === 0" class="card p-6">
      <h3 class="font-semibold text-lg mb-4">
        📸 上传商品图片 <span class="text-red-500 text-sm font-normal">*必填</span>（1-3张，支持一次多选）
      </h3>
      
      <!-- 无图片时的醒目提示 -->
      <div v-if="!filesCount && noImageWarning" class="bg-red-50 border border-red-300 rounded-xl px-4 py-3 mb-4 flex items-start gap-3">
        <span class="text-xl">⚠️</span>
        <div>
          <p class="text-red-700 font-medium text-sm">请先上传商品图片</p>
          <p class="text-red-500 text-xs mt-0.5">点击下方虚线框，可一次选择 1-3 张图片（Ctrl/Cmd + 点击多选）</p>
        </div>
      </div>

      <!-- 图片上传区 -->
      <div class="grid grid-cols-3 gap-3 mb-4">
        <div
          v-for="(img, i) in previews"
          :key="'p'+i"
          class="relative aspect-square rounded-xl overflow-hidden bg-gray-100 shadow-sm"
        >
          <img :src="img" class="w-full h-full object-cover" />
          <button
            @click="removeImage(i)"
            class="absolute top-2 right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs hover:bg-red-600 transition-colors shadow"
          >
            ✕
          </button>
        </div>
        <!-- 占位格子（图片未加载完时） -->
        <div
          v-for="i in (filesCount - previews.length)"
          :key="'ph'+i"
          class="aspect-square rounded-xl bg-gray-100 flex items-center justify-center"
        >
          <span class="animate-pulse text-gray-300 text-sm">加载中...</span>
        </div>
        <label
          v-if="filesCount < 3"
          class="aspect-square rounded-xl border-2 border-dashed border-gray-300 flex flex-col items-center justify-center cursor-pointer hover:border-primary-400 hover:bg-primary-50/50 transition-all"
        >
          <span class="text-3xl text-gray-300 mb-1">+</span>
          <span class="text-xs text-gray-400">{{ filesCount ? '继续添加' : '点击选择图片' }}</span>
          <input
            type="file"
            accept="image/*"
            multiple
            class="hidden"
            @change="onFileChange"
            ref="fileInput"
          />
        </label>
      </div>

      <!-- 商品信息（帮助 AI 更准确识别与估价） -->
      <div class="bg-primary-50/50 border border-primary-100 rounded-xl p-4 mb-4">
        <p class="text-sm font-medium text-gray-700 mb-3">
          💡 填写信息，AI 估价更准 <span class="text-gray-400 font-normal">（都可选，建议至少填品牌/型号）</span>
        </p>
        <div class="grid grid-cols-2 gap-3 mb-3">
          <div>
            <label class="block text-xs text-gray-500 mb-1">🏷️ 品牌 / 型号</label>
            <input v-model="brandModel" class="input-field !py-2 text-sm" placeholder="例如：Apple iPad Air 5" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">💰 购入价格（元）</label>
            <input v-model="buyPrice" type="number" min="0" class="input-field !py-2 text-sm" placeholder="例如：3999" />
          </div>
        </div>
        <div class="mb-3">
          <label class="block text-xs text-gray-500 mb-1">📅 购入时间 / 成色说明</label>
          <input v-model="buyTime" class="input-field !py-2 text-sm" placeholder="例如：去年9月入手，功能正常，配件齐全" />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">💬 其他说明</label>
          <textarea
            v-model="userNote"
            rows="2"
            class="input-field text-sm"
            placeholder="例如：毕业急出，仅限校内当面交易..."
          ></textarea>
        </div>
      </div>

      <button
        @click="startAnalysis"
        :disabled="!filesCount || analyzing"
        class="btn-primary w-full text-lg flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span v-if="analyzing" class="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></span>
        <span>{{ analyzing ? 'AI 分析中...' : '🤖 开始 AI 分析' }}</span>
      </button>
      <p v-if="!filesCount" class="text-red-500 text-sm text-center mt-2">
        ⚠️ 请先上传至少 1 张商品图片
      </p>
    </div>

    <!-- Step 2: AI 结果预览 & 微调 -->
    <div v-if="currentStep === 1" class="card p-6">
      <h3 class="font-semibold text-lg mb-4">🔍 AI 分析结果 — 请确认并微调</h3>
      
      <div class="space-y-4">
        <!-- 标题 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">商品标题</label>
          <input v-model="form.title" class="input-field" />
        </div>

        <!-- 分类 & 成色 -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">分类</label>
            <select v-model="form.category" class="input-field">
              <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">成色</label>
            <select v-model="form.condition" class="input-field">
              <option value="全新">全新</option>
              <option value="99新">99新</option>
              <option value="95新">95新</option>
              <option value="9成新">9成新</option>
              <option value="8成新">8成新</option>
              <option value="7成新">7成新</option>
              <option value="有瑕疵">有瑕疵</option>
            </select>
          </div>
        </div>

        <!-- 价格区间 -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">最低价 ¥</label>
            <input v-model.number="form.price_min" type="number" class="input-field" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">最高价 ¥</label>
            <input v-model.number="form.price_max" type="number" class="input-field" />
          </div>
        </div>

        <!-- AI 标签 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">AI 标签（逗号分隔）</label>
          <input
            v-model="tagsInput"
            class="input-field"
            placeholder="高性价比, 九成新, 正品"
          />
          <div class="flex flex-wrap gap-1 mt-2">
            <span
              v-for="tag in computedTags"
              :key="tag"
              class="text-xs bg-primary-50 text-primary-700 px-2 py-0.5 rounded-full"
            >
              {{ tag }}
            </span>
          </div>
        </div>

        <!-- 文案 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">📝 营销文案</label>
          <textarea v-model="form.copy" rows="4" class="input-field"></textarea>
          <p class="text-xs text-gray-400 mt-1">{{ form.copy.length }} / 200 字</p>
        </div>

        <!-- 联系方式 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            📞 联系方式 <span class="text-red-500">*必填</span>
          </label>
          <input
            v-model="form.contact"
            class="input-field"
            :class="{ 'border-red-400 ring-2 ring-red-200': publishAttempted && !form.contact.trim() }"
            placeholder="微信号 / QQ号 / 手机号"
          />
          <p v-if="publishAttempted && !form.contact.trim()" class="text-red-500 text-xs mt-1">
            ⚠️ 请填写联系方式，方便买家联系你
          </p>
          <p v-else class="text-gray-400 text-xs mt-1">填写后买家才能联系到你，支持线下自提</p>
        </div>
      </div>

      <div class="flex gap-3 mt-6">
        <button @click="currentStep = 0" class="btn-secondary flex-1">← 返回修改图片</button>
        <button
          @click="publishProduct"
          :disabled="publishing"
          class="btn-primary flex-1 flex items-center justify-center gap-2"
        >
          <span v-if="publishing" class="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></span>
          <span>{{ publishing ? '发布中...' : '🚀 一键发布' }}</span>
        </button>
      </div>
    </div>

    <!-- Step 3: 发布成功 -->
    <div v-if="currentStep === 2" class="card p-8 text-center">
      <div class="text-6xl mb-4">🎉</div>
      <h3 class="text-xl font-bold text-gray-800 mb-2">发布成功！</h3>
      <p class="text-gray-500 mb-6">你的商品已上架，快去市场看看吧</p>
      <div class="flex gap-3 justify-center">
        <router-link :to="'/product/' + publishedId" class="btn-primary">查看详情</router-link>
        <router-link to="/" class="btn-secondary">返回市场</router-link>
        <button @click="resetForm" class="btn-secondary">继续发布</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { analyzeImages, createProduct, uploadImage, checkText } from "../api";

const categories = ["数码", "书籍", "生活用品", "服饰", "美妆", "运动户外", "其他"];
const steps = ["上传图片", "AI 分析 & 微调", "发布成功"];

const currentStep = ref(0);
const files = ref([]);
const previews = ref([]);
const userNote = ref("");
const brandModel = ref("");
const buyPrice = ref("");
const buyTime = ref("");
const analyzing = ref(false);
const publishing = ref(false);
const publishAttempted = ref(false);
const publishedId = ref(null);
const fileInput = ref(null);
const noImageWarning = ref(false);
const errorMsg = ref("");

const form = ref({
  title: "",
  category: "生活用品",
  condition: "9成新",
  price_min: 0,
  price_max: 0,
  tags: [],
  copy: "",
  contact: "",
});

const tagsInput = ref("");

// 同步追踪文件数量，避免异步预览加载导致的 UI 闪烁
const filesCount = computed(() => files.value.length);

const computedTags = computed(() => {
  if (!tagsInput.value.trim()) return [];
  return tagsInput.value.split(",").map((t) => t.trim()).filter(Boolean);
});

async function onFileChange(e) {
  const newFiles = Array.from(e.target.files);
  const remaining = 3 - files.value.length;
  
  if (remaining <= 0) {
    e.target.value = "";
    return;
  }
  
  const toAdd = newFiles.slice(0, remaining);
  
  if (newFiles.length > remaining) {
    noImageWarning.value = false;
  }
  
  // 同步添加文件引用
  toAdd.forEach((f) => files.value.push(f));
  
  // 异步加载所有预览图
  const previewPromises = toAdd.map((f) => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (ev) => {
        previews.value.push(ev.target.result);
        resolve();
      };
      reader.onerror = () => resolve();
      reader.readAsDataURL(f);
    });
  });
  
  await Promise.all(previewPromises);
  noImageWarning.value = false;
  
  // 清空 input 以便可以重新选择同一文件
  e.target.value = "";
}

function removeImage(i) {
  files.value.splice(i, 1);
  previews.value.splice(i, 1);
}

function buildNote() {
  const parts = [];
  if (brandModel.value.trim()) parts.push(`品牌/型号：${brandModel.value.trim()}`);
  if (buyPrice.value) parts.push(`购入价格：约¥${buyPrice.value}`);
  if (buyTime.value.trim()) parts.push(`购入时间/成色：${buyTime.value.trim()}`);
  if (userNote.value.trim()) parts.push(`其他说明：${userNote.value.trim()}`);
  return parts.join("；");
}

async function startAnalysis() {
  if (!files.value.length) {
    noImageWarning.value = true;
    // 滚动到提示区域
    window.scrollTo({ top: 0, behavior: 'smooth' });
    return;
  }
  noImageWarning.value = false;
  errorMsg.value = "";
  analyzing.value = true;
  try {
    const result = await analyzeImages(files.value, buildNote());
    form.value = {
      title: result.title || "",
      category: result.category || "生活用品",
      condition: result.condition || "9成新",
      price_min: result.price_min || 0,
      price_max: result.price_max || 0,
      tags: result.tags || [],
      copy: result.copy || "",
      contact: "",
    };
    tagsInput.value = (result.tags || []).join(", ");
    currentStep.value = 1;
  } catch (e) {
    console.error("AI 分析失败", e);
    errorMsg.value = e.response?.data?.detail || "AI 分析失败，请重试";
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } finally {
    analyzing.value = false;
  }
}

async function publishProduct() {
  publishAttempted.value = true;
  
  // 校验：必须上传图片
  if (!files.value.length) {
    alert("请至少上传 1 张商品图片");
    return;
  }
  
  // 校验：必须填写联系方式
  if (!form.value.contact.trim()) {
    // 滚动到联系方式输入框
    const contactEl = document.querySelector('.input-field.border-red-400');
    if (contactEl) contactEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    return;
  }
  
  publishing.value = true;
  errorMsg.value = "";
  try {
    // 敏感词预检：标题/文案/补充说明/联系方式/标签
    const textToCheck = [form.value.title, form.value.copy, userNote.value, form.value.contact, ...computedTags.value]
      .filter(Boolean).join(" ");
    const check = await checkText(textToCheck);
    if (check.flagged) {
      errorMsg.value = `内容包含违规敏感词：${check.words.join("、")}，请修改后重新发布`;
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }

    // 先上传图片到后端（含违规图片审核拦截），获取真实 URL
    const imageUrls = [];
    for (const f of files.value) {
      const { url } = await uploadImage(f);
      imageUrls.push(url);
    }

    const res = await createProduct({
      title: form.value.title,
      category: form.value.category,
      condition: form.value.condition,
      ai_price_min: form.value.price_min,
      ai_price_max: form.value.price_max,
      ai_tags: computedTags.value,
      ai_copy: form.value.copy,
      images: imageUrls,
      user_note: userNote.value,
      contact: form.value.contact,
    });
    publishedId.value = res.id;
    currentStep.value = 2;
  } catch (e) {
    console.error("发布失败", e);
    errorMsg.value = e.response?.data?.detail || "发布失败，请检查网络后重试";
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } finally {
    publishing.value = false;
  }
}

function resetForm() {
  publishAttempted.value = false;
  noImageWarning.value = false;
  errorMsg.value = "";
  currentStep.value = 0;
  files.value = [];
  previews.value = [];
  userNote.value = "";
  tagsInput.value = "";
  form.value = {
    title: "",
    category: "生活用品",
    condition: "9成新",
    price_min: 0,
    price_max: 0,
    tags: [],
    copy: "",
    contact: "",
  };
}
</script>

