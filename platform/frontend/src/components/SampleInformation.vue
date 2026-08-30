<template>
  <div class="main" id="sample-information-table">
    <div class="table-header">
      <span>Sample Information</span>
      <v-icon size="14" @click="onClose">$Close</v-icon>
    </div>
    <div class="table-content">
      <span>Injection structure:</span>
      <span class="content">{{ injectionStructure }}</span>
      <span>Mouse line:</span>
      <span class="content">{{ mouseLine }}</span>
      <span>Gender:</span>
      <span class="content">{{ gender }}</span>
      <span>Injection age:</span>
      <span class="content">{{ age }}</span>
      <span>Injection coordinates:</span>
      <div class="content" style="display: flex; flex-direction: column">
        <span v-for="(item, index) in injectionCoordinates" :key="index">
          {{ item }}
        </span>
      </div>
      <span>Injection virus:</span>
      <span class="content">{{ injectionVirus }}</span>
      <span>Virus expression time:</span>
      <span class="content">{{ ampleDay }}</span>
      <span>Injection volume:</span>
      <div class="content" style="display: flex; flex-direction: column">
        <span v-for="(item, index) in siteVolume" :key="index">
          {{ item + " nl/site" }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";

export default {
  name: "SampleInformation",
  props: {
    neuronItem: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      mouseDown: false,
      mouseDownX: 0,
      mouseDownY: 0
    };
  },
  computed: {
    ...mapState({
      sampleInformation: state => state.sampleInformation
    }),

    currentSampleInfomation() {
      const res = this.sampleInformation[this.neuronItem?.projectFullName];
      return res;
    },

    targetItem() {
      if (!this.currentSampleInfomation || !this.neuronItem) {
        return "";
      }
      const targetId = this.neuronItem?.file?.split("_")[0];
      const res = this.currentSampleInfomation.find(
        el => Number(el.fMOST_id) === Number(targetId)
      );
      return res;
    },

    injectionStructure() {
      if (
        !this.currentSampleInfomation ||
        !this.neuronItem ||
        !this.targetItem
      ) {
        return "";
      }

      return this.targetItem?.injection_structure;
    },

    mouseLine() {
      if (
        !this.currentSampleInfomation ||
        !this.neuronItem ||
        !this.targetItem
      ) {
        return "";
      }

      return this.targetItem?.transgenic_line;
    },

    gender() {
      if (
        !this.currentSampleInfomation ||
        !this.neuronItem ||
        !this.targetItem
      ) {
        return "";
      }

      return this.targetItem?.gender === 0 ? "Male" : "Female";
    },

    age() {
      if (
        !this.currentSampleInfomation ||
        !this.neuronItem ||
        !this.targetItem
      ) {
        return "";
      }

      return this.targetItem?.age + " days";
    },

    injectionCoordinates() {
      if (
        !this.currentSampleInfomation ||
        !this.neuronItem ||
        !this.targetItem
      ) {
        return [];
      }

      return this.targetItem?.injection_coordinates?.split(";");
    },

    injectionVirus() {
      if (
        !this.currentSampleInfomation ||
        !this.neuronItem ||
        !this.targetItem
      ) {
        return "";
      }

      return this.targetItem?.injection_virus;
    },

    ampleDay() {
      if (
        !this.currentSampleInfomation ||
        !this.neuronItem ||
        !this.targetItem
      ) {
        return "";
      }

      return this.targetItem?.ample_delivery_time + " days";
    },

    siteVolume() {
      if (
        !this.currentSampleInfomation ||
        !this.neuronItem ||
        !this.targetItem
      ) {
        return [];
      }

      if (!this.targetItem?.injection_volume) {
        return [];
      }

      return this.targetItem?.injection_volume?.split(";");
    }
  },
  methods: {
    onClose() {
      this.$emit("closeTable");
    }
  }
};
</script>

<style scoped lang="scss">
::-webkit-scrollbar {
  width: 2px !important;
}

::-webkit-scrollbar-thumb {
  width: 2px !important;
}

.main {
  background: #26272bcc;
  display: flex;
  flex-direction: column;
  color: #f5f8ff;
  width: 310px;
  z-index: 9;
}

.table-header {
  border-top: 2px solid #7fbefa;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 28px;
  line-height: 28px;
  padding: 0 10px;
  background: #283652;

  span {
    color: #7fbefa;
    font-weight: 400;
    font-size: 13px;
    text-align: left;
  }
}

.table-content {
  display: grid;
  grid-template-columns: 120px auto;
  grid-row-gap: 10px;
  font-family: Roboto, sans-serif;
  max-height: 300px;
  overflow-y: auto;
  padding: 10px;
  span {
    font-size: 12px;
  }
}

.content {
  word-wrap: break-word;
  width: 155px;
}
</style>
