<template>
  <Dialog
    v-model:visible="dialogVisible"
    modal
    class="tw-w-[75vw]"
    :pt="{
      header: 'tw-p-1 tw-py-0',
      content: isCompleteReview
        ? 'tw-py-4 tw-px-10 tw-text-black tw-bg-purple-100'
        : 'tw-text-black tw-py-4 tw-px-10',
      footer: isCompleteReview
        ? 'tw-p-0 tw-px-1 tw-text-black tw-bg-purple-100'
        : 'tw-p-0 tw-px-1',
    }"
  >
    <template #header>
      <div
        class="tw-w-full tw-p-1 tw-flex tw-flex-col tw-items-center tw-justify-start"
      >
        <div class="tw-flex tw-gap-4">
          <Button
            :pt="{
              root: 'tw-bg-transaparent tw-h-3 tw-w-6',
              icon: 'tw-text-xl',
            }"
            icon="pi pi-angle-left"
            text
            rounded
            @click="prevDoc"
            :disabled="docIndex == 0 ? true : false"
            :severity="docIndex == 0 ? 'secondary' : undefined"
          />
          <div class="tw-text-center">
            Doc
            <span class="tw-font-bold">{{ docIndex + 1 }}</span> of
            <span class="tw-font-bold">25</span> in page
            <span class="tw-font-bold">3</span>
          </div>
          <Button
            :pt="{ root: 'tw-h-3 tw-w-6', icon: 'tw-text-xl' }"
            icon="pi pi-angle-right"
            text
            rounded
            @click="nextDoc"
            :disabled="docIndex == 24 ? true : false"
            :severity="docIndex == 24 ? 'secondary' : undefined"
          />
        </div>
        <p class="tw-absolute tw-right-10">
          (Page <span class="tw-font-bold">3</span> of
          <span class="tw-font-bold">8</span>)
        </p>
      </div>
    </template>

    <div class="tw-flex">
      <div class="tw-mx-[12rem]">
        <div class="tw-px-3 tw-flex tw-flex-col tw-gap-y-1">
          <p class="tw-text-2xl tw-font-bold">
            {{ article.title }}
          </p>
          <div class="tw-flex tw-flex-wrap tw-gap-x-2">
            <span
              class="tw-text-purple-500 tw-font-medium"
              v-for="(au, index) in article.authors"
              :key="index"
            >
              {{ au.split(', ')[1] }} {{ au.split(', ')[0]
              }}<span v-if="index != article.authors.length - 1">; </span>
            </span>
          </div>
          <p class="tw-text-slate-500">pmid: {{ article.id }}</p>
        </div>
        <Divider class="tw-my-3" />
        <!--  -->
        <div class="tw-flex tw-gap-x-10 tw-px-3 tw-justify-center">
          <div class="tw-w-full">
            <p class="tw-font-bold tw-mb-3 tw-text-xl">Abstract</p>
            <div
              v-if="extractSections(article.abstract)"
              class="tw-flex tw-flex-col tw-gap-y-3"
            >
              <p v-for="section in extractSections(article.abstract)">
                <span class="tw-font-medium">{{ section.header }}:</span>
                {{ section.content }}
              </p>
            </div>
            <p v-else>{{ article.abstract }}</p>
          </div>
        </div>
      </div>
      <div
        class="tw-flex tw-flex-col tw-gap-y-2 tw-w-[12rem] tw-absolute tw-right-10 tw-top-[50%] tw-translate-y-[-50%]"
      >
        <Button
          :pt="{ root: 'tw-py-2' }"
          icon="pi pi-thumbs-up"
          label="Include"
          severity="success"
          @click="review('include')"
          :style="getActiveStyle('include')"
        />
        <Button
          :pt="{ root: 'tw-py-2' }"
          icon="pi pi-question"
          label="Maybe"
          severity="secondary"
          @click="review('maybe')"
          :style="getActiveStyle('maybe')"
        />
        <Button
          :pt="{ root: 'tw-py-2' }"
          icon="pi pi-thumbs-down"
          label="Exclude"
          severity="danger"
          @click="review('exclude')"
          :style="getActiveStyle('exclude')"
        />
      </div>
    </div>

    <template #footer>
      <div class="tw-flex tw-justify-center tw-items-center">
        <Accordion
          @tab-open="setShowKeyboardSuport(true)"
          @tab-close="setShowKeyboardSuport(false)"
          :activeIndex="Number(getShowKeyboardSuport)"
          expandIcon="pi pi-chevron-up"
          collapseIcon="pi pi-chevron-down"
          class="tw-w-full"
          iconPos="endVal"
        >
          <AccordionTab
            :pt="{
              headerAction:
                'tw-py-1 tw-flex tw-justify-between tw-flex-row-reverse',
              content: 'tw-p-2',
            }"
          >
            <template #header>
              <div class="tw-flex tw-items-center tw-gap-x-2">
                <i class="fa-regular fa-keyboard"></i>
                <p>Keyboard Support</p>
              </div>
            </template>
            <div class="tw-flex tw-gap-x-2">
              <Panel
                header="Control Keys"
                :pt="{ header: 'tw-py-2', content: 'tw-p-2' }"
                class="tw-w-[33%]"
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
                    keyIcon="pi pi-arrow-left"
                    keyLabel="Left"
                    event="Keypress"
                    for="Previous"
                  />
                  <KeyBoardTips
                    color="purple"
                    keyIcon="pi pi-arrow-right"
                    keyLabel="Right"
                    event="Keypress"
                    for="Next"
                  />
                </div>
              </Panel>
              <Panel
                header="Assessment Keys"
                :pt="{ header: 'tw-py-2', content: 'tw-p-2' }"
                class="tw-w-[33%]"
              >
                <div class="tw-flex tw-justify-around">
                  <KeyBoardTips
                    color="green"
                    keyIcon="pi pi-arrow-up"
                    keyLabel="Up"
                    event="Keypress"
                    for="Include"
                  />
                  <KeyBoardTips
                    color="slate"
                    keyLabel="M"
                    event="Keypress"
                    for="Maybe"
                  />
                  <KeyBoardTips
                    color="red"
                    keyIcon="pi pi-arrow-down"
                    keyLabel="Down"
                    event="Keypress"
                    for="Exclude"
                  />
                </div>
              </Panel>
              <Panel
                header="Composite Keys"
                :pt="{ header: 'tw-py-2', content: 'tw-p-2' }"
                class="tw-w-[33%]"
              >
                <div
                  class="tw-flex tw-justify-around tw-items-center tw-w-full"
                >
                  <div class="tw-font-medium tw-text-sm">
                    <div
                      class="tw-flex tw-justify-around tw-items-end tw-w-full"
                    >
                      <div>
                        <KeyBoardTips
                          color="purple"
                          keyLabel="Alt"
                        />
                        <div class="tw-flex">
                          Hold:&nbsp;<span
                            class="tw-font-bold tw-text-purple-500"
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
                    Assessment and Move to Next
                  </div>
                  <i class="pi pi-plus"></i>
                  <p class="tw-font-medium">Assessment Key</p>
                </div>
              </Panel>
            </div>
          </AccordionTab>
        </Accordion>
      </div>
    </template>
  </Dialog>
</template>

<script lang="ts" setup>
import Dialog from 'primevue/dialog'
import Accordion from 'primevue/accordion'
import AccordionTab from 'primevue/accordiontab'
import KeyBoardTips from './KeyBoardTips.vue'
import Button from 'primevue/button'
import Panel from 'primevue/panel'
import articles from '../configs/data.json'
import Divider from 'primevue/divider'
import { ref, computed } from 'vue'

const props = defineProps<{
  fullView: boolean
  index: number
}>()

const isCompleteReview = ref(false)
const feedback = ref()
const article = ref()
const docIndex = ref<number>(props.index)
const getShowKeyboardSuport = ref()

function initShowKeyboardSuport() {
  getShowKeyboardSuport.value = localStorage.getItem('showKeyboardSuport')
}

initShowKeyboardSuport()

function setShowKeyboardSuport(value: boolean) {
  if (value) {
    localStorage.setItem('showKeyboardSuport', '0')
  } else {
    localStorage.setItem('showKeyboardSuport', '1')
  }
  initShowKeyboardSuport()
}

function review(value: string) {
  if (props.fullView) {
    if (isCompleteReview.value && feedback.value == value) {
      feedback.value = ''
      isCompleteReview.value = false
    } else {
      feedback.value = value
      isCompleteReview.value = true
    }
  }
}

const emit = defineEmits(['update:fullView'])

const dialogVisible = computed({
  get: () => props.fullView,
  set: (value: boolean) => emit('update:fullView', value),
})

const includeStyle =
  'box-shadow: #dcfce7 0px 0px 0px 2px, #4ade80 0px 0px 0px 4px'
const maybeStyle =
  'box-shadow: #f1f5f9 0px 0px 0px 2px, #94a3b8 0px 0px 0px 4px'
const excludeStyle =
  'box-shadow: #fecaca 0px 0px 0px 2px, #f87171 0px 0px 0px 4px'

function getActiveStyle(value: 'include' | 'maybe' | 'exclude') {
  const styleMap = {
    include: includeStyle,
    maybe: maybeStyle,
    exclude: excludeStyle,
  }

  if (isCompleteReview.value) {
    if (feedback.value === value) {
      return styleMap[value]
    }
    return 'opacity: 40%'
  }
}

const judge = ref<string>('')

// -------------------------------------

type KeyCombo =
  | 'Alt+ArrowUp'
  | 'Alt+ArrowDown'
  | 'Alt+m'
  | 'ArrowUp'
  | 'ArrowDown'
  | 'm'
  | 'ArrowLeft'
  | 'ArrowRight'

const keyMappings: Record<KeyCombo, () => void> = {
  'Alt+ArrowUp': () => review('include'),
  'Alt+ArrowDown': () => review('exclude'),
  'Alt+m': () => review('maybe'),
  ArrowUp: () => review('include'),
  ArrowDown: () => review('exclude'),
  m: () => review('maybe'),
  ArrowLeft: () => prevDoc(),
  ArrowRight: () => nextDoc(),
}

window.addEventListener('keydown', (e) => {
  let combo: KeyCombo | null = null

  // Detect Alt + specific key combinations
  if (e.altKey && ['ArrowUp', 'ArrowDown', 'm'].includes(e.key)) {
    combo = `Alt+${e.key}` as KeyCombo
  }
  // Detect single key presses
  else if (
    ['ArrowUp', 'ArrowDown', 'm', 'ArrowLeft', 'ArrowRight'].includes(e.key)
  ) {
    combo = e.key as KeyCombo
  }

  if (combo && combo in keyMappings) {
    judge.value = combo
    keyMappings[judge.value as KeyCombo]()
    judge.value = ''
  }
})

function extractSections(abstract: string) {
  // Regular expression to match dynamic section headers followed by a colon and content
  const sectionRegex = /([A-Z][A-Z\s]*):\s*([\s\S]*?)(?=\s*[A-Z][A-Z\s]*:|$)/g
  const sections = []
  let match

  // Iterate through all matches
  while ((match = sectionRegex.exec(abstract)) !== null) {
    const sectionHeader = match[1].trim()
    const sectionContent = match[2].trim()
    sections.push({
      header: sectionHeader,
      content: sectionContent,
    })
  }

  if (sections.length > 0) return sections
  return null
}

function prevDoc() {
  if (docIndex.value - 1 >= 0 && props.fullView) {
    docIndex.value = docIndex.value - 1
    initArticle()
  }
}

function nextDoc() {
  if (docIndex.value + 1 <= 24 && props.fullView) {
    docIndex.value = docIndex.value + 1
    initArticle()
  }
}

function initArticle() {
  article.value = articles[docIndex.value]
}

initArticle()
</script>
