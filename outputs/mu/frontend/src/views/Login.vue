<template>
  <div class="max-w-md mx-auto px-4 py-16">
    <div class="card p-8">
      <div class="text-center mb-6">
        <div class="text-5xl mb-3">{{ isForgot ? '🔑' : '🏪' }}</div>
        <h2 class="text-xl font-bold text-gray-800">
          {{ isForgot ? '找回密码' : (isRegister ? '注册账号' : '登录') }}
        </h2>
        <p class="text-gray-400 text-sm mt-1">校园跳蚤市场 · AI 智能发品</p>
      </div>

      <!-- ========== 登录 / 注册 / 找回密码 表单 ========== -->
      <div class="space-y-4">
        <!-- 用户名 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
          <input
            v-model="username"
            class="input-field"
            :class="{ 'border-red-400 ring-2 ring-red-200': usernameError }"
            :placeholder="isRegister ? '中文/英文/数字，2-20位，全平台唯一' : '请输入用户名'"
            @input="usernameError = ''"
            @keyup.enter="submit"
          />
          <p v-if="usernameError" class="text-red-500 text-xs mt-1">{{ usernameError }}</p>
        </div>

        <!-- 手机号（注册 / 找回密码时显示） -->
        <div v-if="isRegister || isForgot">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            手机号 <span class="text-red-500">*</span>
            <span class="text-gray-400 font-normal text-xs ml-1">{{ isForgot ? '用于验证身份' : '用于找回密码' }}</span>
          </label>
          <input
            v-model="phone"
            class="input-field"
            :class="{ 'border-red-400 ring-2 ring-red-200': phoneError }"
            placeholder="请输入11位手机号"
            maxlength="11"
            @input="phoneError = ''"
            @keyup.enter="submit"
          />
          <p v-if="phoneError" class="text-red-500 text-xs mt-1">{{ phoneError }}</p>
        </div>

        <!-- 密码（登录 / 注册时显示；找回密码时显示新密码） -->
        <div v-if="!isForgot">
          <label class="block text-sm font-medium text-gray-700 mb-1">密码</label>
          <input
            v-model="password"
            type="password"
            class="input-field"
            :class="{ 'border-red-400 ring-2 ring-red-200': passwordError }"
            :placeholder="isRegister ? '至少8位，需包含字母+数字（或字母+符号、数字+符号）' : '请输入密码'"
            @input="passwordError = ''"
            @keyup.enter="submit"
          />
          <p v-if="passwordError" class="text-red-500 text-xs mt-1">{{ passwordError }}</p>
        </div>

        <!-- 找回密码：新密码 -->
        <div v-if="isForgot">
          <label class="block text-sm font-medium text-gray-700 mb-1">设置新密码</label>
          <input
            v-model="newPassword"
            type="password"
            class="input-field"
            :class="{ 'border-red-400 ring-2 ring-red-200': newPasswordError }"
            placeholder="至少8位，需包含字母+数字（或字母+符号、数字+符号）"
            @input="newPasswordError = ''"
            @keyup.enter="submit"
          />
          <p v-if="newPasswordError" class="text-red-500 text-xs mt-1">{{ newPasswordError }}</p>
        </div>

        <!-- 服务端错误 -->
        <div v-if="error" class="text-red-500 text-sm bg-red-50 rounded-lg px-3 py-2">{{ error }}</div>
        <!-- 成功提示 -->
        <div v-if="success" class="text-green-600 text-sm bg-green-50 rounded-lg px-3 py-2">{{ success }}</div>

        <button @click="submit" :disabled="loading" class="btn-primary w-full text-lg">
          {{ loading ? '处理中...' : (isForgot ? '重置密码' : (isRegister ? '注册' : '登录')) }}
        </button>
      </div>

      <div class="text-center mt-4 flex flex-col gap-2">
        <button v-if="!isForgot" @click="toggleMode" class="text-sm text-primary-600 hover:underline">
          {{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}
        </button>
        <button v-if="!isRegister && !isForgot" @click="enterForgot" class="text-sm text-gray-400 hover:underline">
          忘记密码？
        </button>
        <button v-if="isForgot" @click="isForgot = false; clearErrors()" class="text-sm text-primary-600 hover:underline">
          ← 返回登录
        </button>
      </div>

      <div class="mt-6 pt-4 border-t border-gray-100 text-center">
        <p class="text-xs text-gray-400">管理员测试账号：admin / admin123</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { login, register, resetPassword } from "../api";
import { userStore } from "../stores/user";

const router = useRouter();
const isRegister = ref(false);
const isForgot = ref(false);
const username = ref("");
const password = ref("");
const phone = ref("");
const newPassword = ref("");
const loading = ref(false);
const error = ref("");
const success = ref("");
const usernameError = ref("");
const passwordError = ref("");
const phoneError = ref("");
const newPasswordError = ref("");

function clearErrors() {
  error.value = "";
  success.value = "";
  usernameError.value = "";
  passwordError.value = "";
  phoneError.value = "";
  newPasswordError.value = "";
}

function toggleMode() {
  isRegister.value = !isRegister.value;
  isForgot.value = false;
  clearErrors();
}

function enterForgot() {
  isForgot.value = true;
  isRegister.value = false;
  clearErrors();
}

function validateUsername(v) {
  if (!v.trim()) return "请输入用户名";
  if (v.trim().length < 2) return "用户名至少 2 位";
  if (v.trim().length > 20) return "用户名最多 20 位";
  if (!/^[\u4e00-\u9fa5a-zA-Z0-9]+$/.test(v.trim())) return "用户名只能包含中文、英文、数字";
  return "";
}

function validatePassword(v) {
  if (v.length < 8) return "密码至少 8 位";
  const hasLetter = /[a-zA-Z]/.test(v);
  const hasDigit = /\d/.test(v);
  const hasSpecial = /[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;\/]/.test(v);
  const types = [hasLetter, hasDigit, hasSpecial].filter(Boolean).length;
  if (types < 2) return "密码需包含字母、数字、符号中的至少两种";
  return "";
}

function validatePhone(v) {
  if (!v.trim()) return "请输入手机号";
  if (!/^1[3-9]\d{9}$/.test(v.trim())) return "请输入正确的11位中国大陆手机号";
  return "";
}

async function submit() {
  error.value = "";
  success.value = "";

  // ========== 找回密码 ==========
  if (isForgot.value) {
    usernameError.value = validateUsername(username.value);
    phoneError.value = validatePhone(phone.value);
    newPasswordError.value = validatePassword(newPassword.value);
    if (usernameError.value || phoneError.value || newPasswordError.value) return;

    loading.value = true;
    try {
      const res = await resetPassword(username.value.trim(), phone.value.trim(), newPassword.value);
      success.value = res.message || "密码重置成功";
      // 3 秒后跳回登录
      setTimeout(() => {
        isForgot.value = false;
        success.value = "";
        password.value = "";
        newPassword.value = "";
      }, 2000);
    } catch (e) {
      const detail = e.response?.data?.detail;
      if (detail && typeof detail === "string") error.value = detail;
      else if (e.response?.status === 422) {
        const errs = e.response.data?.detail;
        error.value = Array.isArray(errs) && errs.length ? (errs[0].msg || "输入格式有误") : "输入格式有误";
      } else error.value = "操作失败，请重试";
    } finally {
      loading.value = false;
    }
    return;
  }

  // ========== 注册 ==========
  if (isRegister.value) {
    usernameError.value = validateUsername(username.value);
    passwordError.value = validatePassword(password.value);
    phoneError.value = validatePhone(phone.value);
    if (usernameError.value || passwordError.value || phoneError.value) return;
  } else {
    // ========== 登录 ==========
    if (!username.value.trim() || !password.value) {
      error.value = "请填写用户名和密码";
      return;
    }
  }

  loading.value = true;
  try {
    const fn = isRegister.value ? register : login;
    const args = isRegister.value
      ? [username.value.trim(), password.value, phone.value.trim()]
      : [username.value.trim(), password.value];
    const res = await fn(...args);
    userStore.setAuth(res.access_token, res.user);
    router.push("/");
  } catch (e) {
    const detail = e.response?.data?.detail;
    if (detail && typeof detail === "string") {
      error.value = detail;
    } else if (e.response?.status === 422) {
      const errs = e.response.data?.detail;
      if (Array.isArray(errs) && errs.length) {
        error.value = errs[0].msg || errs[0].message || "输入格式有误";
      } else {
        error.value = "输入格式有误，请检查";
      }
    } else {
      error.value = "操作失败，请重试";
    }
  } finally {
    loading.value = false;
  }
}
</script>
