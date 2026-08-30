<template>
  <div class="">
    <div class="setting-item item-title">Soma Radius</div>
    <div class="setting-item">
      <v-slider
        v-model="somaRadiusData"
        dense
        color="#2D68C3"
        :max="10"
        step="0.1"
        class=""
      >
        <template v-slot:append>
          <div style="transform: translate(11px, 5px)">×</div>
          <v-text-field
            :rules="rules"
            v-model="somaRadiusData"
            outlined
            dense
            color="primary"
            style="width: 51px; transform: translateY(-7px)"
          ></v-text-field>
          <FilterRefresh
            style="cursor: pointer; transform: translateY(3px)"
            fill="#7FBEFA"
            @click.native="resetSomaFunc(1)"
          ></FilterRefresh>
        </template>
      </v-slider>
    </div>
  </div>
</template>

<script>
import FilterRefresh from "@/components/icons/FilterRefresh";
import { mapState } from "vuex";
export default {
  name: "SomaRadius",

  components: { FilterRefresh },

  data() {
    return {
      rules: [
        value => !!value,
        value =>
          /^\d+(\.\d+)?$/.test(value) &&
          parseFloat(value) >= 0 &&
          parseFloat(value) <= 10
      ]
    };
  },

  watch: {
    "functionMap.set_neuron_soma_radius_scale": {
      handler(newVal) {
        if (Object.prototype.hasOwnProperty.call(newVal, "scale")) {
          this.somaRadiusData = newVal.scale;
        }
      }
    }
  },

  computed: {
    ...mapState({
      functionMap: state => state.functionMap
    }),
    somaRadiusData: {
      get() {
        return this.$store.state.settingValues.soma;
      },
      set(newV) {
        this.resetSomaFunc(+newV);
      }
    }
  },

  methods: {
    resetSomaFunc(val) {
      window.neuroViz.setSomaSizeScale(val);
      this.$store.commit("setSettingValues", {
        data: val,
        index: "soma"
      });
    }
  },

  mounted() {}
};
</script>

<style lang="scss" scoped>
:deep {
  .v-text-field input {
    transform: translateY(-1px);
    caret-color: #3b87fd;
  }

  .v-text-field__slot {
    font-size: 13px;
  }

  .v-text-field--outlined fieldset {
    height: 32px;
    border-radius: 2px;
    // border: 1px solid var(--StrokeLine, #343F5C);
    transform: translate(-9px, 6px);
  }

  .v-text-field--outlined.v-input--is-focused fieldset {
    border-color: #343f5c;
  }
}
</style>
