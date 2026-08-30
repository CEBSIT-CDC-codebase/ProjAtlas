<template>
  <div class="">
    <div class="setting-item item-title">Background Color</div>
    <div class="setting-item">
      <v-menu
        v-model="colorPicker"
        offset-x
        :nudge-left="39"
        :nudge-bottom="25"
        :close-on-content-click="false"
      >
        <template v-slot:activator="{ on, attrs }">
          <div
            v-bind="attrs"
            v-on="on"
            style="
              width: 16px;
              height: 16px;
              margin: 10px;
              border-radius: 1px;
              border: 1px solid #7f8490;
              cursor: pointer;
              z-index: 10;
            "
            @click.stop="colorPicker = true"
            :style="computeNeuronColor()"
          >
            <p style="transform: translate(23px, -8px)">
              {{ settingBackground.slice(1) }}
            </p>
          </div>
        </template>

        <v-color-picker
          v-model="settingBackground"
          :elevation="0"
          hide-mode-switch
          width="285"
          height="152"
        ></v-color-picker>
      </v-menu>
    </div>
  </div>
</template>

<script>
import { hexToRgb } from "@/utils/utils";
import { mapState } from "vuex";
export default {
  name: "BackgroundColor",

  components: {},

  data() {
    return {
      colorPicker: false
    };
  },

  watch: {
    "functionMap.set_background_color": {
      handler(newVal) {
        if (Object.prototype.hasOwnProperty.call(newVal, "color")) {
          this.settingBackground = newVal.color;
        }
      }
    }
  },

  computed: {
    ...mapState({
      functionMap: state => state.functionMap
    }),

    settingBackground: {
      get() {
        return this.$store.state.settingValues.background;
      },
      set(newV) {
        this.$store.commit("setSettingValues", {
          data: newV,
          index: "background"
        });
        const val = hexToRgb(newV)?.map(item => item / 255);
        window.neuroViz.setBackground(val);
      }
    }
  },

  methods: {
    computeNeuronColor() {
      return `background: ${this.settingBackground}`;
    }
  },

  mounted() {}
};
</script>

<style lang="scss" scoped></style>
