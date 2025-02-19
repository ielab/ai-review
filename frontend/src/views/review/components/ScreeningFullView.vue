<template>
  <Dialog
    v-model:visible="dialogVisible"
    modal
    class="tw-w-[95%]"
  >
    <template #container>
      <div
        ref="autoScrollTarget"
        class="tw-rounded-t-lg tw-flex tw-min-h-[81.5vh] tw-overflow-y-auto"
        :class="isCompleteReview ? 'tw-bg-purple-50' : 'tw-bg-white'"
      >
        <!-- previous article button -->
        <div
          class="tw-absolute tw-top-[-1.75rem] tw-left-1/2 tw-translate-x-[-50%]"
          @click="prevDoc()"
        >
          <i class="fa-solid fa-chevron-up tw-text-white tw-cursor-pointer"></i>
        </div>

        <!-- next article button -->
        <div
          class="tw-absolute tw-bottom-[-1.75rem] tw-left-1/2 tw-translate-x-[-50%]"
          @click="nextDoc()"
        >
          <i
            class="fa-solid fa-chevron-down tw-text-white tw-cursor-pointer"
          ></i>
        </div>

        <!-- shadow at bottom -->
        <div
          class="tw-text-center tw-bottom-[3.3rem] tw-absolute tw-w-full tw-bg-gradient-to-t tw-from-black/5 tw-h-[2.5rem]"
        ></div>

        <!-- title, authors, pmid, ranking section -->
        <div class="tw-w-[25%]">
          <div
            class="tw-w-[25%] tw-pl-6 tw-py-6 tw-fixed tw-h-[calc(100%-3.8rem)]"
          >
            <div class="tw-flex tw-flex-col tw-justify-between tw-h-full">
              <div>
                <p class="tw-text-2xl tw-font-bold">
                  {{ article.title }}
                </p>
                <div class="tw-flex tw-flex-wrap tw-gap-x-2 tw-my-2">
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
            </div>
          </div>
        </div>

        <!-- abstract section -->
        <div class="tw-w-[50%] tw-gap-y-2 tw-px-6 tw-pt-6">
          <div
            v-if="extractSections(article.abstract)"
            class="tw-flex tw-flex-col tw-gap-y-3 tw-pb-6"
          >
            <p v-for="section in extractSections(article.abstract)">
              <span class="tw-font-medium">{{ section.header }}:</span>
              {{ section.content }}
            </p>
          </div>
          <p v-else>{{ article.abstract }}</p>
        </div>

        <!-- keyboard guide panel section -->
        <div class="tw-relative">
          <KeyBoardGuidePanel />
        </div>
      </div>

      <!-- footer section -->
      <div
        class="tw-bg-white tw-flex tw-justify-between tw-px-6 tw-py-3 tw-rounded-b-lg"
      >
        <div class="tw-flex tw-w-full tw-justify-between tw-items-end">
          <p>
            Doc <b>{{ docIndex + 1 }}</b> of <b>25</b> in Page 3
          </p>
          <div class="tw-flex tw-gap-x-8">
            <Button
              :pt="{ root: 'tw-py-[0.2rem] tw-w-[16rem]' }"
              icon="fa-solid fa-xmark"
              label="Exclude"
              severity="danger"
              @click="review('exclude')"
              :style="getActiveStyle('exclude')"
            />
            <Button
              :pt="{ root: 'tw-py-[0.2rem] tw-w-[16rem]' }"
              icon="fa-solid fa-question"
              label="Maybe"
              severity="secondary"
              @click="review('maybe')"
              :style="getActiveStyle('maybe')"
            />
            <Button
              :pt="{ root: 'tw-py-[0.2rem] tw-w-[16rem]' }"
              icon="fa-solid fa-check"
              label="Include"
              severity="success"
              @click="review('include')"
              :style="getActiveStyle('include')"
            />
          </div>
          <p>Page <b>3</b> of <b>8</b></p>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script lang="ts" setup>
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import KeyBoardGuidePanel from './KeyBoardGuidePanel.vue'
import articles from '../configs/data.json'
import { ref, computed, onMounted } from 'vue'

const props = defineProps<{
  fullView: boolean
  index: number
}>()

const isCompleteReview = ref(false)
const feedback = ref()
const article = ref()
const docIndex = ref<number>(props.index)

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
  | 'ArrowUp'
  | 'ArrowDown'
  | 'ArrowLeft'
  | 'm'
  | 'ArrowRight'
  | 'Alt+ArrowLeft'
  | 'Alt+m'
  | 'Alt+ArrowRight'
  | 'Alt+ArrowDown'
  | 'Alt+ArrowUp'

const keyMappings: Record<KeyCombo, () => void> = {
  ArrowUp: () => prevDoc(),
  ArrowDown: () => nextDoc(),
  ArrowLeft: () => review('exclude'),
  m: () => review('maybe'),
  ArrowRight: () => review('include'),
  // composite keys
  'Alt+ArrowLeft': () => {
    review('exclude')
    setTimeout(() => nextDoc(), 500) // Pass function reference to setTimeout
  },
  'Alt+m': () => {
    review('maybe')
    setTimeout(() => nextDoc(), 500)
  },
  'Alt+ArrowRight': () => {
    review('include')
    setTimeout(() => nextDoc(), 500)
  },
  'Alt+ArrowDown': () => {
    scrollDown()
  },
  'Alt+ArrowUp': () => {
    scrollTop()
  },
}

window.addEventListener('keydown', (e) => {
  let combo: KeyCombo | null = null

  // Detect Alt + specific key combinations
  if (
    e.altKey &&
    ['m', 'ArrowLeft', 'ArrowRight', 'ArrowDown', 'ArrowUp'].includes(e.key)
  ) {
    e.preventDefault()
    combo = `Alt+${e.key}` as KeyCombo
  }
  // Detect single key presses
  else if (
    ['ArrowUp', 'ArrowDown', 'm', 'ArrowLeft', 'ArrowRight'].includes(e.key)
  ) {
    e.preventDefault()
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

function scrollToTop() {
  const scrollTarget = autoScrollTarget.value as HTMLElement
  scrollTarget.scrollTop = 0
}

function prevDoc() {
  if (docIndex.value - 1 >= 0 && props.fullView) {
    docIndex.value = docIndex.value - 1
    initArticle()
    scrollToTop()
  }
}

function nextDoc() {
  if (docIndex.value + 1 <= 24 && props.fullView) {
    docIndex.value = docIndex.value + 1
    isCompleteReview.value = false
    initArticle()
    scrollToTop()
  }
}

function initArticle() {
  article.value = articles[docIndex.value]
}

const autoScrollTarget = ref<HTMLElement | null>(null)

function scrollDown() {
  const scrollTarget = autoScrollTarget.value as HTMLElement
  const startPosition = scrollTarget.scrollTop
  const maxScrollPosition =
    scrollTarget.scrollHeight - scrollTarget.clientHeight

  if (startPosition < maxScrollPosition) {
    const scrollAmount = scrollTarget.clientHeight / 4
    const targetPosition = Math.min(
      startPosition + scrollAmount,
      maxScrollPosition,
    )

    let startTime: number | null = null

    function animation(currentTime: number) {
      if (startTime === null) startTime = currentTime
      const timeElapsed = currentTime - startTime
      const run = ease(
        timeElapsed,
        startPosition,
        targetPosition - startPosition,
        500,
      ) // Adjust duration if needed
      scrollTarget.scrollTop = run

      if (timeElapsed >= 500) {
        scrollTarget.scrollTop = targetPosition
      } else {
        requestAnimationFrame(animation)
      }
    }

    function ease(t: number, b: number, c: number, d: number) {
      t /= d / 2
      if (t < 1) return (c / 2) * t * t + b
      t--
      return (-c / 2) * (t * (t - 2) - 1) + b
    }

    requestAnimationFrame(animation)
  }
}

function scrollTop() {
  const scrollTarget = autoScrollTarget.value as HTMLElement
  const startPosition = scrollTarget.scrollTop
  const scrollAmount = scrollTarget.clientHeight / 4

  if (startPosition > 0) {
    const targetPosition = Math.max(startPosition - scrollAmount, 0)

    let startTime: number | null = null

    function animation(currentTime: number) {
      if (startTime === null) startTime = currentTime
      const timeElapsed = currentTime - startTime
      const run = ease(
        timeElapsed,
        startPosition,
        targetPosition - startPosition,
        500,
      ) // Adjust duration
      scrollTarget.scrollTop = run

      if (timeElapsed >= 500) {
        scrollTarget.scrollTop = targetPosition
      } else {
        requestAnimationFrame(animation)
      }
    }

    function ease(t: number, b: number, c: number, d: number) {
      t /= d / 2
      if (t < 1) return (c / 2) * t * t + b
      t--
      return (-c / 2) * (t * (t - 2) - 1) + b
    }

    requestAnimationFrame(animation)
  }
}

onMounted(() => {
  initArticle()
})
</script>
