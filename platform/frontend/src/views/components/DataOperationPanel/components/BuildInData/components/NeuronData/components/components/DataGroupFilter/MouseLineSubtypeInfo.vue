<template>
  <v-dialog
    v-model="showHyLineSubtypeInfo"
    v-bind="$attrs"
    v-on="$listeners"
    persistent
    width="900px"
    height="600px"
  >
    <div class="dialog-header">
      <span>Information of mouse line and type</span>
      <v-icon style="cursor: pointer" color="#7fbefa" size="16" @click="onClose"
        >$Close</v-icon
      >
    </div>

    <div class="dialog-content">
      <span
        style="color: #ced4e4;font-size: 14px;font-family: Roboto;margin-bottom: 16px;"
        >The following information is a quick overview showing the type and
        mouse line in “Projectome-based characterization of hypothalamic
        peptidergic neurons in male mice”.</span
      >

      <div class="display-options">
        <span
          :class="{ active: active === 'Subtype' }"
          style="border-radius: 4px 0px 0px 4px;"
          @click="active = 'Subtype'"
          >Type</span
        >
        <span
          :class="{ active: active === 'Line' }"
          style="border-radius: 0px 4px  4px 0px;"
          @click="active = 'Line'"
          >Mouse Line</span
        >
      </div>

      <div class="subtype-content" v-show="active === 'Subtype'">
        <span
          class="subtype-item"
          :class="{ active: activeSubtype === item }"
          v-for="(item, index) in classOptions"
          :key="index"
          @click="activeSubtype = item"
          >{{ item }}</span
        >
      </div>

      <img
        v-show="active === 'Subtype'"
        :src="mouseSubtypeImagePath"
        style="width: 100%; height: 207px;"
      />

      <div class="line-content" v-show="active === 'Line'">
        <span
          class="line-item"
          :class="{ active: activeLine === item }"
          v-for="(item, index) in mouseLines"
          :key="index"
          @click="activeLine = item"
          >{{ item }}</span
        >
      </div>
      <img
        v-show="active === 'Line'"
        :src="mouseLineImagePath"
        style="width: 100%; height: 207px;"
      />
    </div>
  </v-dialog>
</template>

<script>
import { mapState } from "vuex";

export default {
  name: "MouseLineSubtypeInfo",
  props: {
    showHyLineSubtypeInfo: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      active: "Subtype",
      activeSubtype: null,
      activeLine: null
    };
  },
  computed: {
    ...mapState({
      filterCondition: state => state.neuron.filterCondition,
      neuronClass: state => state.neuron.neuronClass,
      neuronType: state => state.neuron.neuronType
    }),
    currentPublicGroup() {
      return this.filterCondition.publicGroup;
    },
    classOptions() {
      if (
        this.currentPublicGroup &&
        this.currentPublicGroup === "Mouse Hypothalamus"
      ) {
        return this.neuronClass[this.currentPublicGroup]?.class;
      }
      return [];
    },

    mouseLines() {
      if (
        this.currentPublicGroup &&
        this.currentPublicGroup === "Mouse Hypothalamus"
      ) {
        const sub_type_array = this.neuronType[this.currentPublicGroup]
          ?.sub_type_array;
        if (sub_type_array) {
          return sub_type_array.slice().sort();
        }
        return [];
      }
      return [];
    },

    mouseSubtypeImagePath() {
      if (this.activeSubtype) {
        return (
          process.env.VUE_APP_SRV +
          `/info/mouse/hy/base_subtypes/type_${this.activeSubtype}.png`
        );
      }
      return "";
    },

    mouseLineImagePath() {
      if (this.activeLine) {
        return (
          process.env.VUE_APP_SRV +
          `/info/mouse/hy/base_Mouseline/type_${this.activeLine}.png`
        );
      }
      return "";
    }
  },

  watch: {
    classOptions() {
      if (this.classOptions && this.classOptions.length > 0) {
        this.activeSubtype = this.classOptions[0];
      }
    },
    mouseLines() {
      if (this.mouseLines && this.mouseLines.length > 0) {
        this.activeLine = this.mouseLines[0];
      }
    }
  },
  methods: {
    onClose() {
      this.$emit("close");
    },

    subtypeImagePath(id) {
      return (
        process.env.VUE_APP_SRV + `/info/mouse/base_subtypes/type_${id}.png`
      );
    }
  }
};
</script>

<style lang="scss" scoped>
.dialog-header {
  border-top: 2px solid #7fbefa;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 28px;
  line-height: 28px;
  padding: 0 10px;
  background: #283652;

  span {
    color: var(--dark-2, #7fbefa);
    font-size: 13px;
    font-weight: 400;
  }
}

.dialog-card {
  // padding: 14px;
  border-radius: 0;
  background: var(--dark-bg, #151c2d);

  .card-footer {
    padding-bottom: 10px;
    margin-right: 10px;
    text-align: right;
  }
}

.card-main {
  padding: 10px;
}

:deep {
  .v-dialog {
    border-radius: 0;
  }

  .theme--light.v-data-table.v-data-table--fixed-header thead th {
    box-shadow: none;
  }
}

.dialog-content {
  height: 562px;
  background: #151c2d;
  padding: 14px;
}

.display-options {
  display: flex;
  justify-content: center;
  margin-top: 16px;
  color: #a5abb9;
  font-size: 13px;
  font-family: Roboto;

  span {
    width: 110px;
    justify-content: center;
    text-align: center;
    color: #a5abb9;
    background: #1f283e;
    cursor: pointer;
  }

  .active {
    color: #ffffff;
    // border-right: 1px solid #586075;
    background: #2d68c3;
  }
}

.subtype-content {
  margin-top: 16px;
  margin-bottom: 16px;
  display: grid;
  grid-column-gap: 4px;
  grid-row-gap: 4px;
  grid-template-columns: repeat(auto-fit, minmax(50px, 1fr));

  .subtype-item {
    width: 50px;
    height: 24px;
    text-align: center;
    font-size: 14px;
    background: #1f283e;
    color: #bbb;
    cursor: pointer;
  }

  .active {
    background: #2d68c3;
    color: #ffffff;
  }
}

.line-content {
  margin-top: 16px;
  margin-bottom: 16px;
  display: grid;
  grid-column-gap: 4px;
  grid-row-gap: 4px;
  grid-template-columns: repeat(auto-fit, minmax(82px, 1fr));

  .line-item {
    width: 82px;
    height: 24px;
    text-align: center;
    font-size: 14px;
    background: #1f283e;
    color: #bbb;
    cursor: pointer;
  }

  .active {
    background: #2d68c3;
    color: #ffffff;
  }
}
</style>
