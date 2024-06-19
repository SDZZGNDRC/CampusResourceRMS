<!-- MyRecords.vue -->
<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <!-- 展示结果 -->
        <v-data-table :headers="headers" :items="results" items-per-page="10" items-per-page-text="每页显示">
          <template v-slot:item.status="{ value }">
            <v-chip :color="get_status_color(value)">
              {{ value }}
            </v-chip>
          </template>
          <template v-slot:item.duration="{ value }">
            {{ value }}
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn 
              :disabled="item.status !== '审核中'" 
              class="me-2" 
              :color="item.status !== '审核中' ? '' : 'red'" 
              size="small" 
              @click="cancelReservation(item)"
            >
              撤销
            </v-btn>
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
      { title: '资源名称', align: 'start', key: 'resource_name' },
      { title: '开始时间', key: 'start_time' },
      { title: '结束时间', key: 'end_time' },
      { title: '持续时间', key: 'duration', sortable: false },
      { title: '描述', key: 'description', sortable: false },
      { title: '公开预约', key: 'public', sortable: false },
      { title: '预约状态', key: 'status', sortable: false },
      { title: '操作', key: 'actions', sortable: false },
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

    const cancelReservation = (item) => {
      axios.get('http://127.0.0.1:5000/cancel-reserve', {
        params: {
          userID: userId.value,
          reservation_id: item.reservation_id
        }
      })
      .then(response => {
        axios.get('http://127.0.0.1:5000/get-my-reservations', {
          params: {
            userID: userId.value
          }
        })
        .then(response => {
          results.value = response.data.reservations.map(reservation => {
            const startTime = new Date(reservation.start_time);
            const endTime = new Date(reservation.end_time);
            const durationInMinutes = (endTime - startTime) / (1000 * 60); // 计算持续时间（分钟）
            const hours = Math.floor(durationInMinutes / 60);
            const minutes = durationInMinutes % 60;

            return {
              ...reservation,
              actions: '', // Add actions property to each reservation
              duration: `${hours}小时${minutes}分钟`
            };
          });
        })
        .catch(error => {
          console.error('Error fetching updated data:', error);
        });
      })
      .catch(error => {
        console.error('Error canceling reservation:', error);
      });
    };


    onMounted(() => {
      axios.get('http://127.0.0.1:5000/get-my-reservations', {
        params: {
          userID: userId.value
        }
      })
      .then(response => {
        results.value = response.data.reservations.map(reservation => {
          const startTime = new Date(reservation.start_time);
            const endTime = new Date(reservation.end_time);
            const durationInMinutes = (endTime - startTime) / (1000 * 60); // 计算持续时间（分钟）
            const hours = Math.floor(durationInMinutes / 60);
            const minutes = durationInMinutes % 60;

            return {
              ...reservation,
              actions: '', // Add actions property to each reservation
              duration: `${hours}小时${minutes}分钟`
            };
        });
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
      cancelReservation,
    };
  }
};
</script>
