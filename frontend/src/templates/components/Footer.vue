<template>
  <div class="tw-z-10">
    <Menubar class="tw-border-0 tw-w-full" :pt="{ root: 'tw-bg-primary-900 tw-h-[10vh]' }">
      <template #start>
        <div class="tw-text-white tw-text-sm">
          <!-- E. Khramtsova, T. Leelanupab, S. Zhuang, M. Baktashmotlagh and G. Zuccon; Embark on
          DenseQuest: A System for Selecting the Best Dense Retriever for a Custom Collection;<br />In
          Proceedings of the 2024 ACM SIGIR Conference on Research and Development in Information
          Retrieval, SIGIR 2024, Washington D.C., USA (Accessible via the following
          <a href="https://arxiv.org/pdf/2407.06685" target="_blank" class="tw-text-white">link</a>) -->
        </div>
      </template>
      <template #end>
        <div class="tw-flex tw-bg-white tw-w-full">
          <img :src="ieLab" width="45" height="45" />
          <img :src="queenLand" width="45" height="45" />
        </div>
      </template>
    </Menubar>
  </div>
</template>
<script lang="ts" setup>
import Menubar from "primevue/menubar";
import ieLab from "@/assets/icons/ielab-page001.png";
import queenLand from "@/assets/icons/UQ-300x300.png";
</script>
