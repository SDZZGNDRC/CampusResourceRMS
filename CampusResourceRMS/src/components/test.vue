<template>
  <div>
    <VueDatePicker v-model="date" range week-picker inline />
  </div>
</template>


<script>
import { ref } from 'vue';

export default {
  setup() {
    const startDate = new Date()
    const endDate = new Date(new Date().setDate(startDate.getDate() + 7))
    const date = ref([startDate, endDate])
    return {
      date
    };
  },
  data() {
    return {}
  },
  created() {},
  methods: {
    
  }
}
</script>