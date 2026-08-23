import axios from 'axios';

const api = axios.create({ baseURL: '/api', timeout: 60000 });

// 请求拦截器：自动附加 token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器：401 自动清除 token
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
    return Promise.reject(err);
  }
);

/** AI 图片分析 */
export function analyzeImages(files, note) {
  const formData = new FormData();
  files.forEach((f) => formData.append('files', f));
  if (note) formData.append('note', note);
  return api.post('/ai/analyze', formData).then((r) => r.data);
}

/** 注册 */
export function register(username, password, phone) {
  return api.post('/auth/register', { username, password, phone }).then((r) => r.data);
}

/** 登录 */
export function login(username, password) {
  return api.post('/auth/login', { username, password }).then((r) => r.data);
}

/** 获取当前用户 */
export function getMe() {
  return api.get('/auth/me').then((r) => r.data);
}

/** 找回密码：用户名 + 手机号验证 → 设置新密码 */
export function resetPassword(username, phone, newPassword) {
  return api.post('/auth/reset-password', { username, phone, new_password: newPassword }).then((r) => r.data);
}

/** 修改密码（需登录）：旧密码验证 → 设置新密码 */
export function changePassword(oldPassword, newPassword) {
  return api.post('/auth/change-password', { old_password: oldPassword, new_password: newPassword }).then((r) => r.data);
}

/** 发布商品 */
export function createProduct(data) {
  return api.post('/products', data).then((r) => r.data);
}

/** 获取商品列表 */
export function getProducts(params = {}) {
  return api.get('/products', { params }).then((r) => r.data);
}

/** 获取商品详情 */
export function getProduct(id) {
  return api.get(`/products/${id}`).then((r) => r.data);
}

/** 更新商品 */
export function updateProduct(id, data) {
  return api.put(`/products/${id}`, data).then((r) => r.data);
}

/** 删除商品 */
export function deleteProduct(id) {
  return api.delete(`/products/${id}`).then((r) => r.data);
}

/** 我的商品 */
export function getMyProducts(params = {}) {
  return api.get('/my/products', { params }).then((r) => r.data);
}

/** 上传头像 */
export function uploadAvatar(file) {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/auth/avatar', formData).then((r) => r.data);
}

/** 上传单张图片（后端含违规图片审核拦截） */
export function uploadImage(file) {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload', formData).then((r) => r.data);
}

/** 发布前文本敏感词预检 */
export function checkText(text) {
  return api.post('/moderation/check', { text }).then((r) => r.data);
}

/** 管理员：获取标记商品 */
export function getFlaggedProducts(params = {}) {
  return api.get('/admin/flagged', { params }).then((r) => r.data);
}

/** 管理员：获取所有商品 */
export function getAllProducts(params = {}) {
  return api.get('/admin/all', { params }).then((r) => r.data);
}

/** 管理员：下架商品 */
export function adminOffline(productId) {
  return api.post(`/admin/products/${productId}/offline`).then((r) => r.data);
}

/** 管理员：标记违规（强制下架） */
export function adminFlag(productId) {
  return api.post(`/admin/products/${productId}/flag`).then((r) => r.data);
}

/** 管理员：删除商品 */
export function adminDelete(productId) {
  return api.delete(`/admin/products/${productId}`).then((r) => r.data);
}

/** 管理员：取消标记 */
export function adminUnflag(productId) {
  return api.post(`/admin/products/${productId}/unflag`).then((r) => r.data);
}


/** 管理员：获取用户列表 */
export function getAdminUsers(params = {}) {
  return api.get('/admin/users', { params }).then((r) => r.data);
}

/** 管理员：创建账号（可指定角色） */
export function adminCreateUser(data) {
  return api.post('/admin/users', data).then((r) => r.data);
}

/** 管理员：修改用户角色 */
export function adminSetRole(userId, role) {
  return api.put(`/admin/users/${userId}/role`, { role }).then((r) => r.data);
}

/** 管理员：删除账号 */
export function adminDeleteUser(userId) {
  return api.delete(`/admin/users/${userId}`).then((r) => r.data);
}


export default api;
