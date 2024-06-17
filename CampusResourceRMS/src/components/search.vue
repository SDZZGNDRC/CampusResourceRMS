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
        <v-data-table :headers="headers" :items="results">
          <template v-slot:item.actions="{ item }">
            <v-icon class="me-2" size="small" @click="reserveItem(item)">
              mdi-note-edit-outline
            </v-icon>
          </template>
          <template v-slot:no-data>
            <v-card-text>
              没有相关记录, 请检查你的搜索条件.
            </v-card-text>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
    <v-dialog v-model="reserveDialog" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="text-h5">申请预约</span>
        </v-card-title>

        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="reservedItem.title"
                  label="标题"
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="reservedItem.description"
                  label="描述"
                ></v-text-field>
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
  </v-container>
</template>

<script>
import { ref, watch, onMounted } from 'vue';
import axios from 'axios';

export default {
  setup() {
    const search = ref('');
    const type = ref('');
    const capacity = ref(0);
    const location = ref('');
    const types = ref([]);
    const capacities = ref([]);
    const locations = ref([]);
    const results = ref([]);
    const start_date = ref(new Date());
    const end_date = ref(new Date());
    const reserveDialog = ref(false);
    const reservedIndex = ref(-1);
    const reservedItem = ref({
      title: '',
      description: ''
    });
    const defaultItem = {
      title: '',
      description: ''
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
      reservedItem.value = { ...item };
      reserveDialog.value = true;
    };

    const close = () => {
      reserveDialog.value = false;
      reservedItem.value = { ...defaultItem };
      reservedIndex.value = -1;
    };

    const reserve = () => {
      if (reservedIndex.value > -1) {
        results.value[reservedIndex.value] = { ...reservedItem.value };
      }
      close();
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
      reserve
    };
  }
};
</script>
