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
                  v-model="email"
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
  export default {
    data: () => ({
      valid: true,
      email: '',
      password: '',
      idRules: [
        v => !!v || '学号/教师编号是必填项',
        v => /^\d+$/.test(v) || '学号/教师编号必须有效',
      ],
      passwordRules: [
        v => !!v || '密码是必填项',
        v => (v && v.length >= 8) || '密码必须包含8个以上的字符',
      ],
    }),
    methods: {
      submit() {
        if (this.$refs.form.validate()) {
          // 检查密码是否包含英文字母
          const containsLetter = /[a-zA-Z]/.test(this.password);

          if (containsLetter) {
            // 密码包含英文字母，跳转到 Home 页面
            this.$router.push('/userdashboard');
          } else {
            // 密码不包含英文字母，跳转到 About 页面
            this.$router.push('/about');
          }
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
