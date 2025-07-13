<template>
  <div class="tw-flex tw-flex-col tw-min-h-screen">
    <Navbar />
    <div class="tw-flex-1 tw-flex tw-flex-col">
      <div class="tw-flex-1 tw-flex tw-flex-col">
        <RouterView />
      </div>
      <Footer
        v-if="!['review', 'post-review'].includes(route.name?.toString() ?? '')"
      />
    </div>
  </div>
</template>


<script lang="ts" setup>
import Navbar from "./components/Navbar.vue";
import Footer from "./components/Footer.vue";

import { RouterView, useRoute } from "vue-router";
const route = useRoute();
</script>
