<template>
  <v-container>
    <v-row>
      <v-col cols="6" sm="6" md="6">
        <v-text-field
          label="搜索"
          v-model="search"
          append-inner-icon="mdi-magnify"
          single-line
          hide-details
          clearable 
        ></v-text-field>
      </v-col>
      <v-col cols="2" sm="2" md="2">
        <v-select
          :items="types"
          label="类型"
          v-model="type"
          clearable
        ></v-select>
      </v-col>
      <v-col cols="2" sm="2" md="2">
        <v-select
          :items="capacities"
          label="最大容量"
          v-model="capacity"
          clearable
        ></v-select>
      </v-col>
      <v-col cols="2" sm="2" md="2">
        <v-select
          :items="locations"
          label="位置"
          v-model="location"
          clearable
        ></v-select>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="6">
        <v-row align="center">
          <v-spacer></v-spacer>
          <v-col cols="3">
            <span class="mr-1">开始时间:</span>
          </v-col>
          <v-col cols="8">
            <VueDatePicker v-model="start_date" />
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="6">
        <v-row align="center">
          <v-spacer></v-spacer>
          <v-col cols="3">
            <span class="mr-1">结束时间:</span>
          </v-col>
          <v-col cols="8">
            <VueDatePicker v-model="end_date" />
          </v-col>
        </v-row>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <!-- 展示搜索结果(符合条件的记录) -->
        <v-data-table :headers="headers" :items="results" items-per-page="7" items-per-page-text="每页显示">
          <template v-slot:item.capacity="{ value }">
            <v-chip :color="get_capacity_color(value)">
              {{ value }}
            </v-chip>
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn class="me-2" color="green" size="small" @click="reserveItem(item)">预约</v-btn>
            <v-btn class="me-2" color="blue" size="small" @click="">查看</v-btn>
          </template>
          <template v-slot:no-data>
            <v-card-text>
              没有相关记录, 请检查你的搜索条件.
            </v-card-text>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
    <!-- 预约对话框 -->
    <v-dialog v-model="reserveDialog" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="text-h5">申请预约</span>
        </v-card-title>

        <v-card-text>
          <v-container v-if="reservedIndex > -1">
            <v-row>
              <v-col cols="12">
                <span>资源名称: {{ results[reservedIndex].name }}</span>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <span>资源位置和类型: {{ results[reservedIndex].location }} - {{ results[reservedIndex].type_name }}</span>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <span>开始时间: {{ formatDateTime(reservedItem.start_time) }}</span>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <span>结束时间: {{ formatDateTime(reservedItem.end_time) }}</span>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <span>预约总时长: {{ calculateDuration(reservedItem.start_time, reservedItem.end_time) }}</span>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <v-textarea 
                  v-model="reservedItem.description" 
                  clearable 
                  variant="outlined"
                  label="请输入预约该资源的原因" 
                  :rules="[v => !!v || '描述信息是必填项']"
                  error-messages="描述信息是必填项"
                  rows="3"></v-textarea>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <v-checkbox v-model="reservedItem.public" label="公开预约"></v-checkbox>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue-darken-1" @click="close"> 取消 </v-btn>
          <v-btn color="blue-darken-1" @click="reserve"> 确认 </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>


    <!-- TODO: 查看对话框 -->
  </v-container>
</template>

<script>
import { ref, watch, onMounted, inject } from 'vue';
import axios from 'axios';

export default {
  setup() {
    const userId = inject('user_id');
    const search = ref('');
    const type = ref(null);
    const capacity = ref(null);
    const location = ref(null);
    const types = ref([]);
    const capacities = ref([]);
    const locations = ref([]);
    const results = ref([]);
    const start_date = ref(new Date());
    const end_date = ref(new Date(start_date.value.getTime() + 2 * 60 * 60 * 1000)); // 加2小时
    const reserveDialog = ref(false);
    const reservedIndex = ref(-1);
    const reservedItem = ref({
      resourceID: ref(null),
      start_time: ref(null),
      end_time: ref(null),
      description: ref(''),
      public: ref(true),
    });
    const defaultItem = {
      resourceID: ref(null),
      start_time: ref(null),
      end_time: ref(null),
      description: ref(''),
      public: ref(true),
    };
    

    const headers = [
      { title: '资源ID', align: 'start', key: 'resource_id' },
      { title: '名称', key: 'name' },
      { title: '描述', key: 'description' },
      { title: '位置', key: 'location' },
      { title: '容量', key: 'capacity' },
      { title: '类型', key: 'type_name' },
      { title: '操作', key: 'actions', sortable: false },
    ];

    const fetchResults = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/search', {
          params: {
            name: search.value,
            type: type.value,
            capacity: capacity.value,
            location: location.value,
            start_date: start_date.value,
            end_date: end_date.value,
          }
        });

        results.value = response.data.resources;
      } catch (error) {
        console.error('搜索失败', error);
      }
    };

    watch([search, type, capacity, location, start_date, end_date], fetchResults, { immediate: true });

    const reserveItem = (item) => {
      reservedIndex.value = results.value.indexOf(item);
      reservedItem.value.resourceID = item.resource_id
      reservedItem.value.start_time = new Date(start_date.value)
      reservedItem.value.end_time = new Date(end_date.value)
      reserveDialog.value = true;
    };

    const close = () => {
      reserveDialog.value = false;
      reservedItem.value = { ...defaultItem };
      reservedIndex.value = -1;
    };

    const reserve = async () => {
      if (reservedIndex.value > -1) {
        try {
          console.log("userId:")
          console.log(userId.value)
          const response = await axios.post('http://127.0.0.1:5000/reserve', {
            resource_id: reservedItem.value.resourceID,
            start_time: reservedItem.value.start_time,
            end_time: reservedItem.value.end_time,
            description: reservedItem.value.description,
            public: reservedItem.value.public,
            user_id: userId.value,
          });

          if (response.data.status === 'success') {
            console.log('预约成功:', response.data.message);
            // 更新`results`
            await fetchResults();
          } else {
            console.error('预约失败:', response.data.message);
          }
        } catch (error) {
          console.error('预约请求失败', error);
        }
      }
      close();
    };


    const get_capacity_color = (capacity) => {
      if (capacity >= 100) {
        return 'green';
      } else if (capacity >= 50) {
        return 'orange';
      } else {
        return 'red';
      }
    };

    const calculateDuration = (start, end) => {
      const startTime = new Date(start);
      const endTime = new Date(end);
      const duration = endTime.getTime() - startTime.getTime();
      const hours = Math.floor(duration / (1000 * 60 * 60));
      const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60));

      return `${hours}小时 ${minutes}分钟`;
    };

    const formatDateTime = (datetime) => {
      if (!datetime) {
        return '';
      }

      const date = new Date(datetime);
      return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
    };

    const initialize = async () => {
      try {
        const typesResponse = await axios.get('http://127.0.0.1:5000/get-all-resource-types');
        types.value = typesResponse.data.resource_types;

        const capacitiesResponse = await axios.get('http://127.0.0.1:5000/get-all-resources-capacities');
        capacities.value = capacitiesResponse.data.caps;

        const locationsResponse = await axios.get('http://127.0.0.1:5000/get-all-locations');
        locations.value = locationsResponse.data.locations;

        await fetchResults();
      } catch (error) {
        console.error('初始化失败', error);
      }
    };

    onMounted(initialize);

    return {
      userId,
      search,
      type,
      capacity,
      location,
      types,
      capacities,
      locations,
      results,
      headers,
      start_date,
      end_date,
      reserveDialog,
      reservedIndex,
      reservedItem,
      reserveItem,
      close,
      reserve,
      get_capacity_color,
      calculateDuration,
      formatDateTime,
    };
  }
};
</script>
