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
            item-title="type_name"
            item-value="type_id"
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
        <v-col cols="2">
          <v-row align="center">
          <v-switch
            v-model="display_style"
            :label="`${display_style}`"
            false-value="表格展示"
            true-value="图表展示"
          ></v-switch>
          </v-row>
        </v-col>
        <v-col cols="5">
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
        <v-col cols="5">
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
          <!-- 表格形式展示 -->
          <v-data-table
            :headers="headers" :items="results" 
            items-per-page="7" items-per-page-text="每页显示"
            v-if="display_style==='表格展示'"
          >
            <template v-slot:item.capacity="{ value }">
              <v-chip :color="get_capacity_color(value)">
                {{ value }}
              </v-chip>
            </template>
            <template v-slot:item.type_name="{ item }">
              {{ typeID2typeName(item.type_id) }}
            </template>
            <template v-slot:no-data>
              <v-card-text>
                没有相关记录, 请检查你的搜索条件.
              </v-card-text>
            </template>
          </v-data-table>
          <!-- 图表形式展示 -->
          <Bar :data="chartData" v-if="display_style==='图表展示'" />
        </v-col>
      </v-row>
  
    </v-container>
  </template>
  
  <script>
  import { ref, watch, onMounted, inject, computed } from 'vue';
  import axios from 'axios';
  import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    BarElement,
    CategoryScale,
    LinearScale
  } from 'chart.js'
  import { Bar } from 'vue-chartjs'

  ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

  export default {
    components: {
      Bar,
    },
    setup() {
      const userId = inject('user_id');
      const search = ref('');
      const display_style = ref('表格展示'); // 图表展示
      const type = ref(null);
      const capacity = ref(null);
      const location = ref(null);
      const types = ref([]);
      const capacities = ref([]);
      const locations = ref([]);
      const results = ref([]);
      const start_date = ref(null);
      const end_date = ref(null);

      const chartData = computed(() => {
        // 从results中提取需要的数据，比如资源名称和预约次数
        const chartData = results.value.map((resource) => {
          return {
            name: resource.name,
            count: resource.count
          };
        });

        return {
          labels: chartData.map((data) => data.name),
          datasets: [
            {
              label: '预约次数',
              backgroundColor: 'rgba(75, 192, 192, 0.2)',
              borderColor: 'rgba(75, 192, 192, 1)',
              borderWidth: 1,
              data: chartData.map((data) => data.count)
            }
          ]
        };
      });

      const headers = [
        { title: '名称', key: 'name' },
        { title: '位置', key: 'location' },
        { title: '容量', key: 'capacity' },
        { title: '类型', key: 'type_name' },
        { title: '预约次数', key: 'count' },
        { title: '总时长(分钟)', key: 'duration' },
      ];
  
      const fetchResults = async () => {
        try {
          const response = await axios.get('http://127.0.0.1:5000/statistics', {
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
  
      const typeID2typeName = (typeID) => {
        const t = types.value.find((type) => type.type_id === typeID);
        return t ? t.type_name : '未知类型';
      };
  
      watch([search, type, capacity, location, start_date, end_date, display_style], fetchResults, { immediate: true });
  
  
      const get_capacity_color = (capacity) => {
        if (capacity >= 100) {
          return 'green';
        } else if (capacity >= 50) {
          return 'orange';
        } else {
          return 'red';
        }
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
        display_style,
        type,
        capacity,
        location,
        typeID2typeName,
        types,
        capacities,
        locations,
        chartData,
        results,
        headers,
        start_date,
        end_date,
        get_capacity_color,
      };
    }
  };
  </script>
  