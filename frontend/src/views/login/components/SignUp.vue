<template>
  <Dialog
    v-model:visible="props.visible"
    modal
    :pt="{ content: 'tw-py-0' }"
    class="tw-w-1/2"
  >
    <template #header>
      <div class="tw-flex tw-gap-4 tw-items-center">
        <i class="fa-solid fa-user-plus tw-text-primary-500 fa-2xl" />
        <p class="tw-text-3xl tw-font-bold">Sign up</p>
      </div>
    </template>

    <template #closeicon>
      <i class="pi pi-times" @click="emit('update:visible')" />
    </template>

    <div class="tw-grid tw-gap-2 tw-mb-2">
      <Inputbox
        v-for="item in config"
        v-model="formData[item.dataKey as keyof typeof formData]"
        :type="item.type"
        :label="item.label"
        :mandatory="item.mandatory"
        :feedback="item.feedback"
      />
    </div>
    <template #footer>
      <div class="tw-flex tw-flex-col">
        <div class="tw-text-slate-500 tw-mt-2 tw-text-left">
          <span class="pi pi-exclamation-circle tw-pr-1 tw-text-amber-500">
          </span>
          The provided email is for expressing your interest to receive any
          update about our system. There is no need for email verification at
          the moment.
        </div>
        <Button
          label="Sign Up"
          @click="validate"
          :loading="isLoading"
          class="tw-mt-4 tw-w-full"
        />
      </div>
    </template>
  </Dialog>

  <Dialog v-model:visible="otpDialogVisible" modal :draggable="false">
    <template #header>
      <div class="tw-flex tw-justify-center tw-w-full">
        <p class="tw-text-3xl tw-font-bold">Verify Your Email Address</p>
      </div>
    </template>
    <div class="tw-flex tw-flex-col tw-gap-8">
      <InlineMessage severity="success">
        <small>
          We've sent a verificaton code to your email -
          <span class="tw-font-medium">{{ formData.email }}</span>
        </small>
      </InlineMessage>
      <div class="otp-wrapper">
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

  <Modal
    v-model:is-active="signUpSuccessDialog"
    header="Sign Up successfully"
    title="Sign up with this e-mail successfully."
    leftBtn="Okay"
    icon="pi pi-check-circle"
    iconColor="success"
  >
    <template #value> {{ formData.email }} </template>
  </Modal>
</template>

<script lang="ts" setup>
import { ref, watch } from "vue";

import { config } from "../configs/signUpConfig.ts";
import { DEFAULT_SIGN_UP_FORM } from "@/defaults/auth";

import InlineMessage from "primevue/inlinemessage";
import InputText from "primevue/inputtext";
import Dialog from "primevue/dialog";
import Inputbox from "@/components/Inputbox.vue";
import Modal from "@/components/Modal.vue";
import Button from "primevue/button";

const signUpSuccessDialog = ref(false);
const otpDialogVisible = ref(false);

import { useToast } from "@/composables/toast";
const { showToast } = useToast();

import { useError } from "@/composables/error";
const { getResponseErrorMessage } = useError();

import { useLoading } from "@/composables/loading.ts";
const { setLoading, isLoading } = useLoading(false);

const props = defineProps({
  visible: { type: Boolean, default: false },
});

const emit = defineEmits(["update:visible"]);

// OTP
import { useCountdown } from "@/utils/otp.ts";
const { startCountdown, formatCountdown, resetCountdown, canResend } =
  useCountdown();
import { focusNext } from "@/utils/otp.ts";
const otp = ref(["", "", "", "", "", ""]);

// Sign Up --------------------------------------------------------------------

import axios, { AxiosError } from "axios";
import { ValidationError } from "joi";
import { signUpSchema } from "../validators/signUp.ts";

const formData = ref({ ...DEFAULT_SIGN_UP_FORM });
const hasSentOtp = ref(false);

const validate = () => {
  try {
    const body = formData.value;
    const validate = signUpSchema.validate(body, { abortEarly: false });
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
      ...formData.value,
      key: "sign_up_otp",
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

const errorMessage = ref();
const verifyOTP = async () => {
  try {
    if (otp.value.join("").length <= 0) {
      errorMessage.value = "Please enter the OTP";
      return;
    }

    setLoading(true);
    errorMessage.value = "";
    await axios.post("/auth/validate-otp", {
      ...formData.value,
      key: "sign_up_otp",
      otp: otp.value.join(""),
    });
    otpDialogVisible.value = false;
    signUpSuccessDialog.value = true;
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
    if (hasSentOtp.value && newVal) {
      otpDialogVisible.value = true;
      emit("update:visible");
    }
  }
);
</script>
