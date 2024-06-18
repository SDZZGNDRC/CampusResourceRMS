<!-- MyRecords.vue -->
<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <!-- 展示结果 -->
        <v-data-table :headers="headers" :items="results" items-per-page="7" items-per-page-text="每页显示">
          <template v-slot:item.status="{ value }">
            <v-chip :color="get_status_color(value)">
              {{ value }}
            </v-chip>
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn class="me-2" color="red" size="small" @click="">取消</v-btn>
          </template>
          <template v-slot:no-data>
            <v-card-text>
              没有相关记录
            </v-card-text>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
  </v-container>
</template>


<script>
import { ref, onMounted, inject } from 'vue';
import axios from 'axios';

export default {
  setup() {
    const userId = inject('user_id');

    const headers = [
      // { title: '预约ID', align: 'start', key: 'reservation_id' },
      { title: '资源名称', align: 'start', key: 'resource_name' },
      { title: '开始时间', key: 'start_time' },
      { title: '结束时间', key: 'end_time' },
      { title: '描述', key: 'description', sortable: false },
      { title: '公开预约', key: 'public', sortable: false },
      { title: '预约状态', key: 'status', sortable: false },
    ];
    const results = ref([]);

    const get_status_color = (value) => {
      switch (value) {
        case '审核中':
          return 'red';
        case '审核通过':
          return 'green';
        case '已完成':
          return 'blue';
        default:
          return 'grey';
      }
    };

    onMounted(() => {
      axios.get('http://127.0.0.1:5000/get-my-reservations', {
        params: {
          userID: userId.value
        }
      })
      .then(response => {
        results.value = response.data.reservations;
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });
    });

    return {
      headers,
      results,
      userId,
      get_status_color,
    };
  }
};
</script>
