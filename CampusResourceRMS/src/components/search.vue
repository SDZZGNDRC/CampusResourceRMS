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
import { ref, watchEffect } from 'vue';
import axios from 'axios';
export default {
  setup() {
    const start_date = ref(new Date())
    const end_date = ref(new Date())

    watchEffect(() => {
      fetchResults(search.value, type.value, capacity.value, location.value, start_date.value, end_date.value)
        .then((data) => {
          results.value = data;
        })
        .catch((error) => {
          console.error('搜索失败', error);
        });
    });

    return {
      start_date,
      end_date,
    };
  },
  data() {
    return {
      reserveDialog: false,
      reservedIndex: -1,
      reservedItem: {
        title: '',
        description: '',
      },
      defaultItem: {
        title: '',
        description: '',
      },
      search: '',
      type: null,
      capacity: null,
      location: null,
      types: [],
      capacities: [],
      locations: [],
      results: [],
      headers: [
        { title: '资源ID', align: 'start', key: 'resource_id' },
        { title: '名称', key: 'name' },
        { title: '描述', key: 'description' },
        { title: '位置', key: 'location' },
        { title: '容量', key: 'capacity' },
        { title: '类型', key: 'type_name' },
        { title: '操作', key: 'actions', sortable: false },
      ],
    }
  },
  watch: {
    async search(val) {
      this.results = await this.fetchResults(val, this.type, this.capacity, this.location, this.start_date, this.end_date)
    },
    async type(val) {
      this.results = await this.fetchResults(this.search, val, this.capacity, this.location, this.start_date, this.end_date)
    },
    async capacity(val) {
      this.results = await this.fetchResults(this.search, this.type, val, this.location, this.start_date, this.end_date)
    },
    async location(val) {
      this.results = await this.fetchResults(this.search, this.type, this.capacity, val, this.start_date, this.end_date)
    },
    reserveDialog(val) {
      val || this.close()
    }
  },

  created() {
    this.initialize()
  },

  methods: {
    async initialize() {
        try {
            const typesResponse = await axios.get('http://127.0.0.1:5000/get-all-resource-types');
            this.types = typesResponse.data.resource_types;

            const capacitiesResponse = await axios.get('http://127.0.0.1:5000/get-all-resources-capacities');
            this.capacities = capacitiesResponse.data.caps;

            const locationsResponse = await axios.get('http://127.0.0.1:5000/get-all-locations');
            this.locations = locationsResponse.data.locations;

            this.results = await this.fetchResults('', null, null, null, this.start_date, this.end_date);
        } catch (error) {
            console.error('初始化失败', error);
        }
    },

    async fetchResults(search, type, capacity, location, start_date, end_date) {
      try {
        const response = await axios.get('http://127.0.0.1:5000/search', {
          params: {
            name: search,
            type: type,
            capacity: capacity,
            location: location,
            start_date: start_date,
            end_date: end_date,
          }
        });

        return response.data.resources;
      } catch (error) {
        console.error('搜索失败', error);
      }
      return [];
    },

    reserveItem(item) {
      this.reservedIndex = this.results.indexOf(item)
      this.reservedItem = Object.assign({}, item)
      this.reserveDialog = true
    },

    close() {
      this.reserveDialog = false
      this.$nextTick(() => {
        this.reservedItem = Object.assign({}, this.defaultItem)
        this.reservedIndex = -1
      })
    },

    reserve() {
      if (this.reservedIndex > -1) {
        Object.assign(this.results[this.reservedIndex], this.reservedItem)
      }
      this.close()
    }

  }
}
</script>
