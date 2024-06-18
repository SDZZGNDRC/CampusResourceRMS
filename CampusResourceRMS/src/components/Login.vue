<template>
    <v-container>
      <v-row justify="center">
        <v-col md="6">
          <v-card>
            <v-card-title class="center-align">
              <h1 class="display-1">登录</h1>
            </v-card-title>
            <v-card-text>
              <v-form ref="form" v-model="valid" @submit.prevent="submit">
                <v-text-field
                  v-model="username"
                  :rules="idRules"
                  label="学号/教师编号"
                  required
                ></v-text-field>
                <v-text-field
                  v-model="password"
                  :rules="passwordRules"
                  label="密码"
                  type="password"
                  required
                ></v-text-field>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn :disabled="!valid" color="success" type="submit">
                    提交
                  </v-btn>
                </v-card-actions>
              </v-form>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  <script>
  import axios from 'axios';

  export default {
    data: () => ({
      isLogin: false,
      valid: true,
      user_id: '',
      username: '',
      password: '',
      idRules: [
        v => !!v || '学号/教师编号是必填项',
      ],
      passwordRules: [
        v => !!v || '密码是必填项',
        v => (v && v.length >= 6) || '密码必须包含6个以上的字符',
      ],
    }),
    methods: {
      emitIsLogin() {
        this.$emit('update:isLogin', this.isLogin);
        this.$emit('update:user_id', this.user_id);
      },
      submit() {
        if (this.$refs.form.validate()) {
          const formData = new FormData();
          formData.append('username', this.username);
          formData.append('password', this.password);

          axios.post('http://127.0.0.1:5000/login', formData)
            .then(response => {
              // 根据后端返回的结果进行跳转或显示错误信息
              if (response.data.status === 'success') {
                this.isLogin = true;
                this.user_id = response.data.user.id;
                this.emitIsLogin();
                console.log(response.data)
                this.$router.push('/search');
              } else {
                this.username = '';
                this.password = '';
                // 在登录框显示错误
              }
            })
            .catch(error => {
              console.error(error);
              // 处理错误
            });
        }
      },
    },
  };
  </script>


<style>
.center-align {
  text-align: center;
}
</style>
