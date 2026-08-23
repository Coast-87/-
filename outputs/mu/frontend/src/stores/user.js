import { reactive } from "vue";

export const userStore = reactive({
  user: JSON.parse(localStorage.getItem("user") || "null"),
  token: localStorage.getItem("token") || "",

  get isLoggedIn() {
    return !!this.token && !!this.user;
  },

  get isAdmin() {
    return this.user?.role === "admin";
  },

  setAuth(token, user) {
    this.token = token;
    this.user = user;
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(user));
  },

    updateAvatar(avatarUrl) {
    if (this.user) {
      this.user.avatar = avatarUrl;
      localStorage.setItem("user", JSON.stringify(this.user));
    }
  },

  logout() {
    this.token = "";
    this.user = null;
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  },
});

