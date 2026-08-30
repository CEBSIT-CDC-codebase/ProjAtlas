<template>
  <ADialog
    :visible="show"
    title="Change Coloring Schema"
    width="320"
    persistent
    @update:visible="onVisible"
  >
    <template>
      <div
        class="d-flex flex-column color-schema"
        style="font-size: 13px; padding: 14px;"
      >
        <span style="margin-bottom: 10px;">Neuron coloring schema</span>
        <ASelect :showOptions="showOptions" @clickOutside="showOptions = false">
          <template slot="display-part">
            <div
              class="d-flex align-center"
              style="height: 32px;border: 1px solid #343f5c;border-radius: 2px;padding: 5px 10px; user-select: none;"
              @click="showOptions = true"
            >
              <span style="flex-grow: 1;">{{ colorSchema }}</span>
              <v-icon size="16" :style="arrowStyle">$ArrowDown</v-icon>
            </div>
          </template>

          <template slot="options-part">
            <div
              class="d-flex flex-column accent-6"
              style="font-size: 13px;width: 100%;"
            >
              <span
                v-for="(item, index) in schemaOptions"
                :key="index"
                style="padding: 10px;cursor: pointer;"
                @click="onChooseColorSchema(item)"
                >{{ item }}</span
              >
            </div>
          </template>
        </ASelect>
        <div
          class="align-center"
          style="height: 32px;border: 1px solid #343f5c;margin-top: 10px ;margin-bottom: 18px; display: grid; grid-template-columns: 1fr 1fr 1fr;"
          :style="{
            border: colorScheme === 'structure' ? '1px solid #343f5c' : 'none'
          }"
        >
          <div class="d-flex align-center" v-if="colorScheme === 'structure'">
            <div
              style="width: 16px;height: 16px;margin-right: 10px;margin-left: 14px;background: #FAFF00;border: 1px solid #868686;"
            ></div>
            <span class="primary-text--text" style="font-size: 13px;"
              >Dentrite</span
            >
          </div>
          <div class="d-flex align-center" v-if="colorScheme === 'structure'">
            <div
              style="width: 16px;height: 16px;margin-right: 10px;margin-left: 14px;background: #FF0CBB;border: 1px solid #868686;"
            ></div>
            <span class="primary-text--text" style="font-size: 13px;"
              >Soma</span
            >
          </div>
          <div class="d-flex align-center" v-if="colorScheme === 'structure'">
            <div
              style="width: 16px;height: 16px;margin-right: 10px;margin-left: 14px;background: #29F179;border: 1px solid #868686;"
            ></div>
            <span class="primary-text--text" style="font-size: 13px;"
              >Axon</span
            >
          </div>
        </div>
        <div
          class="d-flex align-center"
          style="justify-content: right; height: 24px; "
        >
          <div
            class="color-action-button primary-text--text"
            style="margin-right:10px;text-align: center;"
            @click="onCancel"
          >
            Cancel
          </div>
          <div
            class="d-flex justify-center background color-action-button "
            @click="onApply"
          >
            Apply
          </div>
        </div>
      </div>
    </template>
  </ADialog>
</template>

<script>
import ASelect from "@/components/ASelect.vue";
import ADialog from "@/components/ADialog";
import { hexToRgb } from "@/utils/utils.js";
import { mapState } from "vuex";

export default {
  name: "ColorSchema",
  components: {
    ASelect,
    ADialog
  },
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      showOptions: false,
      colorSchema: "",
      schemaOptions: [
        "Set by random color",
        "Set by mouse line",
        "Set by soma location area",
        "Set by neuron structure"
      ]
    };
  },
  computed: {
    ...mapState({
      colorScheme: state => state.neuron.colorScheme,
      viewedNeurons: state => state.neuron.viewedNeurons
    }),

    arrowStyle() {
      if (this.showOptions) {
        return {
          transform: "rotateZ(180deg)"
        };
      }

      return {};
    }
  },
  watch: {
    show() {
      if (this.colorScheme === "random") {
        this.colorSchema = "Set by random color";
      } else if (this.colorScheme === "mouseLine") {
        this.colorSchema = "Set by mouse line";
      } else if (this.colorScheme === "region") {
        this.colorSchema = "Set by soma location area";
      } else {
        this.colorSchema = "Set by neuron structure";
      }

      setTimeout(() => {
        const setOverflow = element => {
          if (element) {
            if (element.classList.contains("v-dialog")) {
              element.style.overflow = "visible";
            } else {
              setOverflow(element.parentElement);
            }
          }
        };

        const schema = document.getElementsByClassName("color-schema");
        for (let i = 0; i < schema.length; i++) {
          setOverflow(schema[i]);
        }
      }, 200);
    }
  },

  mounted() {},
  methods: {
    onVisible() {
      this.$emit("close");
      this.showOptions = false;
    },

    onChooseColorSchema(schema) {
      this.colorSchema = schema;
      this.showOptions = false;
    },
    onApply() {
      if (this.colorSchema === "Set by random color") {
        this.batchSetIDColor();
      } else if (this.colorSchema === "Set by mouse line") {
        this.batchSetMouseLineColor();
      } else if (this.colorSchema === "Set by soma location area") {
        // TODO
      } else {
        this.batchSetStructureColor();
      }

      this.showOptions = false;
      this.$emit("close");
    },

    onCancel() {
      this.showOptions = false;
      this.$emit("close");
    },

    batchSetIDColor() {
      const selectedNeurons = this.viewedNeurons.filter(el => el.selected);
      selectedNeurons.forEach(neuron => {
        neuron.colorScheme = "random";
        const rgb = hexToRgb(neuron.idColor).map(el => el / 255.0);
        window.neuroViz.setColor(neuron.file, rgb);
      });

      this.$store.commit("neuron/setColorScheme", "random");
    },

    batchSetMouseLineColor() {
      const selectedNeurons = this.viewedNeurons.filter(el => el.selected);
      selectedNeurons.forEach(neuron => {
        neuron.colorScheme = "mouseLine";
        const rgb = neuron.typeColor.map(el => el / 255.0);
        window.neuroViz.setColor(neuron.file, rgb);
      });

      this.$store.commit("neuron/setColorScheme", "mouseLine");
    },

    batchSetStructureColor() {
      const selectedNeurons = this.viewedNeurons.filter(el => el.selected);
      selectedNeurons.forEach(neuron => {
        neuron.colorScheme = "structure";
        const { somaColor, axonColor, dentriteColor, undefinedColor } = {
          ...neuron.structureColor
        };
        window.neuroViz.setSWCPartColor(
          neuron.file,
          somaColor,
          axonColor,
          dentriteColor,
          undefinedColor
        );
      });

      this.$store.commit("neuron/setColorScheme", "structure");
    }
  }
};
</script>

<style scoped lang="scss">
.color-action-button {
  padding: 4px 14px;
  font-size: 13px;
  cursor: pointer;
  border-radius: 21px;
  border: 1px solid #343f5c;
}

:deep(.v-dialog) {
  overflow: visible !important;
}
</style>
