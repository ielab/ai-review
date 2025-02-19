<template>
  <div class="tw-w-[24%] tw-fixed tw-flex tw-flex-col tw-gap-y-2 tw-py-4">
    <Panel
      header="Control Keys"
      :pt="{ header: 'tw-py-2', content: 'tw-p-2' }"
      class="tw-w-full"
    >
      <div class="tw-flex tw-justify-around">
        <KeyBoardTips
          color="purple"
          keyLabel="Esc"
          event="Keypress"
          for="Quit Full Screen"
        />
        <KeyBoardTips
          color="purple"
          keyIcon="pi pi-arrow-up"
          keyLabel="Up"
          event="Keypress"
          for="Previous"
        />
        <KeyBoardTips
          color="purple"
          keyIcon="pi pi-arrow-down"
          keyLabel="Down"
          event="Keypress"
          for="Next"
        />
      </div>
    </Panel>
    <Panel
      header="Assessment Keys"
      :pt="{ header: 'tw-py-2', content: 'tw-p-2' }"
      class="tw-w-full"
    >
      <div class="tw-flex tw-justify-around">
        <KeyBoardTips
          color="red"
          keyIcon="pi pi-arrow-left"
          keyLabel="Left"
          event="Keypress"
          for="Exclude"
        />
        <KeyBoardTips
          color="slate"
          keyLabel="M"
          event="Keypress"
          for="Maybe"
        />
        <KeyBoardTips
          color="green"
          keyIcon="pi pi-arrow-right"
          keyLabel="Right"
          event="Keypress"
          for="Include"
        />
      </div>
    </Panel>
    <Panel
      header="Composite Keys"
      :pt="{ header: 'tw-py-2', content: 'tw-p-2' }"
      class="tw-w-full"
    >
      <div>
        <div class="tw-flex tw-items-center">
          <div class="tw-font-medium tw-text-sm tw-w-[50%]">
            <div class="tw-flex tw-justify-around tw-items-end tw-w-full">
              <div>
                <KeyBoardTips
                  color="purple"
                  keyLabel="Alt"
                />
                <div class="tw-flex">
                  Hold:&nbsp;<span class="tw-font-bold tw-text-purple-500"
                    >Alt <i class="fa-brands fa-windows"></i
                  ></span>
                </div>
              </div>
              <span>/</span>
              <div>
                <KeyBoardTips
                  color="purple"
                  keyIcon="Option"
                />
                <div class="tw-flex">
                  <span class="tw-font-bold tw-text-purple-500"
                    >Option <i class="fa-brands fa-apple"></i
                  ></span>
                </div>
              </div>
            </div>
          </div>
          <i class="pi pi-plus"></i>
          <div class="tw-w-[50%] tw-flex tw-items-center tw-justify-around">
            <p class="tw-font-medium">Assessment Key</p>
          </div>
        </div>
        <p class="tw-text-sm tw-font-medium tw-text-center">
          Assessment and Move to Next
        </p>
      </div>
      <Divider class="tw-my-3" />
      <div>
        <div class="tw-flex tw-items-center">
          <div class="tw-font-medium tw-text-sm tw-w-[50%]">
            <div class="tw-flex tw-justify-around tw-items-end tw-w-full">
              <div>
                <KeyBoardTips
                  color="purple"
                  keyLabel="Alt"
                />
                <div class="tw-flex">
                  Hold:&nbsp;<span class="tw-font-bold tw-text-purple-500"
                    >Alt <i class="fa-brands fa-windows"></i
                  ></span>
                </div>
              </div>
              <span>/</span>
              <div>
                <KeyBoardTips
                  color="purple"
                  keyIcon="Option"
                />
                <div class="tw-flex">
                  <span class="tw-font-bold tw-text-purple-500"
                    >Option <i class="fa-brands fa-apple"></i
                  ></span>
                </div>
              </div>
            </div>
          </div>
          <i class="pi pi-plus"></i>
          <div class="tw-font-medium tw-text-sm tw-w-[50%]">
            <div class="tw-flex tw-justify-around tw-items-end tw-w-full">
              <div>
                <KeyBoardTips
                  color="purple"
                  keyIcon="pi pi-arrow-up"
                  :secondary="true"
                />
                <div class="tw-flex">
                  Keypress:&nbsp;<span class="tw-font-bold tw-text-purple-500"
                    >Up</span
                  >
                </div>
              </div>
              <span>/</span>
              <div class="tw-flex tw-flex-col tw-items-center">
                <KeyBoardTips
                  color="purple"
                  keyIcon="pi pi-arrow-down"
                  :secondary="true"
                />
                <div class="tw-flex">
                  <span class="tw-font-bold tw-text-purple-500">Down</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <p class="tw-text-sm tw-font-medium tw-text-center">
          Scroll Up or Scroll Down
        </p>
      </div>
    </Panel>
  </div>
</template>

<script lang="ts" setup>
import Panel from 'primevue/panel'
import Divider from 'primevue/divider'
import KeyBoardTips from './KeyBoardTips.vue'
</script>
