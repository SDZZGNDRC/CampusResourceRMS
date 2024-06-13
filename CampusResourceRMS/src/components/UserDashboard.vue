<!-- Dashboard -->
<template>
  <v-container>
    <v-row no-gutters class="height-100">
      <v-col
        v-for="(card, index) in cards"
        :key="index"
        cols="4"
        class="py-1 px-1"
      >
        <v-card
          class="mx-auto"
          color="light-blue darken-2"
          dark
          @click="handleClick(card.id)"
        >
          <v-card-text class="d-flex align-center justify-center">
            {{ card.content }}
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>


<script>
export default {
  data() {
    return {
      cards: Array.from({ length: 3 * 3 }, (_, i) => ({ id: i + 1, content: `Card ${i + 1}` })),
      tab: null,
    };
  },
  methods: {
    handleClick(id) {
      // 执行你的逻辑
      alert(`Card ${id} clicked!`);
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
