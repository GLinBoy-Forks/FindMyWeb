import { createRouter, createWebHashHistory } from "vue-router";
import FindMyWeb from "./lib/FindMyWeb";
const FindMyWebAPI = new FindMyWeb();

export const history = createWebHashHistory();
export const router = createRouter({
  history,
  routes: [
    {
      path: "/",
      name: "Dashboard",
      component: () => import("./views/Dashboard.vue"),
    },
    {
      path: "/login",
      name: "Login",
      component: () => import("./views/Login.vue"),
    },
    {
      path: "/settings",
      name: "Settings",
      component: () => import("./views/Settings.vue"),
      children: [
        {
          path: "profile",
          name: "settings-profile",
          components: {
            settings: () => import("./components/Settings/ProfileSettings.vue"),
          },
        },
        {
          path: "admin",
          name: "settings-admin",
          components: {
            settings: () => import("./components/Settings/AdminSettings.vue"),
          },
        },
      ],
    },
  ],
});
router.beforeEach(async (to: any, from: any) => {
  console.log(`Redirecting from ${from.fullPath} to ${to.fullPath}`);
  if (to.name === "Login") {
    return;
  }
  try {
    await FindMyWebAPI.getAccessories();
  } catch (error) {
    console.error("User is not logged in redirecting to Login");
    return { name: "Login" };
  }
});
