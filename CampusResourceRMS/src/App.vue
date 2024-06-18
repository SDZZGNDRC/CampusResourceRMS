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
      <Login @update:isLogin="updateIsLogin" @update:user_id="updateUserID" />
    </v-container>
    <router-view v-if="isLogin" :user-id="user_id.value"></router-view>
  </v-app>
</template>

<script setup>
import { ref, provide } from 'vue';
import Login from './components/Login.vue';
const isLogin = ref(false);
const user_id = ref('');

provide('user_id', user_id);

const updateIsLogin = (value) => {
  isLogin.value = value;
};

const updateUserID = (value) => {
  user_id.value = value;
  console.log(user_id.value);
};
</script>

<style scoped>
/* 样式 */
</style>
