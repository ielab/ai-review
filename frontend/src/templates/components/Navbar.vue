<template>
  <Menubar
    :model="isLoggedIn ? itemsLogin : items"
    :pt="{
      root: 'tw-py-0 tw-bg-primary-900 tw-h-[6vh]',
      action: ({ context }) => ({
        class: context.active
          ? 'tw-text-black'
          : context.focused
          ? 'tw-text-black'
          : 'tw-text-white',
      }),
    }"
    class="tw-w-full tw-z-0 tw-border-0"
  >
    <template #item="{ item, props, hasSubmenu }">
      <div v-if="item.route" @click="router.push({ name: item.route })" custom>
        <div class="tw-flex tw-items-center" v-bind="props.action">
          <span :class="item.icon" />
          <span class="tw-pl-3">{{ item.label }}</span>
        </div>
      </div>
      <div v-else :href="item.url" :target="item.target" v-bind="props.action">
        <span :class="item.icon" />
        <span class="tw-pl-3">{{ item.label }}</span>
        <i v-if="hasSubmenu" class="pi pi-angle-down text-primary tw-ml-1"></i>
      </div>
    </template>
  </Menubar>

  <Modal
    v-model:isActive="logout_modal"
    route="login"
    header="Confirm to log out"
    title="You are about to log out"
    leftBtn="Back"
    rightBtn="Log out"
    icon="pi pi-exclamation-circle"
    iconColor="warning"
    @confirm="logout"
  >
    <template #body>
      Your data will be periodically erased from the system.
    </template>
  </Modal>
</template>

<script lang="ts" setup>
import { computed, ref } from "vue";

import Menubar from "primevue/menubar";
import Modal from "@/components/Modal.vue";

import { useRouter } from "vue-router";
const router = useRouter();

import { useToast } from "@/composables/toast";
const { showToast } = useToast();

import { useError } from "@/composables/error";
const { getResponseErrorMessage } = useError();

const logout_modal = ref();

const itemsLogin = computed(() => [
  {
    label: "Home",
    icon: "pi pi-home",
    route: "home",
  },
  {
    label: "My Dataset/Review",
    icon: "pi pi-inbox",
    route: "mydataset",
  },
  {
    label: accountAuthStore.username,
    icon: "pi pi-user",
    route: "",
    items: [
      {
        label: "Logout",
        icon: "pi pi-signout",
        command: () => {
          logout_modal.value = true;
        },
      },
    ],
  },
]);

const items = ref([
  {
    label: "Home",
    icon: "pi pi-home",
    route: "home",
  },
  {
    label: "Log in/Sign up",
    icon: "pi pi-sign-in",
    route: "login",
  },
]);

// Account Information ---------------------------------------------------------

import { accountAuthStore, cleanAccountAuthStore } from "@/stores/auth";

import axios, { AxiosError } from "axios";
import { getTokenHeader } from "@/utils/auth";

const isLoggedIn = computed(() => accountAuthStore.id !== null);

const logout = async () => {
  try {
    await axios.post("/auth/logout", {}, getTokenHeader());
    cleanAccountAuthStore();
  } catch (error) {
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error);
      showToast("error", e.message);
    } else {
      showToast("error", "Unknown error", error as string);
    }
  }
};

// -----------------------------------------------------------------------------
</script>
