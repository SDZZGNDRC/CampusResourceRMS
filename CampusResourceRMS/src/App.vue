<!-- App.vue -->
<template>
  <v-app>
    <v-tabs centered bg-color="primary">
      <v-tab to="/home">Home</v-tab>
      <v-tab to="/about">About</v-tab>
      <v-tab to="/userdashboard">User Dashboard</v-tab>
    </v-tabs>
    <!-- 在此处添加一个选项卡（tabs），当对应的tab被点击时，router-view自动渲染对应的组件。 -->
    <v-main class="d-flex align-center justify-center">
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script setup>
  //
</script>

<style scoped>
.align-center {
  align-items: center;
}

.justify-center {
  justify-content: center;
}

.d-flex {
  display: flex;
}
</style>
