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
            :items="statuses"
            label="状态"
            v-model="status"
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
  export default {
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
        status: null,
        location: null,
        types: ['类型1', '类型2', '类型3'],
        statuses: ['状态1', '状态2', '状态3'],
        locations: ['位置1', '位置2', '位置3'],
        results: [ { title: '搜索结果1', description: '描述1' }, { title: '搜索结果2', description: '描述2' } ], // 添加一个新的数据属性来存储搜索结果
        headers: [
          { title: '标题', align: 'start', key: 'title' },
          { title: '描述', key: 'description' },
          { title: '操作', key: 'actions', sortable: false },
        ],
      }
    },
    watch: {
      search(val) {
        this.results = this.fetchResults(val, this.type, this.status, this.location)
      },
      type(val) {
        this.results = this.fetchResults(this.search, val, this.status, this.location)
      },
      status(val) {
        this.results = this.fetchResults(this.search, this.type, val, this.location)
      },
      location(val) {
        this.results = this.fetchResults(this.search, this.type, this.status, val)
      },
      reserveDialog(val) {
        val || this.close()
      }
    },
  
    created() {
      this.initialize()
    },
  
    methods: {
  
      initialize() {
        // this.fetchResults('', null, null, null)
      },
  
      fetchResults(search, type, status, location) {
        // 在这里执行你的搜索操作并返回结果
        // 这只是一个示例，你需要根据你的实际需求来实现这个函数
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
  