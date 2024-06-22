<!-- App.vue -->
<template>
  <v-app>
    <v-tabs align-tabs="center" centered bg-color="primary" v-if="isLogin">
      <v-tab v-for="tab in tabsToShow" :key="tab.to" :to="tab.to">{{ tab.label }}</v-tab>
    </v-tabs>
    <v-container v-if="!isLogin">
      <Login 
        @update:isLogin="updateIsLogin" 
        @update:user_id="updateUserID" 
        @update:role_id="updateRoleID" 
      />
    </v-container>
    <router-view v-if="isLogin" :user-id="user_id.value"></router-view>
  </v-app>
</template>

<script setup>
import { ref, provide } from 'vue';
import Login from './components/Login.vue';
const isLogin = ref(false);
const user_id = ref('');
const role_id = ref('');
const tabsToShow = ref([]);

provide('user_id', user_id);

const updateIsLogin = (value) => {
  isLogin.value = value;
};

const updateUserID = (value) => {
  user_id.value = value;
  console.log(user_id.value);
};

const updateRoleID = (value) => {
  role_id.value = value;
  switch (value) {
    case 0:
      tabsToShow.value = [
        { to: '/recent-activities', label: '最近活动'},
        { to: '/user-manager', label: '用户管理' },
        { to: '/resource-manager', label: '资源管理' },
        { to: '/reservation-manager', label: '预约管理' },
        { to: 'statistics', label: '使用统计'},
      ]
      break;
    case 1:
      tabsToShow.value = [
        { to: '/recent-activities', label: '最近活动'},
        { to: '/search', label: '预约资源' },
        { to: '/my-records', label: '我的记录' },
      ]
      break;
    case 2:
      tabsToShow.value = [
        { to: '/recent-activities', label: '最近活动'},
        { to: '/search', label: '预约资源' },
        { to: '/my-records', label: '我的记录' },
      ]
      break;
    default:
      break;
  }
};

</script>

<style scoped>
/* 样式 */
</style>
