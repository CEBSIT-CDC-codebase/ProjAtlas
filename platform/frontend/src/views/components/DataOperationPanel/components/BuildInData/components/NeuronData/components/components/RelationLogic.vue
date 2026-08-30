<template>
  <div>
    <v-menu offset-y>
      <template v-slot:activator="{ on, attrs }">
        <div
          v-bind="attrs"
          v-on="on"
          class="background d-flex align-center justify-center"
          style="width: 24px;height: 24px;"
        >
          <v-icon size="16">{{ displayedIcon }}</v-icon>
        </div>
      </template>
      <div class="d-flex flex-column accent-6">
        <v-list-item
          v-for="(item, index) in menuItems"
          :key="index"
          style="padding:5px 10px;font-size: 13px;cursor: pointer;"
          @click="onChooseItem(item.text)"
        >
          <v-icon size="16">{{ item.icon }}</v-icon>
          {{ item.text }}
        </v-list-item>
      </div>
    </v-menu>
  </div>
</template>

<script>
export default {
  name: "RelationLogic",
  props: {
    value: {
      type: String,
      default: "",
      event: "change"
    }
  },
  data() {
    return {
      selected: null,
      menuItems: [
        { icon: "$Overlap", text: "Overlap" },
        { icon: "$Exclude", text: "Exclude" },
        { icon: "$AddLogic", text: "Add" }
      ]
    };
  },
  computed: {
    displayedIcon() {
      switch (this.value) {
        case "Overlap":
          return "$Overlap";
        case "Exclude":
          return "$Exclude";
        case "Add":
          return "$AddLogic";
        default:
          return "$AddFill";
      }
    }
  },

  methods: {
    onChooseItem(text) {
      if (this.value === "") {
        this.$emit("create", text);
      }

      this.$emit("change", text);
    }
  }
};
</script>

<style scoped lang="scss">
:deep(.v-list-item) {
  padding: 10px;
  min-height: 32px !important;
  height: 32px !important;
  display: flex;
  align-items: center !important;
}

:deep(.v-list-item__icon) {
  margin: 0 !important;
}
</style>
