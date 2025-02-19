<template>
  <div class="tw-items-center tw-p-12 tw-min-h-[86vh]">
    <div class="tw-flex tw-items-center tw-gap-12">
      <div class="tw-flex tw-flex-col tw-gap-6 tw-w-1/2">
        <div class="tw-flex tw-flex-col tw-gap-2">
          <div class="tw-flex tw-items-center">
            <div class="tw-w-12 tw-flex tw-justify-center">
              <i class="fa-solid fa-list-check fa-xl tw-text-primary-500" />
            </div>
            <h2>DenseReviewer</h2>
          </div>
          <h3 class="tw-font-medium tw-text-[#4b5563] tw-ml-12">
            Accelerate Your Title & Abstract Screening
          </h3>
        </div>

        <div class="tw-text-lg tw-flex tw-flex-col tw-gap-2 tw-mt-1">
          <div class="tw-flex tw-items-center">
            <div class="tw-w-12 tw-flex tw-justify-center">
              <i class="fa-solid fa-rocket fa-lg tw-text-primary-500" />
            </div>
            <h4>Why DenseReviewer?</h4>
          </div>
          <h4 class="tw-flex tw-font-normal tw-text-[#4b5563] tw-ml-12">
            <div class="tw-flex">
              <div class="tw-w-10 tw-flex tw-items-center tw-h-[50%]">
                <i class="fa-solid fa-brain tw-text-primary-500" />
              </div>
              <h5 class="tw-font-normal">
                <b>Al-Powered Ranking</b> - Our intelligent system learns from
                your screening decisions to prioritise relevant studies
              </h5>
            </div>
          </h4>

          <h4 class="tw-flex tw-font-normal tw-text-[#4b5563] tw-ml-12">
            <div class="tw-flex">
              <div class="tw-w-10 tw-flex tw-items-center tw-h-[50%]">
                <i class="fa-solid fa-keyboard tw-text-primary-500" />
              </div>
              <h5 class="tw-font-normal">
                <b>Efficient Screening Interface</b> - Streamlined workflow with
                keyboard shortcuts and dual viewing modes
              </h5>
            </div>
          </h4>

          <h4 class="tw-flex tw-font-normal tw-text-[#4b5563] tw-ml-12">
            <div class="tw-flex">
              <div class="tw-w-10 tw-flex tw-items-center tw-h-[50%]">
                <i class="fa-solid fa-chart-line tw-text-primary-500" />
              </div>
              <h5 class="tw-font-normal">
                <b>Real-time Progress Tracking</b> - Monitor your screening
                progress and study discovery rates
              </h5>
            </div>
          </h4>
        </div>

        <div class="tw-text-lg tw-flex tw-flex-col tw-gap-2">
          <div class="tw-flex tw-items-center">
            <div class="tw-w-12 tw-flex tw-justify-center">
              <i
                class="fa-regular fa-circle-question fa-lg tw-text-primary-500"
              />
            </div>
            <h4>Getting Started</h4>
          </div>
          <h5 class="tw-font-normal tw-ml-12 tw-text-[#4b5563]">
            Sign in or create an account to start accelerating your systematic
            review screening process. Our interactive system helps you identify
            key studies earlier in the process to accelerate downstream review
            tasks.
          </h5>
        </div>

        <div class="tw-px-4">
          <Divider />
        </div>

        <div
          class="tw-text-lg tw-flex tw-flex-col tw-text-sm tw-text-[#4b5563]"
        >
          <div class="tw-flex tw-items-center">
            <div class="tw-ml-2 tw-w-10 tw-flex tw-justify-center">
              <i class="fa-regular fa-envelope" />
            </div>
            <p class="tw-font-normal">For support or questions:</p>
          </div>
          <p class="tw-font-normal tw-ml-12 tw-text-primary-500 tw-font-medium">
            xinyu.mao@uq.edu.au
          </p>
        </div>
      </div>

      <Card class="tw-text-black tw-bg-primary-50 tw-w-1/2">
        <template #title>
          <div class="tw-flex tw-gap-4 tw-items-center">
            <i
              class="fa-solid fa-arrow-right-to-bracket tw-text-primary-500 fa-lg"
            />
            <p class="tw-text-3xl tw-font-bold">Log in</p>
          </div>
        </template>
        <template #content>
          <div class="tw-grid tw-gap-5" @keydown.enter="login">
            <Inputbox
              v-for="item in config"
              v-model="formData[item.dataKey as keyof typeof formData]"
              :type="item.type"
              :label="item.label"
              :mandatory="item.mandatory"
              :feedback="item.feedback"
            />
            <CustomButton label="Log in" @click="login" :loading="isLoading" />
            <CustomButton
              label="Create new account"
              outlined
              @click="visible = true"
            />
          </div>
        </template>
      </Card>
    </div>

    <SignUp :visible="visible" @update:visible="visible = false" />
  </div>
</template>
<script lang="ts" setup>
import { ref } from "vue";

import { storeToken } from "@/utils/auth";
import { config } from "./configs/loginConfig.ts";
import { DEFAULT_LOGIN_FORM } from "@/defaults/auth";

import SignUp from "../signUp/SignUp.vue";
import Card from "primevue/card";
import Inputbox from "@/components/Inputbox.vue";
// import Dialog from 'primevue/dialog'

import { useRouter, useRoute } from "vue-router";
const router = useRouter();
const route = useRoute();
const visible = ref(false);

import { useToast } from "@/composables/toast";
const { showToast } = useToast();

import { useError } from "@/composables/error";
const { getResponseErrorMessage } = useError();

// Login --------------------------------------------------

const formData = ref({ ...DEFAULT_LOGIN_FORM });
const isLoading = ref(false);

import axios, { AxiosError } from "axios";
import { ValidationError } from "joi";
import { loginSchema } from "./validators/login";
import CustomButton from "@/components/CustomButton.vue";
import Divider from "primevue/divider";

const login = async () => {
  try {
    isLoading.value = true;
    const body = formData.value;
    const validate = loginSchema.validate(body, { abortEarly: false });
    if (validate.error) throw validate.error;
    const result = await axios.post("/auth/login", body);
    storeToken(result.data.token);
    const redirectPath = route.query.next as string;
    redirectPath
      ? router.push(redirectPath)
      : router.push({ name: "mydataset" });
  } catch (error) {
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error);
      showToast("error", e.message);
    } else if (error instanceof ValidationError) {
      const e = error as ValidationError;
      showToast(
        "error",
        "Invalid",
        `\n-${e.message.split(". ").join("\n\n- ")}\n\n`
      );
    } else {
      showToast("error", "Unknown error", error as string);
    }
  } finally {
    isLoading.value = false;
  }
};

// --------------------------------------------------------
</script>
