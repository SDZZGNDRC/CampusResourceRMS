<template>
<v-container>
  <v-stepper v-model="step" :items="steps">
    <template v-slot:item.1>
      <ChooseCourses :selected.sync="selectedCourses"></ChooseCourses>
    </template>
    <template v-slot:item.2>
      <div style="display: flex; justify-content: center;">
        <v-card>
          <h2 style="display: flex; justify-content: center;">
            请选择课程的开始周和结束周
          </h2>
          <VueDatePicker 
            v-model="date" range week-picker inline 
            style="display: flex; justify-content: center;"
          />
        </v-card>
      </div>
    </template>

    <template v-slot:item.3>
      <v-row>
        <v-col cols="4">
          <v-card>
            <v-card-title>填写课程信息</v-card-title>
            <v-card-text>
              <v-text-field v-model="courseName" label="课程名称"></v-text-field>
              <v-text-field v-model="numberOfStudents" label="学生人数"></v-text-field>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

    </template>
  </v-stepper>
</v-container>
</template>
  
<script>
import ChooseCourses from './chooseCourses.vue';
import { ref } from 'vue';
export default {
  components: {
    // ChooseCourses,
  },
  setup() {
    const startDate = new Date()
    const endDate = new Date(new Date().setDate(startDate.getDate() + 7))
    const date = ref([startDate, endDate])
    return {
      date
    };
  },
  data () {
    return {
      steps: ['选择课程时间', '设置课程持续时间', '设置课程信息'],
      step: 1,
      selectedCourses: [],
    }
  }
};
</script>
  