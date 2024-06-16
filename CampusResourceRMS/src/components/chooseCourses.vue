<!-- Dashboard -->
<template>
  <v-container>
    <v-row no-gutters class="justify-center">
      <v-col cols="2" class="py-1 px-1">
        <v-card class="mx-auto text-center" color="darken-2" dark></v-card>
      </v-col>
      <v-col
        v-for="{id, name} in weekdays"
        :key="id"
        cols="1"
        class="py-1 px-1"
      >
        <v-card
          class="mx-auto text-center"
          color="darken-2"
          dark
          variant="outlined"
        >
        {{ name }}
        </v-card>
      </v-col>
    </v-row>
    <v-row no-gutters class="justify-center"
      v-for="{id, name, time} in courses"
      :key="id"
      cols="12"
    >
      <!-- 显示时间 -->
      <v-col cols="2" class="py-1 px-1">
        <v-card
          class="mx-auto text-center"
          color="darken-2"
          dark
          variant="outlined"
        >
        {{ name }}
        {{ time }}
        </v-card>
      </v-col>
      <v-col cols="1" class="py-1 px-1"
        v-for="weekday in weekdays"
        :key="weekday.id"
      >
        <v-card
          class="mx-auto text-center"
          :color="selected[(id * weekdays.length) + weekday.id] ? 'primary' : 'green'"
          @click="selectedIndex=(id * weekdays.length) + weekday.id;dialog = true"
        >
          <v-icon v-if="!selected[(id * weekdays.length) + weekday.id]">mdi-plus</v-icon>
          <v-icon v-else>mdi-check</v-icon>
        </v-card>
      </v-col>
    </v-row>
    <v-dialog
      v-model="dialog"
      max-width="290"
    >
      <v-card>
        <v-card-title class="text-h5" v-if="dialog && selectedIndex !== -1">
          {{ selected[selectedIndex] ? '取消课程' : '选择课程' }}
        </v-card-title> 
        <v-card-text v-if="dialog && selectedIndex !== -1">
          {{ selected[selectedIndex] ? '你确定要取消这节课吗？' : '你确定要选择这节课吗？' }}
        </v-card-text>
        <v-card-actions v-if="dialog && selectedIndex !== -1">
          <v-spacer></v-spacer>
          <v-btn color="green darken-1" text @click="dialogSave(selectedIndex)">确定</v-btn>
          <v-btn color="red darken-1" text @click="dialogCancel()">取消</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>


<script>
export default {
  data() {
    const weekdays = [
      { id: 0, name: "周一" },
      { id: 1, name: "周二" },
      { id: 2, name: "周三" },
      { id: 3, name: "周四" },
      { id: 4, name: "周五" },
      { id: 5, name: "周六" },
      { id: 6, name: "周日" }
    ];

    const courses = [
      { id: 0, name: "第1节", time: "08:00-09:45" },
      { id: 1, name: "第2节", time: "10:05-11:50" },
      { id: 2, name: "第3节", time: "14:00-15:45" },
      { id: 3, name: "第4节", time: "16:05-17:50" },
      { id: 4, name: "第5节", time: "18:40-20:25" },
      { id: 5, name: "第6节", time: "20:45-22:30" },
    ];

    const selected = Array.from({ length: weekdays.length * courses.length }, () => false);

    return {
      selectedIndex: -1,
      weekdays,
      courses,
      selected,
      dialog: false,
      tab: null,
    };
  },
  methods: {
    dialogSave(id) {
      this.selected[id] = !this.selected[id];
      this.emitSelected();
      this.selectedIndex = -1;
      this.dialog = false;
    },
    dialogCancel() {
      this.selectedIndex = -1;
      this.dialog = false;
    },
    emitSelected() {
      this.$emit('update:selected', this.selected);
    },
  },


};
</script>

<style>
.align-center {
align-items: center;
}

.justify-center {
justify-content: center;
}

.d-flex {
display: flex;
}
</style>
