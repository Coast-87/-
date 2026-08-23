<template>
  <div class="welcome-root" ref="welcomeRef">
    <div class="bg-layer" aria-hidden="true">
      <div class="bg-base"></div>
      <div class="prism-beam prism-beam--1"></div>
      <div class="prism-beam prism-beam--2"></div>
      <div class="prism-beam prism-beam--3"></div>
      <div class="glass-orb glass-orb--1"></div>
      <div class="glass-orb glass-orb--2"></div>
      <div class="glass-orb glass-orb--3"></div>
      <div class="glass-orb glass-orb--4"></div>
      <svg class="dot-grid" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
        <defs>
          <pattern id="sky-dots" width="48" height="48" patternUnits="userSpaceOnUse">
            <circle cx="24" cy="24" r="0.8" fill="rgba(8,145,178,0.06)" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#sky-dots)" />
      </svg>
      <div class="particle particle--1"></div>
      <div class="particle particle--2"></div>
      <div class="particle particle--3"></div>
      <div class="particle particle--4"></div>
      <div class="particle particle--5"></div>
      <div class="particle particle--6"></div>
    </div>
    <div class="welcome-content">
      <div class="brand-section">
        <div class="brand-mark">
          <svg viewBox="0 0 56 56" fill="none">
            <rect x="4" y="10" width="48" height="36" rx="7" stroke="currentColor" stroke-width="1.2" />
            <path d="M4 24h48" stroke="currentColor" stroke-width="1.2" />
            <circle cx="20" cy="38" r="3.5" fill="currentColor" opacity="0.3" />
            <circle cx="34" cy="38" r="3.5" fill="currentColor" opacity="0.3" />
            <path d="M13 10V5a3 3 0 0 1 3-3h24a3 3 0 0 1 3 3v5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" />
            <path d="M21 2h14" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" />
          </svg>
        </div>
        <h1 class="brand-title">校园集市</h1>
        <p class="brand-subtitle">AI 智能发品平台</p>
        <div class="brand-rule"></div>
      </div>
      <div class="auth-card" ref="cardRef" :style="cardTransform">
        <div class="card-accent-bar"></div>
        <div class="card-gloss"></div>
        <div class="card-body">
          <nav class="tabs">
            <button
              v-for="t in tabs"
              :key="t.key"
              @click="switchTab(t.key)"
              class="tab"
              :class="{ active: activeTab === t.key }"
            >{{ t.label }}</button>
            <div class="tab-track" :class="'track-' + activeTab"></div>
          </nav>
          <form v-show="activeTab === 'login'" @submit.prevent="submit" class="form" autocomplete="off">
            <div class="field" :class="{ 'has-error': usernameError }">
              <label class="field-label">用户名</label>
              <div class="input-wrap">
                <svg class="input-icon" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="7" r="3.5" stroke="currentColor" stroke-width="1.5" /><path d="M4 17c0-3.3 2.7-6 6-6s6 2.7 6 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" /></svg>
                <input v-model="username" type="text" placeholder="输入用户名" class="input" autocomplete="username" @input="usernameError = ''" />
              </div>
              <p v-if="usernameError" class="field-error">{{ usernameError }}</p>
            </div>
            <div class="field" :class="{ 'has-error': passwordError }">
              <label class="field-label">密码</label>
              <div class="input-wrap">
                <svg class="input-icon" viewBox="0 0 20 20" fill="none"><rect x="3" y="7" width="14" height="10" rx="2" stroke="currentColor" stroke-width="1.5" /><circle cx="10" cy="12" r="1.5" fill="currentColor" opacity="0.4" /></svg>
                <input v-model="password" :type="showPwd ? 'text' : 'password'" placeholder="输入密码" class="input" autocomplete="current-password" @input="passwordError = ''" />
                <button type="button" class="toggle-pwd" @click="showPwd = !showPwd" :aria-label="showPwd ? '隐藏密码' : '显示密码'">
                  <svg v-if="!showPwd" class="toggle-icon" viewBox="0 0 20 20" fill="none"><path d="M10 4C4 4 1 10 1 10s3 6 9 6 9-6 9-6-3-6-9-6z" stroke="currentColor" stroke-width="1.5" /><circle cx="10" cy="10" r="3" stroke="currentColor" stroke-width="1.5" /></svg>
                  <svg v-else class="toggle-icon" viewBox="0 0 20 20" fill="none"><path d="M10 4C4 4 1 10 1 10s3 6 9 6 9-6 9-6-3-6-9-6z" stroke="currentColor" stroke-width="1.5" /><path d="M3 3l14 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" /></svg>
                </button>
              </div>
              <p v-if="passwordError" class="field-error">{{ passwordError }}</p>
            </div>
            <p v-if="loginError" class="msg msg--err">{{ loginError }}</p>
            <button type="submit" class="btn" :disabled="loading">
              <span v-if="loading" class="btn-spinner"></span>
              <span v-else>登 录</span>
            </button>
          </form>
          <form v-show="activeTab === 'register'" @submit.prevent="submit" class="form" autocomplete="off">
            <div class="field" :class="{ 'has-error': usernameError }">
              <label class="field-label">用户名</label>
              <div class="input-wrap">
                <svg class="input-icon" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="7" r="3.5" stroke="currentColor" stroke-width="1.5" /><path d="M4 17c0-3.3 2.7-6 6-6s6 2.7 6 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" /></svg>
                <input v-model="username" type="text" placeholder="输入用户名" class="input" autocomplete="username" @input="usernameError = ''" />
              </div>
              <p v-if="usernameError" class="field-error">{{ usernameError }}</p>
            </div>
            <div class="field" :class="{ 'has-error': phoneError }">
              <label class="field-label">手机号</label>
              <div class="input-wrap">
                <svg class="input-icon" viewBox="0 0 20 20" fill="none"><rect x="5" y="2" width="10" height="16" rx="2" stroke="currentColor" stroke-width="1.5" /><circle cx="10" cy="14" r="1" fill="currentColor" opacity="0.4" /></svg>
                <input v-model="phone" type="tel" placeholder="输入手机号" class="input" autocomplete="tel" maxlength="11" @input="onPhoneInput" />
              </div>
              <p v-if="phoneError" class="field-error">{{ phoneError }}</p>
            </div>
            <div class="field" :class="{ 'has-error': passwordError }">
              <label class="field-label">密码</label>
              <div class="input-wrap">
                <svg class="input-icon" viewBox="0 0 20 20" fill="none"><rect x="3" y="7" width="14" height="10" rx="2" stroke="currentColor" stroke-width="1.5" /><circle cx="10" cy="12" r="1.5" fill="currentColor" opacity="0.4" /></svg>
                <input v-model="password" :type="showPwd ? 'text' : 'password'" placeholder="至少8位，含两种字符类型" class="input" autocomplete="new-password" @input="passwordError = ''" />
                <button type="button" class="toggle-pwd" @click="showPwd = !showPwd" :aria-label="showPwd ? '隐藏密码' : '显示密码'">
                  <svg v-if="!showPwd" class="toggle-icon" viewBox="0 0 20 20" fill="none"><path d="M10 4C4 4 1 10 1 10s3 6 9 6 9-6 9-6-3-6-9-6z" stroke="currentColor" stroke-width="1.5" /><circle cx="10" cy="10" r="3" stroke="currentColor" stroke-width="1.5" /></svg>
                  <svg v-else class="toggle-icon" viewBox="0 0 20 20" fill="none"><path d="M10 4C4 4 1 10 1 10s3 6 9 6 9-6 9-6-3-6-9-6z" stroke="currentColor" stroke-width="1.5" /><path d="M3 3l14 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" /></svg>
                </button>
              </div>
              <p v-if="passwordError" class="field-error">{{ passwordError }}</p>
            </div>
            <p v-if="formMsg" class="msg" :class="'msg--' + formMsgType">{{ formMsg }}</p>
            <button type="submit" class="btn" :disabled="loading">
              <span v-if="loading" class="btn-spinner"></span>
              <span v-else>注 册</span>
            </button>
          </form>
          <form v-show="activeTab === 'forgot'" @submit.prevent="submit" class="form" autocomplete="off">
            <div class="field" :class="{ 'has-error': phoneError }">
              <label class="field-label">手机号</label>
              <div class="input-wrap">
                <svg class="input-icon" viewBox="0 0 20 20" fill="none"><rect x="5" y="2" width="10" height="16" rx="2" stroke="currentColor" stroke-width="1.5" /><circle cx="10" cy="14" r="1" fill="currentColor" opacity="0.4" /></svg>
                <input v-model="phone" type="tel" placeholder="输入注册手机号" class="input" autocomplete="tel" maxlength="11" @input="onPhoneInput" />
              </div>
              <p v-if="phoneError" class="field-error">{{ phoneError }}</p>
            </div>
            <div class="field" :class="{ 'has-error': passwordError }">
              <label class="field-label">新密码</label>
              <div class="input-wrap">
                <svg class="input-icon" viewBox="0 0 20 20" fill="none"><rect x="3" y="7" width="14" height="10" rx="2" stroke="currentColor" stroke-width="1.5" /><circle cx="10" cy="12" r="1.5" fill="currentColor" opacity="0.4" /></svg>
                <input v-model="password" :type="showPwd ? 'text' : 'password'" placeholder="至少8位，含两种字符类型" class="input" autocomplete="new-password" @input="passwordError = ''" />
                <button type="button" class="toggle-pwd" @click="showPwd = !showPwd" :aria-label="showPwd ? '隐藏密码' : '显示密码'">
                  <svg v-if="!showPwd" class="toggle-icon" viewBox="0 0 20 20" fill="none"><path d="M10 4C4 4 1 10 1 10s3 6 9 6 9-6 9-6-3-6-9-6z" stroke="currentColor" stroke-width="1.5" /><circle cx="10" cy="10" r="3" stroke="currentColor" stroke-width="1.5" /></svg>
                  <svg v-else class="toggle-icon" viewBox="0 0 20 20" fill="none"><path d="M10 4C4 4 1 10 1 10s3 6 9 6 9-6 9-6-3-6-9-6z" stroke="currentColor" stroke-width="1.5" /><path d="M3 3l14 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" /></svg>
                </button>
              </div>
              <p v-if="passwordError" class="field-error">{{ passwordError }}</p>
            </div>
            <p v-if="formMsg" class="msg" :class="'msg--' + formMsgType">{{ formMsg }}</p>
            <button type="submit" class="btn" :disabled="loading">
              <span v-if="loading" class="btn-spinner"></span>
              <span v-else>重 置 密 码</span>
            </button>
          </form>
        </div>
        <div class="card-footer">
          <p>校园集市 · 让每一件物品找到新主人</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";
import { userStore } from "../stores/user";
import api from "../api";

const router = useRouter();

// ============================================================
// Tab
// ============================================================
const tabs = [
  { key: "login", label: "登录" },
  { key: "register", label: "注册" },
  { key: "forgot", label: "找回密码" },
];
const activeTab = ref("login");
const loading = ref(false);
const showPwd = ref(false);

function switchTab(key) {
  activeTab.value = key;
  loginError.value = "";
  formMsg.value = "";
  usernameError.value = "";
  phoneError.value = "";
  passwordError.value = "";
}

// ============================================================
// 表单字段
// ============================================================
const username = ref("");
const password = ref("");
const phone = ref("");
const loginError = ref("");
const formMsg = ref("");
const formMsgType = ref("err");
const usernameError = ref("");
const phoneError = ref("");
const passwordError = ref("");

// ============================================================
// 校验
// ============================================================
function validateUsername() {
  const v = username.value.trim();
  if (!v) { usernameError.value = "请输入用户名"; return false; }
  if (v.length < 2 || v.length > 20) { usernameError.value = "2-20个字符"; return false; }
  if (!/^[一-龥a-zA-Z0-9]+$/.test(v)) { usernameError.value = "仅支持中文、英文、数字"; return false; }
  usernameError.value = "";
  return true;
}


function onPhoneInput(e) {
  const raw = e.target.value;
  const cleaned = raw.replace(/\D/g, '');
  if (raw !== cleaned) {
    phone.value = cleaned;
  }
  phoneError.value = '';
}

function cleanPhone(v) {
  return (v || '').replace(/\D/g, '');
}

function validatePhone() {
  const v = phone.value.trim();
  if (!v) { phoneError.value = "请输入手机号"; return false; }
  if (!/^\d{11}$/.test(v) || v[0] !== "1") { phoneError.value = "请输入正确的11位手机号"; return false; }
  phoneError.value = "";
  return true;
}

function validatePassword() {
  const v = password.value;
  if (!v) { passwordError.value = "请输入密码"; return false; }
  if (v.length < 8) { passwordError.value = "至少8位"; return false; }
  let types = 0;
  if (/[a-z]/.test(v)) types++;
  if (/[A-Z]/.test(v)) types++;
  if (/[0-9]/.test(v)) types++;
  if (/[^a-zA-Z0-9]/.test(v)) types++;
  if (types < 2) { passwordError.value = "需包含至少两种字符类型"; return false; }
  passwordError.value = "";
  return true;
}

// ============================================================
// 提交
// ============================================================
async function submit() {
  loginError.value = "";
  formMsg.value = "";

  if (activeTab.value === "login") {
    if (!username.value.trim()) { loginError.value = "请输入用户名"; return; }
    if (!password.value) { loginError.value = "请输入密码"; return; }
    loading.value = true;
    try {
      const res = await api.post("/auth/login", {
        username: username.value.trim(),
        password: password.value,
      });
      const data = res.data;
      userStore.setAuth(data.token || data.access_token, data.user);
      router.push("/market");
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.response?.data?.message || "登录失败，请重试";
      loginError.value = msg;
    } finally {
      loading.value = false;
    }
    return;
  }

  if (activeTab.value === "register") {
    if (!validateUsername()) return;
    if (!validatePhone()) return;
    if (!validatePassword()) return;
    loading.value = true;
    try {
      const res = await api.post("/auth/register", {
        username: username.value.trim(),
        phone: cleanPhone(phone.value),
        password: password.value,
      });
      formMsg.value = res.data?.message || "注册成功，请登录";
      formMsgType.value = "ok";
      setTimeout(() => { activeTab.value = "login"; formMsg.value = ""; }, 1500);
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.response?.data?.message || "注册失败";
      formMsg.value = msg;
      formMsgType.value = "err";
    } finally {
      loading.value = false;
    }
    return;
  }

  if (activeTab.value === "forgot") {
    if (!validatePhone()) return;
    if (!validatePassword()) return;
    loading.value = true;
    try {
      const res = await api.post("/auth/reset-password", {
        phone: cleanPhone(phone.value),
        new_password: password.value,
      });
      formMsg.value = res.data?.message || "密码重置成功，请登录";
      formMsgType.value = "ok";
      setTimeout(() => { activeTab.value = "login"; formMsg.value = ""; }, 1500);
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.response?.data?.message || "重置失败";
      formMsg.value = msg;
      formMsgType.value = "err";
    } finally {
      loading.value = false;
    }
    return;
  }
}

// ============================================================
// 视差倾斜
// ============================================================
const cardRef = ref(null);
const welcomeRef = ref(null);
const cardTransform = ref({});

function onMouseMove(e) {
  if (!cardRef.value || !welcomeRef.value) return;
  const welcome = welcomeRef.value.getBoundingClientRect();
  const cx = welcome.width / 2;
  const cy = welcome.height / 2;
  const dx = (e.clientX - cx) / cx;
  const dy = (e.clientY - cy) / cy;
  const maxTilt = 1.8;

  cardTransform.value = {
    transform: `perspective(1200px) rotateY(${dx * maxTilt}deg) rotateX(${-dy * maxTilt}deg) translateZ(0)`,
    transition: "transform 0.25s cubic-bezier(0.23, 1, 0.32, 1)",
  };
}

function onMouseLeave() {
  cardTransform.value = {
    transform: "perspective(1200px) rotateY(0deg) rotateX(0deg) translateZ(0)",
    transition: "transform 0.8s cubic-bezier(0.23, 1, 0.32, 1)",
  };
}

onMounted(() => {
  window.addEventListener("mousemove", onMouseMove, { passive: true });
  document.addEventListener("mouseleave", onMouseLeave);
});

onBeforeUnmount(() => {
  window.removeEventListener("mousemove", onMouseMove);
  document.removeEventListener("mouseleave", onMouseLeave);
});
</script>

<style>
/* ============================================================
   Design Tokens — 琉璃晴空 (Crystal Sky)
   明亮、通透、高级 — 晴空下的棱镜光束 × 玻璃质感
   ============================================================ */
.welcome-root {
  --bg-start: #F0F5FA;
  --bg-end: #F8F6F3;
  --bg-card: rgba(255, 255, 255, 0.85);
  --bg-card-solid: #FFFFFF;
  --bg-input: #F7F9FB;
  --bg-input-focus: #F0F4F8;
  --text-primary: #0F172A;
  --text-secondary: #475569;
  --text-muted: #94A3B8;
  --accent: #0891B2;
  --accent-hover: #0E7490;
  --accent-teal: #0D9488;
  --accent-soft: rgba(8, 145, 178, 0.06);
  --accent-glow: rgba(8, 145, 178, 0.12);
  --warm-amber: rgba(245, 158, 11, 0.08);
  --border: #E2E8F0;
  --border-input: #E2E8F0;
  --border-focus: #0891B2;
  --danger: #EF4444;
  --danger-soft: rgba(239, 68, 68, 0.06);
  --success: #10B981;
  --success-soft: rgba(16, 185, 129, 0.06);
  --shadow-card: 0 1px 0 rgba(0,0,0,0.04), 0 16px 48px rgba(8,145,178,0.08), 0 4px 16px rgba(0,0,0,0.03);
  --shadow-card-hover: 0 1px 0 rgba(0,0,0,0.04), 0 24px 64px rgba(8,145,178,0.12), 0 6px 20px rgba(0,0,0,0.04);
  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 20px;
  --radius-btn: 10px;
  --font-display: 'Playfair Display', 'Noto Serif SC', 'SimSun', serif;
  --font-body: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  --ease-out-expo: cubic-bezier(0.19, 1, 0.22, 1);
  --transition-fast: 200ms var(--ease-out-expo);
  --transition-slow: 600ms var(--ease-out-expo);

  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-body);
  background: linear-gradient(160deg, var(--bg-start) 0%, #E8F0F8 40%, var(--bg-end) 100%);
  overflow: hidden;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ============================================================
   背景层
   ============================================================ */
.bg-layer { position: absolute; inset: 0; z-index: 0; pointer-events: none; }

.bg-base {
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse 80% 50% at 20% 20%, rgba(8, 145, 178, 0.04) 0%, transparent 60%),
    radial-gradient(ellipse 60% 60% at 75% 70%, rgba(13, 148, 136, 0.03) 0%, transparent 50%),
    radial-gradient(ellipse 50% 40% at 50% 50%, rgba(245, 158, 11, 0.02) 0%, transparent 50%);
}

/* 棱镜光束 */
.prism-beam {
  position: absolute;
  top: -20%; bottom: -20%;
  width: 200px;
  opacity: 0.06;
  transform-origin: center center;
  will-change: transform;
}
.prism-beam--1 {
  left: 15%;
  background: linear-gradient(180deg, transparent 0%, rgba(8, 145, 178, 0.5) 30%, rgba(13, 148, 136, 0.4) 60%, transparent 100%);
  transform: rotate(-12deg);
  animation: beam-drift-1 18s ease-in-out infinite;
}
.prism-beam--2 {
  left: 45%;
  width: 140px;
  background: linear-gradient(180deg, transparent 0%, rgba(8, 145, 178, 0.35) 25%, rgba(245, 158, 11, 0.2) 55%, transparent 100%);
  transform: rotate(-8deg);
  animation: beam-drift-2 22s ease-in-out infinite;
}
.prism-beam--3 {
  left: 70%;
  width: 180px;
  background: linear-gradient(180deg, transparent 0%, rgba(13, 148, 136, 0.4) 35%, rgba(8, 145, 178, 0.3) 65%, transparent 100%);
  transform: rotate(-5deg);
  animation: beam-drift-3 20s ease-in-out infinite;
}

@keyframes beam-drift-1 {
  0%, 100% { transform: rotate(-12deg) translateX(0); opacity: 0.06; }
  50% { transform: rotate(-12deg) translateX(30px); opacity: 0.08; }
}
@keyframes beam-drift-2 {
  0%, 100% { transform: rotate(-8deg) translateX(0); opacity: 0.05; }
  50% { transform: rotate(-8deg) translateX(-20px); opacity: 0.07; }
}
@keyframes beam-drift-3 {
  0%, 100% { transform: rotate(-5deg) translateX(0); opacity: 0.05; }
  50% { transform: rotate(-5deg) translateX(25px); opacity: 0.07; }
}

/* 玻璃浮球 */
.glass-orb {
  position: absolute; border-radius: 50%;
  backdrop-filter: blur(40px);
  -webkit-backdrop-filter: blur(40px);
  will-change: transform;
}
.glass-orb--1 {
  width: 280px; height: 280px;
  background: radial-gradient(circle at 35% 35%, rgba(255,255,255,0.5), rgba(8,145,178,0.08) 60%, transparent 80%);
  border: 1px solid rgba(255,255,255,0.4);
  top: -8%; left: 8%;
  animation: orb-float-1 26s ease-in-out infinite;
}
.glass-orb--2 {
  width: 200px; height: 200px;
  background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.45), rgba(13,148,136,0.06) 60%, transparent 80%);
  border: 1px solid rgba(255,255,255,0.35);
  top: 60%; right: -5%;
  animation: orb-float-2 30s ease-in-out infinite;
}
.glass-orb--3 {
  width: 160px; height: 160px;
  background: radial-gradient(circle at 40% 30%, rgba(255,255,255,0.4), rgba(245,158,11,0.05) 60%, transparent 80%);
  border: 1px solid rgba(255,255,255,0.3);
  top: 15%; right: 15%;
  animation: orb-float-3 22s ease-in-out infinite;
}
.glass-orb--4 {
  width: 120px; height: 120px;
  background: radial-gradient(circle at 35% 35%, rgba(255,255,255,0.5), rgba(8,145,178,0.06) 60%, transparent 80%);
  border: 1px solid rgba(255,255,255,0.35);
  bottom: 10%; left: 20%;
  animation: orb-float-4 24s ease-in-out infinite;
}

@keyframes orb-float-1 {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(30px, -20px) rotate(3deg); }
  50% { transform: translate(-10px, -40px) rotate(-2deg); }
  75% { transform: translate(-30px, -10px) rotate(1deg); }
}
@keyframes orb-float-2 {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  33% { transform: translate(-25px, -15px) rotate(-3deg); }
  66% { transform: translate(15px, 20px) rotate(2deg); }
}
@keyframes orb-float-3 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(-20px, -25px) scale(1.05); }
}
@keyframes orb-float-4 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(20px, -15px) scale(1.08); }
}

/* 点阵网格 */
.dot-grid { position: absolute; inset: 0; width: 100%; height: 100%; }

/* 浮动粒子 */
.particle {
  position: absolute; border-radius: 50%;
  background: rgba(8, 145, 178, 0.12);
  will-change: transform;
}
.particle--1 { width: 6px; height: 6px; top: 20%; left: 25%; animation: particle-float 14s ease-in-out infinite; }
.particle--2 { width: 4px; height: 4px; top: 35%; left: 60%; animation: particle-float 16s ease-in-out 2s infinite; }
.particle--3 { width: 5px; height: 5px; top: 65%; left: 35%; animation: particle-float 18s ease-in-out 4s infinite; }
.particle--4 { width: 3px; height: 3px; top: 75%; left: 70%; animation: particle-float 15s ease-in-out 1s infinite; }
.particle--5 { width: 4px; height: 4px; top: 10%; left: 80%; animation: particle-float 17s ease-in-out 3s infinite; }
.particle--6 { width: 3px; height: 3px; top: 50%; left: 12%; animation: particle-float 20s ease-in-out 5s infinite; }

@keyframes particle-float {
  0%, 100% { transform: translate(0, 0); opacity: 0.4; }
  25% { transform: translate(15px, -20px); opacity: 0.7; }
  50% { transform: translate(-10px, -35px); opacity: 0.3; }
  75% { transform: translate(-20px, -10px); opacity: 0.6; }
}

/* ============================================================
   内容层
   ============================================================ */
.welcome-content {
  position: relative; z-index: 1;
  display: flex; flex-direction: column;
  align-items: center; gap: 40px;
  animation: content-fade-in 0.8s var(--ease-out-expo);
}

@keyframes content-fade-in {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ============================================================
   品牌区
   ============================================================ */
.brand-section {
  display: flex; flex-direction: column;
  align-items: center; text-align: center;
}

.brand-mark {
  width: 52px; height: 52px;
  display: flex; align-items: center; justify-content: center;
  color: var(--accent);
  margin-bottom: 14px;
  opacity: 0.85;
}
.brand-mark svg { width: 100%; height: 100%; }

.brand-title {
  font-family: var(--font-display);
  font-size: 42px; font-weight: 600;
  letter-spacing: 0.08em; line-height: 1.1;
  color: var(--text-primary);
  margin: 0;
}

.brand-subtitle {
  font-family: var(--font-body);
  font-size: 13px; font-weight: 500;
  letter-spacing: 0.2em; text-transform: uppercase;
  color: var(--text-muted);
  margin: 8px 0 0;
}

.brand-rule {
  width: 48px; height: 2px;
  background: linear-gradient(90deg, var(--accent), var(--accent-teal));
  border-radius: 1px;
  margin-top: 18px;
  opacity: 0.6;
}

/* ============================================================
   登录卡片
   ============================================================ */
.auth-card {
  position: relative;
  width: 100%; max-width: 440px;
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(255,255,255,0.6);
  box-shadow: var(--shadow-card);
  overflow: hidden;
  will-change: transform;
}

/* 三色渐变顶部条 */
.card-accent-bar {
  height: 3px;
  background: linear-gradient(90deg, var(--accent) 0%, var(--accent-teal) 50%, #F59E0B 100%);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

/* 光泽覆盖层 */
.card-gloss {
  position: absolute; inset: 0; pointer-events: none; z-index: 2;
  border-radius: inherit;
  background:
    radial-gradient(ellipse 100% 40% at 50% 0%, rgba(255,255,255,0.35) 0%, transparent 60%),
    radial-gradient(ellipse 100% 30% at 50% 100%, rgba(255,255,255,0.1) 0%, transparent 50%);
}

.card-body {
  position: relative; z-index: 1;
  padding: 0;
}

/* ============================================================
   Tab 切换
   ============================================================ */
.tabs {
  position: relative;
  display: flex; align-items: stretch;
  padding: 28px 32px 0;
  gap: 0;
}
.tab {
  flex: 1;
  padding: 14px 0;
  background: none; border: none;
  font-family: var(--font-body); font-size: 14px; font-weight: 500;
  letter-spacing: 0.04em; color: var(--text-muted);
  cursor: pointer; text-align: center;
  transition: color var(--transition-fast);
  position: relative; z-index: 1;
  -webkit-tap-highlight-color: transparent;
}
.tab:hover { color: var(--text-secondary); }
.tab.active { color: var(--accent); font-weight: 600; }

.tab-track {
  position: absolute; bottom: 0; height: 2px;
  border-radius: 1px;
  background: linear-gradient(90deg, var(--accent), var(--accent-teal));
  transition: left 0.3s var(--ease-out-expo), width 0.3s var(--ease-out-expo);
}
.track-login { left: 32px; width: calc((100% - 64px) / 3); }
.track-register { left: calc(32px + (100% - 64px) / 3); width: calc((100% - 64px) / 3); }
.track-forgot { left: calc(32px + 2 * (100% - 64px) / 3); width: calc((100% - 64px) / 3); }

/* ============================================================
   表单
   ============================================================ */
.form {
  display: flex; flex-direction: column;
  padding: 28px 32px 32px;
  gap: 18px;
}

.field { display: flex; flex-direction: column; gap: 6px; }

.field-label {
  font-size: 12px; font-weight: 600;
  letter-spacing: 0.06em; text-transform: uppercase;
  color: var(--text-secondary);
  padding-left: 2px;
}

.input-wrap {
  display: flex; align-items: center;
  height: 50px;
  background: var(--bg-input);
  border: 1.5px solid var(--border-input);
  border-radius: var(--radius-sm);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast), background var(--transition-fast);
  overflow: hidden;
}
.input-wrap:focus-within {
  border-color: var(--border-focus);
  background: var(--bg-input-focus);
  box-shadow: 0 0 0 3px rgba(8, 145, 178, 0.08);
}
.has-error .input-wrap {
  border-color: var(--danger);
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.06);
}

.input-icon {
  width: 18px; height: 18px;
  margin-left: 14px;
  flex-shrink: 0;
  color: var(--text-muted);
  transition: color var(--transition-fast);
}
.input-wrap:focus-within .input-icon { color: var(--accent); }
.has-error .input-wrap .input-icon { color: var(--danger); }

.input {
  flex: 1; height: 100%;
  padding: 0 14px;
  background: transparent; border: none; outline: none;
  font-family: var(--font-body); font-size: 14px; font-weight: 400;
  color: var(--text-primary);
  letter-spacing: 0.02em;
}
.input::placeholder { color: var(--text-muted); opacity: 0.6; }
.input:-webkit-autofill,
.input:-webkit-autofill:hover,
.input:-webkit-autofill:focus {
  -webkit-text-fill-color: var(--text-primary);
  -webkit-box-shadow: 0 0 0 30px var(--bg-input) inset !important;
  caret-color: var(--text-primary);
}

/* 密码切换 */
.toggle-pwd {
  display: flex; align-items: center; justify-content: center;
  width: 44px; height: 44px; margin-right: 6px;
  background: none; border: none; cursor: pointer;
  color: var(--text-muted); border-radius: var(--radius-sm);
  transition: color var(--transition-fast), background var(--transition-fast);
  flex-shrink: 0;
}
.toggle-pwd:hover { color: var(--text-secondary); background: rgba(0,0,0,0.03); }
.toggle-icon { width: 18px; height: 18px; }

.field-error {
  font-size: 12px; color: var(--danger);
  margin: 0; padding-left: 2px; letter-spacing: 0.02em;
}

.msg {
  padding: 12px 16px; border-radius: var(--radius-sm);
  font-size: 13px; line-height: 1.5; margin: 0;
}
.msg--err { background: var(--danger-soft); border: 1px solid rgba(239,68,68,0.12); color: var(--danger); }
.msg--ok { background: var(--success-soft); border: 1px solid rgba(16,185,129,0.12); color: var(--success); }

/* ============================================================
   主按钮
   ============================================================ */
.btn {
  width: 100%; height: 54px;
  display: flex; align-items: center; justify-content: center;
  margin-top: 4px;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-teal) 100%);
  border: none; border-radius: var(--radius-btn);
  font-family: var(--font-body); font-size: 15px; font-weight: 600;
  letter-spacing: 0.3em; color: #FFFFFF;
  cursor: pointer; position: relative; overflow: hidden;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast), filter var(--transition-fast);
}
.btn::after {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(255,255,255,0.15) 0%, transparent 50%);
  pointer-events: none;
}
.btn:hover {
  transform: translateY(-1px);
  filter: brightness(1.05);
  box-shadow: 0 8px 28px rgba(8, 145, 178, 0.3), 0 2px 8px rgba(8, 145, 178, 0.15);
}
.btn:active { transform: translateY(0); filter: brightness(0.95); box-shadow: 0 2px 8px rgba(8, 145, 178, 0.2); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; filter: none; box-shadow: none; }

.btn-spinner {
  width: 22px; height: 22px;
  border: 2px solid rgba(255,255,255,0.25);
  border-top-color: #FFFFFF; border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ============================================================
   卡片底部
   ============================================================ */
.card-footer { padding: 0 32px 28px; text-align: center; }
.card-footer p {
  font-size: 12px; font-weight: 400; letter-spacing: 0.04em;
  color: var(--text-muted); margin: 0;
}

/* ============================================================
   A11Y
   ============================================================ */
@media (prefers-reduced-motion: reduce) {
  .prism-beam, .glass-orb, .particle { animation: none; }
  .welcome-content { animation: none; }
  .tab-track { transition: none; }
  .btn { transition: none; }
}

/* ============================================================
   响应式 ≤ 640px
   ============================================================ */
@media (max-width: 640px) {
  .welcome-content { padding: 20px; gap: 30px; }
  .brand-title { font-size: 34px; }
  .brand-subtitle { font-size: 11px; }
  .auth-card { max-width: 100%; border-radius: var(--radius-md); }
  .card-accent-bar { border-radius: var(--radius-md) var(--radius-md) 0 0; }
  .tabs { padding: 24px 24px 0; }
  .tab { font-size: 13px; padding: 12px 0; }
  .track-login { left: 24px; width: calc((100% - 48px) / 3); }
  .track-register { left: calc(24px + (100% - 48px) / 3); width: calc((100% - 48px) / 3); }
  .track-forgot { left: calc(24px + 2 * (100% - 48px) / 3); width: calc((100% - 48px) / 3); }
  .form { padding: 24px 24px 28px; gap: 16px; }
  .input-wrap { height: 48px; }
  .btn { height: 48px; }
  .card-footer { padding: 0 24px 24px; }
}

/* ============================================================
   响应式 ≤ 400px
   ============================================================ */
@media (max-width: 400px) {
  .welcome-content { padding: 16px; gap: 24px; }
  .brand-mark { width: 42px; height: 42px; margin-bottom: 10px; }
  .brand-title { font-size: 28px; }
  .brand-subtitle { font-size: 10px; letter-spacing: 0.18em; }
  .brand-rule { margin-top: 14px; }
  .tabs { padding: 20px 20px 0; }
  .tab { font-size: 12px; padding: 10px 0; }
  .track-login { left: 20px; width: calc((100% - 40px) / 3); }
  .track-register { left: calc(20px + (100% - 40px) / 3); width: calc((100% - 40px) / 3); }
  .track-forgot { left: calc(20px + 2 * (100% - 40px) / 3); width: calc((100% - 40px) / 3); }
  .form { padding: 20px 20px 24px; gap: 14px; }
  .input-wrap { height: 44px; }
  .input { font-size: 14px; padding: 0 10px; }
  .input-icon { width: 16px; height: 16px; margin-left: 12px; }
  .btn { height: 44px; font-size: 14px; letter-spacing: 0.25em; }
  .card-footer { padding: 0 20px 20px; }
  .card-footer p { font-size: 11px; }
}
</style>