<template>
  <v-container>
    <v-data-table
      :headers="headers"
      :items="reservations"
      items-per-page="7"
      items-per-page-text="每页显示"
    >
      <!-- <template v-slot:top>
        <v-toolbar flat>
          <v-toolbar-title>近期的预约活动</v-toolbar-title>
        </v-toolbar>
      </template> -->
      <template v-slot:item.start_time="{ item }">
        {{ new Date(item.start_time).toLocaleString() }}
      </template>
      <template v-slot:item.end_time="{ item }">
        {{ new Date(item.end_time).toLocaleString() }}
      </template>
    </v-data-table>
  </v-container>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import axios from 'axios';

export default {
  setup() {
    const headers = [
      { title: '资源名称', key: 'resource_name' },
      { title: '开始时间', key: 'start_time' },
      { title: '结束时间', key: 'end_time' },
      { title: '申请人', key: 'user_name', sortable: false },
      { title: '描述', key: 'description', sortable: false },
    ];

    const reservations = ref([]);

    const fetchRecentReservations = () => {
      axios.get('http://127.0.0.1:5000/get-recent-reservations')
        .then(response => {
          reservations.value = response.data.reservations;
          console.log(reservations.value);
        })
        .catch(error => {
          console.error('Error fetching recent reservations:', error);
        });
    };

    onMounted(() => {
      fetchRecentReservations();
    });

    return {
      headers,
      reservations,
    };
  },
};
</script>

<style>
</style>
