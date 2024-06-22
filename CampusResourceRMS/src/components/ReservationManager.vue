<!-- MyRecords.vue -->
<template>
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-text-field
            v-model="search"
            label="过滤"
            prepend-inner-icon="mdi-magnify"
            variant="outlined"
            hide-details
            single-line
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <!-- 展示结果 -->
          <v-data-table 
            :headers="headers" 
            :items="results" 
            items-per-page="8" 
            items-per-page-text="每页显示"
            :search="search"
          >
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
                :color="item.status !== '审核中' ? '' : 'blue'" 
                size="small" 
                @click="updateReservation(item, '审核通过')"
              >
                通过
              </v-btn>
              <v-btn 
                :disabled="item.status !== '审核中'" 
                class="me-2" 
                :color="item.status !== '审核中' ? '' : 'red'" 
                size="small" 
                @click="updateReservation(item, '审核不通过')"
              >
                拒绝
              </v-btn>
            </template>
            <template v-slot:no-data>
              <v-card-text>
                没有相关记录
              </v-card-text>
            </template>
          </v-data-table>
          <v-dialog v-model="confirmDialog" max-width="500px">
            <v-card>
              <v-card-title class="headline">确认审核通过</v-card-title>
              <v-card-text>
                该预约与以下预约存在冲突:
                <ul>
                  <li v-for="id in conflictingReservationIds" :key="id">预约编号: {{ id }}</li>
                </ul>
                是否确认审核通过? 如果通过该预约，和它冲突的预约将被拒绝。
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="blue darken-1" text @click="confirmDialog = false">取消</v-btn>
                <v-btn color="blue darken-1" text @click="confirmUpdate">确认</v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
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
        { title: '预约ID', align: 'start', key: 'reservation_id' },
        { title: '资源名称', align: 'start', key: 'resource_name' },
        { title: '申请人', key: 'username' },
        { title: '开始时间', key: 'start_time' },
        { title: '结束时间', key: 'end_time' },
        { title: '持续时间', key: 'duration', sortable: false },
        { title: '描述', key: 'description', sortable: false },
        { title: '预约状态', key: 'status', sortable: false },
        { title: '操作', key: 'actions', sortable: false },
      ];

      const search = ref('');
      const results = ref([]);
  
      const get_status_color = (value) => {
        switch (value) {
          case '审核中':
            return 'red';
          case '审核通过':
            return 'green';
          case '已完成':
            return 'blue';
          case '审核不通过':
            return 'orange';
          default:
            return 'grey';
        }
      };

      const confirmDialog = ref(false);
      const conflictingReservationIds = ref([]);
      const selectedItem = ref(null);
      const selectedStatus = ref('');

      const updateReservation = (item, s) => {
        if (s === '审核通过') {
          axios.get('http://127.0.0.1:5000/is-conflict', {
            params: {
              reservation_id: item.reservation_id
            }
          })
          .then(response => {
            if (response.data.status === 'no_conflict') {
              performUpdate(item, s);
            } else if (response.data.status === 'conflict') {
              selectedItem.value = item;
              selectedStatus.value = s;
              conflictingReservationIds.value = response.data.conflicting_reservation_ids;
              confirmDialog.value = true;
            }
          })
          .catch(error => {
            console.error('Error checking conflict:', error);
          });
        } else {
          performUpdate(item, s);
        }
      };

      const confirmUpdate = () => {
        confirmDialog.value = false;

        // 更新其余与当前预约发生冲突的预约状态为`审核不通过`
        axios.post('http://127.0.0.1:5000/update-conflicting-reservations', {
          reservation_ids: conflictingReservationIds.value,
          status: '审核不通过',
        })
        .then(response => {
          // 更新当前预约的状态为所选的状态
          performUpdate(selectedItem.value, selectedStatus.value);
        })
        .catch(error => {
          console.error('Error updating conflicting reservations:', error);
        });
      };

      const performUpdate = (item, s) => {
        axios.post('http://127.0.0.1:5000/update-reservation', {
          reservation_id: item.reservation_id,
          status: s,
        })
        .then(response => {
          axios.get('http://127.0.0.1:5000/get-my-reservations', {
            params: {
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
          console.log(results.value)
        })
        .catch(error => {
          console.error('Error fetching data:', error);
        });
      });
  
      return {
        confirmDialog,
        conflictingReservationIds,
        selectedItem,
        selectedStatus,
        confirmUpdate,
        headers,
        search,
        results,
        userId,
        get_status_color,
        updateReservation,
      };
    }
  };
  </script>
  