import { createRouter, createWebHistory } from "vue-router";
import { userStore } from "../stores/user";

const routes = [
  {
    path: "/",
    name: "Welcome",
    component: () => import("../views/Welcome.vue"),
  },
  {
    path: "/market",
    name: "Home",
    component: () => import("../views/Home.vue"),
  },
  {
    path: "/publish",
    name: "Publish",
    component: () => import("../views/Publish.vue"),
  },
  {
    path: "/product/:id",
    name: "Detail",
    component: () => import("../views/Detail.vue"),
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("../views/Login.vue"),
  },
  {
    path: "/profile",
    name: "Profile",
    component: () => import("../views/Profile.vue"),
  },
  {
    path: "/admin",
    name: "Admin",
    component: () => import("../views/Admin.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 路由守卫：已登录用户访问 / 自动跳转 /market
router.beforeEach((to, from, next) => {
  if (to.name === "Welcome" && userStore.isLoggedIn) {
    next("/market");
  } else {
    next();
  }
});

export default router;
