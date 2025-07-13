<template>
  <div class="tw-flex tw-items-center tw-p-12">
    <div class="tw-flex tw-items-center tw-gap-12">
      <div class="tw-flex tw-flex-col tw-gap-6 tw-w-1/2">
        <div class="tw-flex tw-flex-col tw-gap-2">
          <div class="tw-flex tw-items-center">
            <div class="tw-w-12 tw-flex tw-justify-center">
              <i class="fa-solid fa-list-check fa-xl tw-text-primary-500" />
            </div>
            <h2>AiReview</h2>
          </div>
          <h3 class="tw-font-medium tw-text-[#4b5563] tw-ml-12">
            Explore Your Screening Experience with Al
          </h3>
        </div>

        <div class="tw-text-lg tw-flex tw-flex-col tw-gap-2 tw-mt-1">
          <div class="tw-flex tw-items-center">
            <div class="tw-w-12 tw-flex tw-justify-center">
              <i class="fa-solid fa-rocket fa-lg tw-text-primary-500" />
            </div>
            <h4>Why AiReview?</h4>
          </div>
          <h4 class="tw-flex tw-font-normal tw-text-[#4b5563] tw-ml-12">
            <div class="tw-flex tw-items-center tw-justify-center">
              <div class="tw-w-10 tw-flex tw-items-center tw-h-[50%]">
                <i class="pi pi-cog tw-text-primary-500" />
              </div>
              <h5 class="tw-font-normal">
                <b>Transparent Al Pipeline</b> - Full control over Al roles.
                prompts, and configurations
              </h5>
            </div>
          </h4>

          <h4 class="tw-flex tw-font-normal tw-text-[#4b5563] tw-ml-12">
            <div class="tw-flex tw-items-center tw-justify-center">
              <div class="tw-w-10 tw-flex tw-items-center tw-h-[50%]">
                <i class="fa-solid fa-plug tw-text-primary-500" />
              </div>
              <h5 class="tw-font-normal">
                <b>Flexible LLM Integration</b> - Connect and customize your
                preferred large language models
              </h5>
            </div>
          </h4>

          <h4 class="tw-flex tw-font-normal tw-text-[#4b5563] tw-ml-12">
            <div class="tw-flex tw-items-center tw-justify-center">
              <div class="tw-w-10 tw-flex tw-items-center tw-h-[50%]">
                <i class="pi pi-sliders-h tw-text-primary-500" />
              </div>
              <h5 class="tw-font-normal">
                <b>Bias-Aware Screening</b> - Control Al influence with
                adjustable interaction levels
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
            admin@ielab.io
          </p>
        </div>
      </div>

      <Card
        class="tw-text-black tw-bg-primary-50 tw-w-1/2"
        :pt="{ content: 'tw-pb-0' }"
      >
        <template #title>
          <div class="tw-flex tw-gap-4 tw-items-center">
            <i
              class="fa-solid fa-arrow-right-to-bracket tw-text-primary-500 fa-lg"
            />
            <p class="tw-text-3xl tw-font-bold">Log in</p>
          </div>
        </template>
        <template #content>
          <div class="tw-flex tw-flex-col tw-gap-4" @keydown.enter="login">
            <Inputbox
              v-for="item in config"
              v-model="formData[item.dataKey as keyof typeof formData]"
              :type="item.type"
              :label="item.label"
              :mandatory="item.mandatory"
              :feedback="item.feedback"
              class="tw-w-full"
            />
            <div class="tw-flex tw-justify-end">
              <Button
                text
                label="Forgot your password?"
                :pt="{ root: 'tw-p-2' }"
                @click="forgotPasswordVisible = true"
              />
            </div>
            <Button
              label="Log in"
              @click="login"
              class="tw-w-full"
              :loading="loginIsLoading"
              :disabled="isLoading"
            />
            <Button
              label="Log in via OTP"
              @click="
                hasSentOtp
                  ? (otpDialogVisible = true)
                  : (loginOTPVisible = true)
              "
              class="tw-w-full"
              outlined
              :disabled="isLoading || loginIsLoading"
            />
            <div class="tw-flex tw-items-center tw-gap-2 tw-justify-center">
              <p class="tw-text-[#4b5563]">Don't have an account?</p>
              <Button
                text
                label="Create new account"
                :pt="{ root: 'tw-p-2' }"
                @click="signUpVisible = true"
              />
            </div>
          </div>
        </template>
      </Card>
    </div>

    <Dialog
      :visible="loginOTPVisible"
      modal
      :draggable="false"
      class="tw-w-1/3"
    >
      <template #header>
        <div class="tw-flex tw-justify-center tw-w-full">
          <p class="tw-text-3xl tw-font-bold">Log in via OTP</p>
        </div>
      </template>

      <template #closeicon>
        <i class="pi pi-times" @click="loginOTPVisible = false" />
      </template>

      <div class="tw-flex tw-flex-col tw-gap-8" @keydown.enter="validate()">
        <InlineMessage severity="info">
          Enter the email address you registered with, and we’ll send you an OTP
          to log into the system.
        </InlineMessage>
        <div class="tw-flex tw-flex-col tw-gap-2">
          <label for="email">Email</label>
          <InputText v-model="email" />
        </div>
        <InlineMessage v-if="errorMessage" severity="error">
          {{ errorMessage }}
        </InlineMessage>
      </div>
      <template #footer>
        <Button
          label="Continue"
          class="tw-w-full"
          @click="validate()"
          :loading="isLoading"
        />
      </template>
    </Dialog>

    <Dialog v-model:visible="otpDialogVisible" modal :draggable="false">
      <template #header>
        <div class="tw-flex tw-justify-center tw-w-full">
          <p class="tw-text-3xl tw-font-bold">Log in via OTP</p>
        </div>
      </template>
      <div class="tw-flex tw-flex-col tw-gap-8">
        <InlineMessage severity="success">
          <div class="tw-flex tw-flex-col tw-text-center">
            <small>
              We've sent a verificaton code to your email -
              <span class="tw-font-medium">{{ email }}</span>
            </small>
          </div>
        </InlineMessage>
        <div class="otp-wrapper" @keydown.enter="verifyOTP()">
          <InputText
            v-for="(_digit, index) in otp"
            :key="index"
            v-model="otp[index]"
            class="otp-box"
            maxlength="1"
            @input="focusNext(index)"
          />
        </div>
        <InlineMessage v-if="errorMessage" severity="error">
          {{ errorMessage }}
        </InlineMessage>
      </div>

      <template #footer>
        <div class="tw-flex tw-flex-col tw-gap-2">
          <Button
            label="Continue"
            @click="verifyOTP()"
            :loading="isLoading"
            class="tw-w-full"
          />
          <Button
            text
            :label="
              canResend ? `Resend OTP` : `Resend OTP in ${formatCountdown()}`
            "
            :disabled="!canResend"
            @click="requestOTP()"
            class="tw-w-full"
          />
        </div>
      </template>
    </Dialog>

    <SignUp :visible="signUpVisible" @update:visible="signUpVisible = false" />

    <ForgotPassword
      :visible="forgotPasswordVisible"
      @update:visible="forgotPasswordVisible = false"
    />
  </div>
</template>
<script lang="ts" setup>
import { ref } from "vue";
import { storeToken } from "@/utils/auth";
import { config } from "./configs/loginConfig.ts";
import { DEFAULT_LOGIN_FORM } from "@/defaults/auth";

import SignUp from "./components/SignUp.vue";
import ForgotPassword from "./components/ForgotPassword.vue";
import Card from "primevue/card";
import Inputbox from "@/components/Inputbox.vue";
import Dialog from "primevue/dialog";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import Divider from "primevue/divider";
import InlineMessage from "primevue/inlinemessage";

import { useRouter, useRoute } from "vue-router";
const router = useRouter();
const route = useRoute();

import { useLoading } from "@/composables/loading";
const { setLoading, isLoading } = useLoading(false);

import { useToast } from "@/composables/toast";
const { showToast } = useToast();

import { useError } from "@/composables/error";
const { getResponseErrorMessage } = useError();

const signUpVisible = ref(false);
const forgotPasswordVisible = ref(false);
const loginOTPVisible = ref(false);
const otpDialogVisible = ref(false);

// Login --------------------------------------------------
const formData = ref({ ...DEFAULT_LOGIN_FORM });

import axios, { AxiosError } from "axios";
import { ValidationError } from "joi";
import { loginSchema } from "./validators/login";
const loginIsLoading = ref(false);

const login = async () => {
  try {
    loginIsLoading.value = true;
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
    loginIsLoading.value = false;
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
  }
};

// --------------------------------------------------------
import Joi from "joi";

import { useCountdown } from "@/utils/otp.ts";
const { startCountdown, formatCountdown, resetCountdown, canResend } =
  useCountdown();

import { focusNext } from "@/utils/otp.ts";

const email = ref("");
const otp = ref(["", "", "", "", "", ""]);
const hasSentOtp = ref(false);
const errorMessage = ref("");

const emailSchema = Joi.object({
  email: Joi.string()
    .email({ tlds: { allow: false } })
    .label("Email")
    .required()
    .messages({ "string.empty": "{{#label}} is required" }),
});

const validate = () => {
  try {
    const validate = emailSchema.validate(
      { email: email.value },
      { abortEarly: false }
    );
    if (validate.error) throw validate.error;
    requestOTP();
  } catch (error) {
    const e = error as ValidationError;
    showToast(
      "error",
      "Invalid",
      `\n-${e.message.split(". ").join("\n\n- ")}\n\n`
    );
    errorMessage.value = e.message;
  }
};

const requestOTP = async () => {
  try {
    setLoading(true);
    errorMessage.value = "";
    await axios.post("/auth/request-otp", {
      email: email.value,
      key: "log_in_otp",
    });
    loginOTPVisible.value = false;
    otpDialogVisible.value = true;
    hasSentOtp.value = true;
    resetCountdown();
    startCountdown();
  } catch (error) {
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error);
      showToast("error", e.message);
      errorMessage.value = e.message;
    } else {
      showToast("error", "Unknown error", error as string);
      errorMessage.value = error as string;
    }
  } finally {
    setLoading(false);
  }
};

const verifyOTP = async () => {
  try {
    if (otp.value.join("").length <= 0) {
      errorMessage.value = "Please enter the OTP";
      return;
    }

    setLoading(true);
    errorMessage.value = "";
    const result = await axios.post("/auth/validate-otp", {
      email: email.value,
      otp: otp.value.join(""),
      key: "log_in_otp",
    });
    storeToken(result.data.token);

    otpDialogVisible.value = false;
    router.push({ name: "mydataset" });
  } catch (error) {
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error);
      showToast("error", e.message);
      errorMessage.value = e.message;
    } else {
      showToast("error", "Unknown error", error as string);
      errorMessage.value = error as string;
    }
  } finally {
    setLoading(false);
  }
};
</script>
