<!-- App.vue -->
<template>
  <v-app>
    <v-tabs centered bg-color="primary" v-if="isLogin">
      <v-tab to="/test">Test</v-tab>
      <v-tab to="/userdashboard">User Dashboard</v-tab>
      <v-tab to="/search">预约资源</v-tab>
      <v-tab to="/my-records">我的记录</v-tab>
      <v-tab to="/auto-schedule-course">自动排课</v-tab>
    </v-tabs>
    <v-container v-if="!isLogin">
      <Login @update:isLogin="updateIsLogin" />
    </v-container>
    <router-view v-if="isLogin"></router-view>
  </v-app>
</template>

<script setup>
import { ref } from 'vue';
import Login from './components/Login.vue';
const isLogin = ref(false);

const updateIsLogin = (value) => {
  isLogin.value = value;
  console.log(isLogin.value);
};
</script>

<style scoped>
/* 样式 */
</style>
