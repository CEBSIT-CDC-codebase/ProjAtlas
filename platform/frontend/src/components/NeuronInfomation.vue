<template>
  <div class="neuron_info_div" id="neuron_info_div">
    <sample-information
      v-if="showSampleInfo && currentNeuronItem != null"
      :neuron-item="currentNeuronItem"
      @closeTable="showSampleInfo = false"
      style="
        position: absolute;
        top: 0;
        left: 0;
        transform: translateX(calc(-100% - 10px));
      "
    >
    </sample-information>

    <div class="neuron_info_header atlas-draggable-header">
      <span>Neuron Info</span>
      <v-icon size="14" @click="closeFunc">$Close</v-icon>
    </div>
    <div class="neuron_tab_div">
      <div class="neuron_tab_item_div" v-show="visualType === 'mouse'">
        <div
          class="neuron_tab_first_column"
          style="border-top: 1px solid #586075"
        >
          <span style="margin-left: 8px">Sample ID</span>
        </div>
        <div
          class="neuron_tab_second_column"
          style="border-top: 1px solid #586075"
        >
          <span
            style="margin-left: 8px; line-height: 28px; color: #f5f8ff"
            class="pickable_span"
            @click="showSampleInfo = true"
          >
            {{
              currentNeuronItem != null
                ? currentNeuronItem?.file?.split("_")[0]
                : ""
            }}
          </span>
        </div>
      </div>

      <div class="neuron_tab_item_div">
        <div class="neuron_tab_first_column">
          <span style="margin-left: 8px">Neuron ID</span>
        </div>
        <div class="neuron_tab_second_column">
          <span style="margin-left: 8px; line-height: 28px; color: #f5f8ff">{{
            currentNeuronItem != null
              ? currentNeuronItem?.file?.slice(0, -4)?.replace("-", "")
              : ""
          }}</span>
        </div>
      </div>

      <div class="neuron_tab_item_div">
        <div class="neuron_tab_first_column">
          <span style="margin-left: 8px">{{
            isRBM ? "Soma EyeSide" : "Soma Hemisphere"
          }}</span>
        </div>
        <div class="neuron_tab_second_column">
          <span style="margin-left: 8px; line-height: 28px">{{
            currentNeuronItem !== null
              ? neuronData[currentNeuronItem?.projectFullName][
                  currentNeuronItem?.id
                ]?.hemisphere
              : ""
          }}</span>
        </div>
      </div>

      <div class="neuron_tab_item_div">
        <div class="neuron_tab_first_column">
          <span style="margin-left: 8px">Soma Brain Area</span>
        </div>
        <div class="neuron_tab_second_column">
          <span
            v-for="(somaItem, somaIndex) in neuronSomaLocations"
            :key="somaIndex"
            :style="{
              textDecoration: somaItem.viewed ? 'none' : 'underline',
              cursor: somaItem.viewed ? 'default' : 'pointer'
            }"
            @click="onAddRegionFromNeuronInforPanel(somaItem)"
            >{{ somaItem?.label }}</span
          >
        </div>
      </div>

      <div class="neuron_tab_item_div">
        <div class="neuron_tab_first_column" style="height: 70px">
          <span style="margin-left: 8px; line-height: 70px !important">
            Projection Area
          </span>
        </div>
        <div
          class="neuron_tab_second_column"
          style="height: 70px; overflow-y: auto; display: flex; flex-wrap: wrap"
        >
          <span
            v-for="(axonItem, axonIndex) in neuronProjectionLocations"
            :key="axonIndex"
            :style="{
              textDecoration: axonItem.viewed ? 'none' : 'underline',
              cursor: axonItem.viewed ? 'default' : 'pointer'
            }"
            @click="onAddRegionFromNeuronInforPanel(axonItem)"
            >{{ axonItem.label }}</span
          >
        </div>
      </div>

      <div class="neuron_tab_item_div" v-if="positionVisible">
        <div class="neuron_tab_first_column" style="height: 60px">
          <span style="margin-left: 8px; line-height: 60px !important">
            Coordinates
          </span>
        </div>
        <div
          class="neuron_tab_second_column"
          style="height: 60px; overflow-y: auto; display: flex; flex-wrap: wrap"
        >
          <span>X: {{ worldPosition[0].toFixed(1) }}</span>
          <span>Y: {{ worldPosition[1].toFixed(1) }}</span>
          <span>Z: {{ worldPosition[2].toFixed(1) }}</span>
        </div>
      </div>

    </div>

    <div class="neuron_info">
      <v-icon size="16" class="mr-1">$GreeInfo</v-icon>
      Click on the name of the brain area to add it to the scene.
    </div>
  </div>
</template>
<script>
import { mapGetters, mapState } from "vuex";
import { loadRegion } from "@/utils/neuronLoader";
import SampleInformation from "./SampleInformation.vue";
export default {
  name: "NeuronInfomation",
  components: {
    SampleInformation
  },
  props: ["currentItem", "positionVisible"],
  data() {
    return {
      currentNeuronItem: null,
      neuronSomaLocations: [],
      neuronProjectionLocations: [],
      showSampleInfo: false
    };
  },
  watch: {
    currentItem() {
      if (!this.currentItem) return;
      const relationItem = this.neuronRegionRelation[
        this.currentItem?.projectFullName
      ][this.currentItem?.id];
      this.currentNeuronItem = {
        inputRegionArray: relationItem.input_region_array,
        outputRegionArray: relationItem.output_region_array,
        ownerRegionArray: relationItem.owner_region_array.slice(-1),
        outputLengthArray: relationItem.output_length_array,
        ...this.currentItem
      };
      this.showNeuronItemInfo();
      const fullName = this.currentItem?.projectFullName;
      if (this.sampleInformation[fullName]) return;
      this.$store.dispatch("getSampleInformation", fullName);
    },

    viewedRegions() {
      const viewedSet = new Set(
        this.viewedRegions.map(element => String(element.uid))
      );

      this.neuronSomaLocations.forEach(element => {
        element.viewed = viewedSet.has(String(element.uid));
      });

      this.neuronProjectionLocations.forEach(element => {
        element.viewed = viewedSet.has(String(element.uid));
      });
    }
  },
  computed: {
    ...mapState({
      sampleInformation: state => state.sampleInformation,
      viewedRegions: state => state.region.viewedRegions,
      regionData: state => state.region.regionData,
      neuronData: state => state.neuron.neuronData,
      worldPosition: state => state.PickedInformation.pickedNeuronWorldPosition,
      neuronRegionRelation: state => state.neuron.neuronRegionRelation,
      viewTarget: state => state.target
    }),

    ...mapGetters(["visualType"]),
    isRBM() {
      return process.env.VUE_APP_SUB_SPECIES === "rbm";
    }
  },
  created() {},
  mounted() {},
  methods: {
    closeFunc() {
      this.$emit("close");
      this.showSampleInfo = false;
    },

    showNeuronItemInfo() {
      const viewedSet = new Set(
        this.viewedRegions.map(element => String(element.uid))
      );

      this.neuronSomaLocations = [];
      this.currentNeuronItem.ownerRegionArray.forEach(id => {
        this.neuronSomaLocations.push({
          label: this.getRegionAbbraviation(id),
          uid: id,
          viewed: viewedSet.has(String(id))
        });
      });

      this.neuronProjectionLocations = [];
      const idSet = this.filterLeafRegionIDSet(
        this.currentNeuronItem.outputRegionArray || []
      );
      idSet.forEach(id => {
        this.neuronProjectionLocations.push({
          label: this.getRegionAbbraviation(id),
          uid: id,
          viewed: viewedSet.has(String(id))
        });
      });
    },

    filterLeafRegionIDSet(regionArray) {
      const idSet = new Set(regionArray);
      for (let i = 0; i < regionArray.length; i++) {
        const raw = this.regionData[regionArray[i]];
        const pID = raw.parent_uid + "";
        idSet.delete(pID);
      }
      return idSet;
    },

    getRegionAbbraviation(regionId) {
      return this.regionData[regionId].acronym;
    },

    onAddRegionFromNeuronInforPanel(inforItem) {
      if (inforItem.viewed === true) {
        return;
      }
      // check again
      let viewedIds = this.viewedRegions.map(element => {
        return String(element.uid);
      });

      if (viewedIds.indexOf(String(inforItem.uid)) !== -1) {
        inforItem.viewed = true;
        return;
      }

      inforItem.name = inforItem.label;
      inforItem.regionObj = {
        uid_array: [inforItem.uid]
      };

      loadRegion(inforItem);
      inforItem.viewed = true;
    }
  }
};
</script>
<style lang="scss" scoped>
.neuron_info_div {
  transition: all 0.3s 0.1s;
  width: 300px;
  background-color: rgba(38, 39, 43, 0.8);
  position: fixed;
  left: -310px;
  top: 50px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.neuron_info_header {
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

.neuron_tab_div {
  margin: 10px 12px 10px 10px;
}

.neuron_tab_item_div {
  display: flex;
  color: #f5f8ff;
  font-size: 12px;
}

.neuron_tab_first_column {
  width: 122px;
  height: 28px;
  border-left: 1px solid #586075;
  border-right: 1px solid #586075;
  border-bottom: 1px solid #586075;
}

.neuron_tab_first_column span {
  line-height: 28px;
  font-size: 12px;
}

.neuron_tab_second_column {
  flex: 1;
  height: 28px;
  width: 254px;
  border-right: 1px solid #586075;
  border-bottom: 1px solid #586075;
}

.neuron_tab_second_column span {
  margin-left: 8px;
  line-height: 28px;
  font-size: 12px;
  color: #f5f8ff;
}

.neuron_tab_second_column p {
  margin-left: 8px;
  line-height: 28px;
  color: #f5f8ff;
}

.disabled_button {
  cursor: default !important;
  background-color: #586075 !important;
}

.contour_region {
  font-weight: bolder;
  font-size: 16px;
  color: #01d1ff;
}

.pickable_span {
  cursor: pointer;
  text-decoration: underline;
}

.neuron_info {
  margin: 0 10px 10px;
  display: flex;
  align-items: center;
  color: #808080;
  font-size: 12px;
}

::v-deep
  .theme--dark.v-btn.v-btn--disabled:not(.v-btn--flat):not(.v-btn--text):not(.v-btn--outlined) {
  background-color: #26272b !important;
}
</style>
