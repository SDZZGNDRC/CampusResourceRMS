<template>
  <v-container>
    <v-data-table
      :headers="headers"
      :items="resources"
      items-per-page="9" 
      items-per-page-text="每页显示"
    >
      <template v-slot:top>
        <v-toolbar
          flat
        >
          <v-toolbar-title>资源列表</v-toolbar-title>
          <v-divider
            class="mx-4"
            inset
            vertical
          ></v-divider>
          <v-spacer></v-spacer>
          <v-dialog v-model="dialog" max-width="500px">
            <template v-slot:activator="{ props }">
              <v-btn class="mb-2" color="primary" dark v-bind="props">添加资源</v-btn>
            </template>
            <v-card>
              <v-card-title>
                <span class="text-h5">{{ formTitle }}</span>
              </v-card-title>

              <v-card-text>
                <v-container>
                  <v-row>
                    <v-col cols="12">
                      <v-text-field v-model="editedItem.name" label="资源名称"></v-text-field>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="12">
                      <v-text-field v-model="editedItem.description" label="描述"></v-text-field>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="6">
                      <v-text-field v-model="editedItem.location" label="位置"></v-text-field>
                    </v-col>
                    <v-col cols="6">
                      <v-text-field v-model="editedItem.capacity" label="容量"></v-text-field>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="12">
                      <v-select
                        v-model="editedItem.type_id"
                        :items="types"
                        item-title="type_name"
                        item-value="type_id"
                        label="类型"
                      ></v-select>
                    </v-col>
                  </v-row>
                </v-container>
              </v-card-text>

              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="blue-darken-1" variant="text" @click="close">取消</v-btn>
                <v-btn color="blue-darken-1" variant="text" @click="save">保存</v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>

          <v-dialog v-model="dialogDelete" max-width="500px">
            <v-card>
              <v-card-title class="text-h5">再次确定</v-card-title>
              <v-card-text class="bold">与该资源相关的所有信息都将删除, 你确定删除该资源吗?</v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="blue-darken-1" variant="text" @click="closeDelete">取消</v-btn>
                <v-btn color="red" variant="text" @click="deleteItemConfirm">确认</v-btn>
                <v-spacer></v-spacer>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </v-toolbar>
      </template>
      <template v-slot:item.capacity="{ value }">
            <v-chip :color="this.get_capacity_color(value)">
              {{ value }}
            </v-chip>
          </template>
      <template v-slot:item.type_name="{ item }">
        {{ this.typeID2typeName(item.type_id) }}
      </template>
      <template v-slot:item.actions="{ item }">
        <v-icon
          class="me-2"
          size="small"
          color="primary"
          @click="editItem(item)"
        >
          mdi-pencil
        </v-icon>
        <v-icon
          size="small"
          color="red"
          @click="deleteItem(item)"
        >
          mdi-delete
        </v-icon>
      </template>
    </v-data-table>
  </v-container>
  </template>

<script>
export default {
  data: () => ({
    dialog: false,
    dialogDelete: false,
    headers: [
      { title: '名称', key: 'name' },
      { title: '描述', key: 'description', sortable: false },
      { title: '位置', key: 'location' },
      { title: '容量', key: 'capacity' },
      { title: '类型', key: 'type_name' },
      { title: '操作', key: 'actions', sortable: false },
    ],
    resources: [],
    types: [],
    editedIndex: -1,
    editedItem: {
      resource_id: '',
      name: '',
      description: '',
      location: '',
      capacity: '',
      status: '',
      type_id: '',
    },
    defaultItem: {
      resource_id: '',
      name: '',
      description: '',
      location: '',
      capacity: '',
      status: '',
      type_id: '',
    },
  }),

  computed: {
    formTitle () {
      return this.editedIndex === -1 ? '添加资源' : '编辑资源'
    },
  },

  watch: {
    dialog (val) {
      val || this.close()
    },
    dialogDelete (val) {
      val || this.closeDelete()
    },
  },

  created () {
    this.fetchResources()
    this.fetchTypes()
  },

  methods: {
    initialize () {
      // 可以在需要时进行初始化操作
    },

    fetchResources() {
      fetch('http://127.0.0.1:5000/search')
        .then(response => response.json())
        .then(data => {
          this.resources = data.resources;
        })
        .catch(error => {
          console.error('Error fetching resources:', error);
        });
    },

    fetchTypes () {
      fetch('http://127.0.0.1:5000/get-all-resource-types')
        .then(response => response.json())
        .then(data => {
          this.types = data.resource_types;
        })
        .catch(error => {
          console.error('Error fetching resource_types:', error);
        });
    },

    typeID2typeName (typeID) {
      const t = this.types.value.find((type) => type.type_id === typeID);
      return t ? t.type_name : '未知类型';
    },

    editItem (item) {
      this.editedIndex = this.resources.indexOf(item)
      this.editedItem = { ...item }
      this.dialog = true
    },

    deleteItem (item) {
      this.editedIndex = this.resources.indexOf(item)
      this.editedItem = { ...item }
      this.dialogDelete = true
    },

    deleteItemConfirm () {
      fetch('http://127.0.0.1:5000/delete-resource', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ resource_id: this.editedItem.resource_id }),
      })
      .then(response => response.json())
      .then(data => {
        console.log(data.message);
        this.fetchResources(); // 重新获取资源列表
      })
      .catch(error => {
        console.error('Error deleting resource:', error);
      });
      this.closeDelete();
    },

    close () {
      this.dialog = false
      this.$nextTick(() => {
        this.editedItem = { ...this.defaultItem }
        this.editedIndex = -1
      })
    },

    closeDelete () {
      this.dialogDelete = false
      this.$nextTick(() => {
        this.editedItem = { ...this.defaultItem }
        this.editedIndex = -1
      })
    },

    typeID2typeName (typeID) {
      const t = this.types.find((type) => type.type_id === typeID);
      return t ? t.type_name : '未知类型';
    },

    get_capacity_color (capacity) {
      if (capacity >= 100) {
        return 'green';
      } else if (capacity >= 50) {
        return 'orange';
      } else {
        return 'red';
      }
    },

    save () {
      if (this.editedIndex > -1) {
        fetch('http://127.0.0.1:5000/update-resource', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(this.editedItem),
      })
      .then(response => response.json())
      .then(data => {
        console.log(data.message);
        this.fetchResources(); // 重新获取资源列表
        this.close();
      })
      .catch(error => {
        console.error('Error updating resource:', error);
      });
  } else {
      fetch('http://127.0.0.1:5000/add-resource', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(this.editedItem),
      })
      .then(response => response.json())
      .then(data => {
        console.log(data.message);
        this.fetchResources(); // 重新获取资源列表
        this.close();
      })
      .catch(error => {
          console.error('Error adding resource:', error);
        });
      }
    }
  },
}
</script>