<template>
    <v-data-table
      :headers="headers"
      :items="users"
      items-per-page="9" 
      items-per-page-text="每页显示"
    >
      <template v-slot:top>
        <v-toolbar
          flat
        >
          <v-toolbar-title>用户列表</v-toolbar-title>
          <v-divider
            class="mx-4"
            inset
            vertical
          ></v-divider>
          <v-spacer></v-spacer>
          <v-dialog v-model="dialog" max-width="500px">
            <template v-slot:activator="{ props }">
              <v-btn class="mb-2" color="primary" dark v-bind="props">添加用户</v-btn>
            </template>
            <v-card>
              <v-card-title>
                <span class="text-h5">{{ formTitle }}</span>
              </v-card-title>

              <v-card-text>
                <v-container>
                  <v-row>
                    <v-col cols="12">
                      <v-text-field v-model="editedItem.username" label="用户名称"></v-text-field>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="12">
                      <v-text-field v-model="editedItem.password" label="密码"></v-text-field>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="12">
                      <v-select
                        v-model="editedItem.role_id"
                        :items="roles"
                        item-title="role_name"
                        item-value="role_id"
                        label="角色"
                      ></v-select>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="12">
                      <v-text-field v-model="editedItem.email" label="邮箱"></v-text-field>
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
              <v-card-text class="bold">与该用户相关的所有信息都将删除, 你确定删除该用户吗?</v-card-text>
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
      <template v-slot:item.role_name="{ item}">
        {{ this.roleID2roleName(item.role_id) }}
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
  </template>

<script>
export default {
  data: () => ({
    dialog: false,
    dialogDelete: false,
    headers: [
      { title: '用户名称', align: 'start', key: 'username' },
      { title: '密码', key: 'password', sortable: false },
      { title: '角色', key: 'role_name', sortable: false },
      { title: '邮箱', key: 'email', sortable: false },
      { title: '操作', key: 'actions', sortable: false },
    ],
    users: [],
    roles: [],
    editedIndex: -1,
    editedItem: {
      user_id: '',
      username: '',
      password: '',
      role_id: '',
      email: '',
    },
    defaultItem: {
      user_id: '',
      username: '',
      password: '',
      role_id: '',
      email: '',
    },
  }),

  computed: {
    formTitle () {
      return this.editedIndex === -1 ? '添加用户' : '编辑用户'
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
    this.fetchUsers()
    this.fetchRoles()
  },

  methods: {
    initialize () {
      // 可以在需要时进行初始化操作
    },

    fetchUsers () {
      fetch('http://127.0.0.1:5000/get-all-users')
        .then(response => response.json())
        .then(data => {
          this.users = data.users;
        })
        .catch(error => {
          console.error('Error fetching users:', error);
        });
    },

    fetchRoles () {
      fetch('http://127.0.0.1:5000/get-all-roles')
        .then(response => response.json())
        .then(data => {
          this.roles = data.roles;
        })
        .catch(error => {
          console.error('Error fetching roles:', error);
        });
    },

    roleID2roleName (roleID) {
      const role = this.roles.find(role => role.role_id === roleID);
      return role ? role.role_name : 'Unknown Role';
    },

    editItem (item) {
      this.editedIndex = this.users.indexOf(item)
      this.editedItem = { ...item }
      this.dialog = true
    },

    deleteItem (item) {
      this.editedIndex = this.users.indexOf(item)
      this.editedItem = { ...item }
      this.dialogDelete = true
    },

    deleteItemConfirm () {
      fetch('http://127.0.0.1:5000/delete-user', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: this.editedItem.user_id })
      })
        .then(response => response.json())
        .then(data => {
          this.fetchUsers(); // 重新获取用户列表
          this.closeDelete();
        })
        .catch(error => {
          console.error('Error deleting user:', error);
        });
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

    save () {
      if (this.editedIndex > -1) {
        // 编辑用户
        fetch('http://127.0.0.1:5000/update-user', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.editedItem)
        })
          .then(response => response.json())
          .then(data => {
            this.fetchUsers(); // 重新获取用户列表
            this.close();
          })
          .catch(error => {
            console.error('Error updating user:', error);
          });
      } else {
        // 添加新用户
        fetch('http://127.0.0.1:5000/add-user', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.editedItem)
        })
          .then(response => response.json())
          .then(data => {
            this.fetchUsers(); // 重新获取用户列表
            this.close();
          })
          .catch(error => {
            console.error('Error adding user:', error);
          });
      }
    },
  },
}
</script>