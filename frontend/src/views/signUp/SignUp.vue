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
      <CustomIconButton
        icon="fa-solid fa-xmark fa-lg"
        @click="emit('update:visible')"
        severity="secondary"
        text
      />
    </template>

    <div class="tw-gap-4 tw-grid">
      <Inputbox
        v-for="item in config"
        v-model="formData[item.dataKey as keyof typeof formData]"
        :type="item.type"
        :label="item.label"
        :mandatory="item.mandatory"
        :feedback="item.feedback"
      />
      <div class="tw-text-slate-500">
        <span class="pi pi-exclamation-circle tw-pr-1 tw-text-amber-500"></span>
        The provided email is for expressing your interest to receive any update
        about our system. There is no need for email verification at the moment.
      </div>
    </div>
    <template #footer>
      <CustomButton
        label="Sign Up"
        @click="validate"
        :isLoading="isLoading"
        class="tw-mt-4"
      />
    </template>
  </Dialog>

  <Modal
    v-model:is-active="signUpSuccess"
    header="Sign Up successfully"
    title="Sign up with this e-mail successfully."
    leftBtn="Okay"
    icon="pi pi-check-circle"
    iconColor="success"
  >
    <template #value> {{ formData.email }} </template>
  </Modal>
  <Modal
    v-model:is-active="confirmSignUp"
    header="Confirm Account Creation"
    title="Please Review the Information"
    rightBtn="Confirm"
    leftBtn="Cancel"
    icon="pi pi-exclamation-circle"
    iconColor="warning"
    @confirm="signUp()"
  >
    <template #body>
      <div class="tw-flex tw-flex-col tw-gap-6 tw-my-8">
        <div class="tw-text-rose-400 tw-font-semibold">
          You will not be able to change your information after account is
          created.
        </div>
        <div>
          Username:
          <span class="tw-font-bold tw-text-xl tw-pl-5">{{
            formData.username
          }}</span>
        </div>
        <div>
          Email:
          <span class="tw-font-bold tw-text-xl tw-pl-5">{{
            formData.email
          }}</span>
        </div>
      </div>
    </template>
    <template #note>
      <span class="pi pi-exclamation-circle tw-pr-2 tw-text-violet-600"></span>
      Note that as a current system is a demo version, it will not send any
      messages to your email account. Please write down your username and
      password as the system does not have a password recovery function.
    </template>
  </Modal>

  <!-- <Container>
    <div class="tw-flex tw-w-5/12">
      <Card class="tw-w-full">
        <template #title>
          <div class="tw-mt-3 tw-mb-8">Sign up</div>
          <Divider type="solid" />
        </template>
        <template #content>
          <div class="tw-gap-5 tw-grid">
            <Inputbox
              v-for="item in config"
              v-model="formData[item.dataKey as keyof typeof formData]"
              :type="item.type"
              :label="item.label"
              :mandatory="item.mandatory"
              :feedback="item.feedback"
            ></Inputbox>
            <div class="tw-text-slate-500 tw-mt-2">
              <span class="pi pi-exclamation-circle tw-pr-1 tw-text-amber-500"></span>
              The provided email is for expressing your interest to receive any update about our
              system. There is no need for email verification at the moment.
            </div>
          </div>
        </template>
        <template #footer>
          <div class="tw-gap-10 tw-flex tw-items-center tw-mt-3">
            <Button
              class="tw-w-full"
              label="Sign Up"
              @click="validate"
              :isLoading="isLoading"
            ></Button>
          </div>
        </template>
      </Card>
    </div>
  </Container>
  <Modal
    v-model:is-active="signUpSuccess"
    header="Sign Up successfully"
    title="Sign up with this e-mail successfully."
    leftBtn="Okay"
    icon="pi pi-check-circle"
    iconColor="success"
    route="login"
  >
    <template #value> your_email@someMail.com </template>
  </Modal>
  <Modal
    v-model:is-active="confirmSignUp"
    header="Confirm Account Creation"
    title="Please Review the Information"
    rightBtn="Confirm"
    leftBtn="Cancel"
    icon="pi pi-exclamation-circle"
    iconColor="warning"
    @confirm="signUp()"
  >
    <template #body>
      <div class="tw-flex tw-flex-col tw-gap-6 tw-my-8">
        <div class="tw-text-rose-400 tw-font-semibold">
          You will not be able to change your information after account is created.
        </div>
        <div>
          Username: <span class="tw-font-bold tw-text-xl tw-pl-5">{{ formData.username }}</span>
        </div>
        <div>
          Email: <span class="tw-font-bold tw-text-xl tw-pl-5">{{ formData.email }}</span>
        </div>
      </div>
    </template>
    <template #note>
      <span class="pi pi-exclamation-circle tw-pr-2 tw-text-violet-600"></span>
      Note that as a current system is a demo version, it will not send any messages to your email
      account. Please write down your username and password as the system does not have a password
      recovery function.
    </template>
  </Modal> -->
</template>
<script lang="ts" setup>
import { ref } from "vue";

import { config } from "./configs/signUpConfig.ts";
import { DEFAULT_SIGN_UP_FORM } from "@/defaults/auth";

import Dialog from "primevue/dialog";
// import Divider from 'primevue/divider'
// import Card from 'primevue/card'
// import Button from '@/components/Button.vue'
import Inputbox from "@/components/Inputbox.vue";
// import Container from '@/components/Container.vue'
import CustomButton from "@/components/CustomButton.vue";

import Modal from "@/components/Modal.vue";
const confirmSignUp = ref(false);
const signUpSuccess = ref(false);

import { useToast } from "@/composables/toast";
const { showToast } = useToast();

import { useError } from "@/composables/error";
const { getResponseErrorMessage } = useError();

const props = defineProps({
  visible: { type: Boolean, default: false },
});

const emit = defineEmits(["update:visible"]);

// Sign Up --------------------------------------------------------------------

import axios, { AxiosError } from "axios";
import { ValidationError } from "joi";
import { signUpSchema } from "./validators/signUp";
import CustomIconButton from "@/components/CustomIconButton.vue";

const formData = ref({ ...DEFAULT_SIGN_UP_FORM });
const isLoading = ref(false);

const validate = () => {
  try {
    isLoading.value = true;
    const body = formData.value;
    const validate = signUpSchema.validate(body, { abortEarly: false });
    if (validate.error) throw validate.error;
    confirmSignUp.value = true;
  } catch (error) {
    const e = error as ValidationError;
    showToast(
      "error",
      "Invalid",
      `\n-${e.message.split(". ").join("\n\n- ")}\n\n`
    );
    isLoading.value = false;
  }
};

const signUp = async () => {
  try {
    const body = formData.value;
    await axios.post("/auth/sign-up", body);
    emit("update:visible");
    signUpSuccess.value = true;
  } catch (error) {
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error);
      showToast("error", e.message);
    } else {
      showToast("error", "Unknown error", error as string);
    }
  } finally {
    isLoading.value = false;
  }
};

// ----------------------------------------------------------------------------
</script>
