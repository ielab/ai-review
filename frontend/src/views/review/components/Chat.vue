<template>
  <div>
    <div class="tw-p-2 tw-flex tw-flex-col tw-gap-2 tw-relative">
      <!-- <div
          class="tw-absolute tw-translate-x-[-50%] tw-left-0 tw-top-0 tw-flex tw-items-center tw-justify-center sidebar-button tw-transition-opacity"
        >
          <Button
            :pt="{ root: 'tw-p-0 tw-w-8 tw-h-8 tw-shadow tw-mx-2' }"
            icon="pi pi-angle-right"
            rounded
            size="small"
            @click="visibleChat = !visibleChat"
          />
        </div> -->
      <!-- <div class="tw-rounded-xl tw-p-2 tw-flex tw-gap-4">
        <div>
          <i class="pi pi-user tw-bg-gray-200 tw-p-3 tw-rounded-full" />
        </div>
        <div class="tw-flex tw-flex-col tw-gap-4">
          <div class="tw-flex tw-flex-col tw-gap-1">
            <p class="tw-font-medium">User</p>
            <p>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
              eiusmod tempor incididunt ut labore et dolore magna aliqua.
            </p>
          </div>
        </div>
      </div> -->

      <div
        class="tw-flex tw-justify-between tw-items-center tw-bg-slate-50 tw-px-4 tw-py-3 tw-rounded-lg"
      >
        <div class="tw-w-[90%] tw-flex tw-items-center">
          <div
            class="tw-w-full tw-flex tw-items-center tw-gap-2 tw-overflow-hidden"
          >
            <i class="pi pi-book tw-text-indigo-500" />
            <Dropdown
              v-model="selectedChat"
              :options="chats"
              optionLabel="name"
              class="tw-w-[75%]"
              :pt="{
                root: 'tw-border-none tw-bg-transparent',
                input: 'tw-p-0',
                trigger: 'tw-w-5',
              }"
            />
            <p class="tw-text-xs tw-text-slate-400">Study #1</p>
          </div>
        </div>
        <i class="pi pi-pen-to-square" />
      </div>

      <div
        class="tw-bg-indigo-50/70 tw-rounded-xl tw-p-2 tw-flex tw-gap-4 tw-h-[48vh] tw-overflow-y-auto"
      >
        <div>
          <i
            class="pi pi-sparkles tw-text-indigo-500 tw-bg-indigo-100 tw-p-3 tw-rounded-full"
          />
        </div>
        <div class="tw-flex tw-flex-col tw-gap-2">
          <div class="tw-flex tw-flex-col tw-gap-[0.9rem] tw-leading-relaxed">
            <div>
              Based on the selected study and the configured inclusion/exclusion
              criteria, here’s my feedback:
            </div>

            <div>
              <b
                >“Posttraumatic Stress Symptoms after Exposure to Two Fire
                Disasters: Comparative Study” by</b
              >
              Van Loey NE; van de Schoot R; Faber AW
            </div>

            <div>
              <b>Conclusion</b>: This study meets all inclusion criteria: it’s
              longitudinal, measures PTSD using the Impact of Event Scale,
              applies latent growth modeling, and investigates trauma consistent
              with DSM-IV criterion A1.
            </div>

            <div>
              <b>Relevance</b>:<br />Rated 4/4 (high probability of inclusion)
              for the systematic review.
            </div>
          </div>
        </div>
      </div>

      <div class="tw-bg-indigo-50/70 tw-rounded-xl tw-p-2 tw-flex tw-gap-4">
        <div>
          <i
            class="pi pi-sparkles tw-text-indigo-500 tw-bg-indigo-100 tw-p-3 tw-rounded-full"
          />
        </div>
        <div class="tw-flex tw-flex-col tw-gap-2">
          <div class="tw-flex tw-flex-col tw-gap-2">
            <p>What other tasks can I assist with?</p>
            <div class="tw-flex tw-gap-2 tw-w-full">
              <Button
                text
                icon="pi pi-bookmark"
                label="PICO Extraction"
                :pt="{
                  root: 'tw-bg-indigo-100 tw-p-2',
                  label: 'tw-font-medium',
                }"
              />
              <Button
                text
                icon="pi pi-lightbulb"
                label="Detailed Reasoning"
                :pt="{
                  root: 'tw-bg-indigo-100 tw-p-2',
                  label: 'tw-font-medium',
                }"
              />
            </div>
          </div>
        </div>
      </div>
      <InputGroup class="tw-mt-2">
        <InputText :disabled="reviewerStore.level === 'low'" />
        <Button icon="pi pi-send" :disabled="reviewerStore.level === 'low'" />
      </InputGroup>
    </div>
  </div>
</template>

<script lang="ts" setup>
import Button from "@/components/Button.vue";
import Dropdown from "primevue/dropdown";
import InputText from "primevue/inputtext";
import InputGroup from "primevue/inputgroup";

import { ref } from "vue";
import { reviewerStore } from "@/stores/reviewer";

const chats = ref([{ name: "Posttraumatic Stress Symptoms after" }]);
const selectedChat = ref(chats.value[0]);

async function chatClient2(uri: any, inputMsg: any) {
  try {
    const websocket = new WebSocket(uri);

    websocket.onopen = () => {
      const message = JSON.stringify({ message: inputMsg });
      websocket.send(message);
      console.log(`[You]:\t${inputMsg}`);
      // process.stdout.write("[LLM]:\t");
    };

    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const response = data?.data?.chunk || "";
        const eventType = data?.event || "";

        if (
          eventType === "on_parser_start" ||
          eventType === "on_parser_stream"
        ) {
          console.log(response);

          // process.stdout.write(response);
        } else {
          console.log(); // Newline after complete response
          websocket.close();
        }
      } catch (error) {
        console.error("\nError decoding JSON response.");
        websocket.close();
      }
    };

    websocket.onclose = () => {
      console.log("\nConnection closed.");
    };

    websocket.onerror = (error) => {
      console.error("\nAn error occurred:", error);
      websocket.close();
    };
  } catch (error) {
    console.error("\nAn error occurred:", error);
  }
}

const userId = `u${String(1).padStart(5, "0")}`;
const reviewId = `r${String(8).padStart(5, "0")}`;
const uri = `ws://aireview.ielab.io/api/ws/chat/${userId}/${reviewId}/`;

chatClient2(uri, "Why the sky is blue?");
</script>
