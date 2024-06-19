<template>
<v-container>
  <v-stepper v-model="step" :items="steps">
    <template v-slot:item.1>
      <ChooseCourses @update:selected="updateSelectedCourses"></ChooseCourses>
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
    <template v-slot:item.4>
      <v-card>
        <v-card-title>确认课程信息</v-card-title>
        <v-card-text>
          <p>课程名称: {{ courseName }}</p>
          <p>学生人数: {{ numberOfStudents }}</p>
          <p>课程时间: {{ selectedArr2string(selectedCourses) }}</p>
          <p>开始日期: {{ date[0][0] }}</p>
          <p>结束日期: {{ date[1][0] }}</p>
          <p>持续周数: {{ getWeeksBetween(date[0][0], date[1][0]) }}</p>
          <!-- Add more information as needed -->
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" @click="submitCourseInfo">确认</v-btn>
        </v-card-actions>
      </v-card>
    </template>
  </v-stepper>
</v-container>
</template>
  

<script>
import ChooseCourses from './chooseCourses.vue';
import { ref, inject, computed } from 'vue';
import axios from 'axios'; // Assuming you use axios for HTTP requests

export default {
  components: {
    ChooseCourses,
  },
  setup() {
    const startDate = new Date()
    const endDate = new Date(new Date().setDate(startDate.getDate() + 7))
    const date = ref([startDate, endDate])
    const steps = ref(['选择课程时间', '设置课程持续时间', '设置课程信息', '确认信息'])
    const step = ref(1)
    const selectedCourses = ref([])
    const numberOfStudents = ref(null)
    const courseName = ref('')
    const userId = inject('user_id')

    const formatDate = (date) => {
      return date.toISOString().substring(0, 10);
    }

    const courseID2courseName = (courseID) => {
      const dayOfWeek = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"];
      const dayIndex = Math.floor(courseID / 6);
      const courseIndex = courseID % 6 + 1;
      return `${dayOfWeek[dayIndex]}第${courseIndex}节`;
    }

    const selectedArr2string = (arr) => {
      const selectedCourses = [];
      for (let i = 0; i < arr.length; i++) {
        if (arr[i]) {
          selectedCourses.push(courseID2courseName(i));
        }
      }
      return selectedCourses.join(', ');
    }

    const getWeeksBetween = (startDate, endDate) => {
      if (!startDate || !endDate) {
        return 0;
      }

      let diff = endDate.getTime() - startDate.getTime();
      let days = diff / (24 * 60 * 60 * 1000);
      let weeks = days / 7;

      return weeks;
    }

    const updateSelectedCourses = (newSelectedCourses) => {
      selectedCourses.value = newSelectedCourses;
    }

    const submitCourseInfo = async () => {
      // try {
      //   await axios.post('http://127.0.0.1:5000/reserve-course', {
      //     user_id: userId.value,
      //     start_time: date.value[0][0],
      //     end_time: date.value[1][1],
      //     course_name: courseName.value,
      //     student_number: numberOfStudents.value,
      //     selected: selectedCourses.value,
      //   });

      //   courseName.value = '';
      //   numberOfStudents.value = '';
      //   selectedCourses.value = [];
      //   step.value = 1;
      // } catch (error) {
      //   console.error(error);
      // }
    }

    return {
      date,
      steps,
      step,
      selectedCourses,
      numberOfStudents,
      courseName,
      formatDate,
      courseID2courseName,
      selectedArr2string,
      getWeeksBetween,
      updateSelectedCourses,
      submitCourseInfo,
    }
  },
};
</script>