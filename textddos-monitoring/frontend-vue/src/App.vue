<template>
  <div>
    <!-- <login-view>
      <RouterView />
    </login-view> -->
    <main-view>
      <RouterView />  
    </main-view>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { RouterView } from 'vue-router';
import LoginView from './pages/LoginView.vue';
import Mainview from './pages/MainView.vue';

</script>
