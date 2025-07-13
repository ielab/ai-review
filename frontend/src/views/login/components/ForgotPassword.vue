<template>
  <Dialog
    v-model:visible="props.visible"
    modal
    :draggable="false"
    class="tw-w-1/3"
  >
    <template #header>
      <div class="tw-flex tw-justify-center tw-w-full">
        <p class="tw-text-3xl tw-font-bold">Forgot password</p>
      </div>
    </template>

    <template #closeicon>
      <i class="pi pi-times" @click="emit('update:visible')" />
    </template>

    <div class="tw-flex tw-flex-col tw-gap-8" @keydown.enter="validateEmail()">
      <InlineMessage severity="info">
        Enter the email address you registered with, and we’ll send you an OTP
        to reset your password.
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
        label="Reset password"
        class="tw-w-full"
        @click="validateEmail()"
        :loading="isLoading"
      />
    </template>
  </Dialog>

  <Dialog v-model:visible="otpDialogVisible" modal :draggable="false">
    <template #header>
      <div class="tw-flex tw-justify-center tw-w-full">
        <p class="tw-text-3xl tw-font-bold">Password reset</p>
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
          class="tw-w-full"
          @click="verifyOTP()"
          :loading="isLoading"
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

  <Dialog
    v-model:visible="setNewPasswordDialogVisible"
    modal
    :draggable="false"
    class="tw-w-1/3"
  >
    <template #header>
      <div class="tw-flex tw-justify-center tw-w-full">
        <p class="tw-text-3xl tw-font-bold">Set new password</p>
      </div>
    </template>
    <div class="tw-flex tw-flex-col tw-gap-8" @keydown.enter="validatePassword">
      <div class="tw-flex tw-flex-col tw-gap-2">
        <label for="password">Password</label>
        <Password
          v-model="password"
          toggleMask
          :pt="{
            hideIcon: 'tw-translate-y-[-50%]',
            showIcon: 'tw-translate-y-[-50%]',
          }"
        />
      </div>
      <div class="tw-flex tw-flex-col tw-gap-2">
        <label for="confirmPassword">Confirm Password</label>
        <Password
          v-model="confirmPassword"
          toggleMask
          :feedback="false"
          :pt="{
            hideIcon: 'tw-translate-y-[-50%]',
            showIcon: 'tw-translate-y-[-50%]',
          }"
        />
      </div>
    </div>

    <InlineMessage v-if="errorMessage" severity="error">
      {{ errorMessage }}
    </InlineMessage>

    <template #footer>
      <Button
        label="Reset password"
        class="tw-w-full"
        @click="validatePassword"
        :loading="isLoading"
      />
    </template>
  </Dialog>

  <Modal
    v-model:is-active="resetPasswordSuccessDialog"
    header="All done!"
    title="Your password has been reset."
    leftBtn="Okay"
    icon="pi pi-check-circle"
    iconColor="success"
  />
</template>

<script lang="ts" setup>
import { ref, watch } from "vue";
import Dialog from "primevue/dialog";
import InputText from "primevue/inputtext";
import Password from "primevue/password";
import InlineMessage from "primevue/inlinemessage";
import Button from "primevue/button";
import Modal from "@/components/Modal.vue";

import { useLoading } from "@/composables/loading";
const { setLoading, isLoading } = useLoading(false);

const props = defineProps({
  visible: { type: Boolean, default: false },
});

const otpDialogVisible = ref(false);
const setNewPasswordDialogVisible = ref(false);
const resetPasswordSuccessDialog = ref(false);

const errorMessage = ref();

const emit = defineEmits(["update:visible"]);

const email = ref("");
const password = ref("");
const confirmPassword = ref("");

import { useToast } from "@/composables/toast";
const { showToast } = useToast();

import { useError } from "@/composables/error";
const { getResponseErrorMessage } = useError();

import Joi from "joi";
import { ValidationError } from "joi";
import axios, { AxiosError } from "axios";

const emailSchema = Joi.object({
  email: Joi.string()
    .email({ tlds: { allow: false } })
    .label("Email")
    .required()
    .messages({ "string.empty": "{{#label}} is required" }),
});

const passwordSchema = Joi.object({
  password: Joi.string()
    .min(3)
    .max(15)
    .required()
    .label("Password")
    .messages({ "string.empty": "{{#label}} is required" }),
  confirm_password: Joi.any()
    .equal(Joi.ref("password"))
    .required()
    .label("Confirm Password")
    .messages({ "any.only": "{{#label}} does not match" }),
});

const hasSentOtp = ref(false);
const hasVerifyOtp = ref(false);

const validateEmail = () => {
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

const validatePassword = () => {
  try {
    const validate = passwordSchema.validate(
      { password: password.value, confirm_password: confirmPassword.value },
      { abortEarly: false }
    );
    if (validate.error) throw validate.error;
    resetPassword();
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

// OTP
import { useCountdown } from "@/utils/otp";
const { startCountdown, formatCountdown, resetCountdown, canResend } =
  useCountdown();
import { focusNext } from "@/utils/otp";
const otp = ref(["", "", "", "", "", ""]);

const requestOTP = async () => {
  try {
    setLoading(true);
    errorMessage.value = "";
    await axios.post("/auth/request-otp", {
      email: email.value,
      key: "reset_password_otp",
    });
    emit("update:visible");
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
    await axios.post("/auth/validate-otp", {
      email: email.value,
      otp: otp.value.join(""),
      key: "reset_password_otp",
    });
    otpDialogVisible.value = false;
    setNewPasswordDialogVisible.value = true;
    hasVerifyOtp.value = true;
  } catch (error) {
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error);
      errorMessage.value = e.message;
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

const resetPassword = async () => {
  try {
    setLoading(true);
    errorMessage.value = "";
    await axios.post("/auth/reset-password", {
      email: email.value,
      otp: otp.value.join(""),
      password: password.value,
      confirm_password: confirmPassword.value,
      key: "reset_password_otp",
    });
    setNewPasswordDialogVisible.value = false;
    resetPasswordSuccessDialog.value = true;
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

watch(
  () => props.visible,
  (newVal) => {
    if (hasSentOtp.value && !hasVerifyOtp.value && newVal) {
      otpDialogVisible.value = true;
      emit("update:visible");
    } else if (hasSentOtp.value && hasVerifyOtp.value && newVal) {
      setNewPasswordDialogVisible.value = true;
      emit("update:visible");
    }
  }
);
</script>
