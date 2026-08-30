<template>
  <div style="flex-grow: 1">
    <ASelect
      :showOptions="displaySearchOptions"
      @clickOutside="displaySearchOptions = false"
    >
      <template slot="display-part">
        <div
          class="d-flex align-center secondary"
          style="
            position: relative;
            height: 28px;
            padding: 5px 5px;
            user-select: none;
            cursor: pointer;
            justify-content: space-between;
            border-radius: 2px;
          "
        >
          <input
            v-model="keyWords"
            :disabled="disableInput"
            class="primary-text--text"
            placeholder="Brain area"
            style="flex-grow: 1"
            @click="onClickInputField"
          />
          <div
            v-show="disableInput"
            @click="onClickInputMask"
            style="
              position: absolute;
              top: 0;
              left: 0;
              width: calc(100% - 24px);
              height: 100%;
            "
          ></div>
          <v-icon
            v-show="disableInput"
            size="16"
            color="#7F8491"
            @click="onClearRegion"
          >
            $DeleteCross
          </v-icon>
        </div>
      </template>

      <template slot="options-part">
        <div
          class="d-flex flex-column accent-6"
          style="font-size: 13px; width: 350px; max-height: 400px; overflow: auto"
        >
          <div v-if="regionName === ''" class="d-flex flex-column accent-6">
            <span
              style="
                height: 24px;
                line-height: 24px;
                margin: 2px 10px;
                cursor: pointer;
                font-size: 12px;
                width: 320px;
                max-width: 320px;
                text-overflow: ellipsis;
                white-space: nowrap;
                overflow: hidden;
              "
              v-for="(searchItem, index) in searchResult"
              :key="index"
              v-html="highlightKeyWords(searchItem.name)"
              @click="chooseRegion(searchItem)"
            ></span>
          </div>

          <v-treeview
            v-show="showTree"
            ref="regionTree"
            :items="regionAxonTreeArray"
            :dense="true"
            :active="activeItems"
            :open.sync="openTree"
            selection-type="independent"
            selected-color="light-blue"
            return-object
            :activatable="true"
            :hoverable="true"
            color="#c4c4c4;"
            @update:active="onChooseRegion"
          >
            <template v-slot:label="{ item, active }">
              <v-tooltip right>
                <template v-slot:activator="{ on, attrs }">
                  <div
                    v-bind="attrs"
                    v-on="on"
                    class="d-flex align-center"
                    style="font-size: 12px; cursor: pointer"
                    :style="{ fontWeight: active ? 'bolder' : '' }"
                    :class="hideTooltip ? 'hide' : ''"
                  >
                    <span v-html="highlightKeyWords(item.name)"></span>
                  </div>
                </template>
                <span v-html="highlightKeyWords(item.name)"></span>
              </v-tooltip>
            </template>
          </v-treeview>
        </div>
      </template>
    </ASelect>
  </div>
</template>

<script>
import ASelect from "@/components/ASelect.vue";
import { mapState } from "vuex/dist/vuex.common.js";
export default {
  name: "RegionSearch",
  props: {
    neuronPart: {
      type: String,
      default: ""
    }
  },
  components: {
    ASelect
  },
  data() {
    return {
      regionTree: [],
      openItems: [],
      activeItems: [],
      search: "",
      displaySearchOptions: false,
      keyWords: "",
      searchResult: [],
      regionName: "",
      openTree: [],
      hideTooltip: false,
      disableInput: false,
      showTree: false
    };
  },

  computed: {
    ...mapState({
      functionMap: state => state.functionMap,
      regionAxonTreeArray: state => state.region.regionAxonTreeArray
    })
  },
  watch: {
    keyWords() {
      if (!this.keyWords || this.keyWords.length === 0) {
        this.openTree = [this.regionAxonTreeArray[0]];
        this.searchResult = [];
        this.showTree = true;
      } else {
        if (this.regionName === "") {
          this.showTree = false;
        }

        this.searchRegionTree();
      }
    },

    "functionMap.set_soma_location": {
      handler(newVal) {
        if (this.neuronPart === "Soma") {
          this.onClearRegion();
          this.keyWords = newVal?.region;
        }
      }
    },

    "functionMap.set_axon_projects_to_location": {
      handler(newVal) {
        if (this.neuronPart === "Axon") {
          this.onClearRegion();
          this.keyWords = newVal?.region;
        }
      }
    }
  },

  methods: {
    onClickInputField() {
      if (this.keyWords === "") {
        this.displaySearchOptions = true;
        this.showTree = true;
        this.openTree = [this.regionAxonTreeArray[0]];
        this.searchResult = [];
      } else {
        this.searchRegionTree();
      }
    },

    onClickInputMask() {
      if (this.regionName !== "") {
        this.displaySearchOptions = true;
        this.showTree = true;

        this.$nextTick(() => {
          const element = this.$refs.regionTree.$el.querySelector(
            ".v-treeview-node--active"
          );
          if (element) element.scrollIntoView();
        });
      }
    },
    searchRegionTree() {
      this.displaySearchOptions = false;
      if (this.keyWords.length < 2) {
        if (this.keyWords.length === 0) {
          this.clearSearch();
        }
        return;
      }
      this.displaySearchOptions = true;

      const iterateSearch = (item, search) => {
        if (item.name.toLocaleLowerCase().includes(search)) {
          this.searchResult.push(item);
        }
        item.children.forEach(child => {
          iterateSearch(child, search);
        });
      };

      this.searchResult = [];
      this.regionAxonTreeArray.forEach(item => {
        iterateSearch(item, this.keyWords.toLocaleLowerCase().trim());
      });
    },

    clearSearch() {
      this.keyWords = "";
      this.displaySearchOptions = false;

      this.openTree = [];
      this.openTree.push(this.regionAxonTreeArray[0]);
      this.openTree.push(this.regionAxonTreeArray[0].children[0]);
      this.openTree.push(this.regionAxonTreeArray[0].children[1]);
    },

    isAllCapitalized(str) {
      const len = str.length;
      for (let i = 0; i < len; ++i) {
        if (str.charAt(i) !== str.charAt(i).toUpperCase()) {
          return false;
        }
      }
      return true;
    },

    highlightKeyWords(content) {
      if (this.keyWords && this.keyWords.length > 0) {
        let text = "";
        let lowerCaseContent = content.toLocaleLowerCase();
        const parts = lowerCaseContent.split(this.keyWords.toLocaleLowerCase());

        let count = 0;
        for (let i = 0; i < parts.length; ++i) {
          if (parts[i].length === 0) {
            text += `<span style="color: #01d1ff; font-weight: bolder;text-overflow:ellipsis;" :style="{marginRight: i===0? '8px':'0'}">${content.slice(
              count,
              count + this.keyWords.length
            )}</span>`;
            count += this.keyWords.length;
          } else {
            let words = content.slice(count, count + parts[i].length);
            if (words.endsWith(" ")) {
              words = words.slice(0, -1) + "&nbsp";
            }
            count += parts[i].length;
            text +=
              words +
              `<span style="color: #01d1ff; font-weight: bolder;">${content.slice(
                count,
                count + this.keyWords.length
              )}</span>`;
            count += this.keyWords.length;
          }
        }
        return text;
      } else {
        let text = "";
        const tempStr = content.split(" ");
        for (let i = 0; i < tempStr.length; ++i) {
          if (this.isAllCapitalized(tempStr[i])) {
            text += `<span style="color: #ced4e4; font-weight: bolder;margin-right: 8px">${tempStr[i]}</span>`;
          } else {
            const rest = tempStr.slice(i).join(" ");
            text += `<span >${rest}</span>`;
            break;
          }
        }

        return text;
      }
    },

    onChooseRegion(activeItems) {
      if (activeItems.length === 0) {
        return;
      }

      // it's an array, but only one is selected
      const uid = activeItems[0].regionObj.uid_array[0];
      this.$emit("changeRegion", uid);
      this.keyWords = activeItems[0].name;
      this.disableInput = true;
      this.displaySearchOptions = false;
      this.showTree = false;
      this.regionName = activeItems[0].name;

      // hide tool tips if there are any
      const toolTips = document.getElementsByClassName("v-tooltip__content");
      Array.from(toolTips).forEach(el => {
        el.style.display = "none";
      });
    },

    onClearRegion() {
      this.keyWords = "";
      this.disableInput = false;
      this.regionName = "";
      this.searchResult = [];
      this.$emit("changeRegion", "");
      this.$nextTick(() => {
        this.openTree = [this.regionAxonTreeArray[0]];
      });
    },

    chooseRegion(item) {
      this.keyWords = item.name;
      this.displaySearchOptions = false;
      this.openTree = [];
      this.regionName = item.name;
      this.showTree = false;
      this.disableInput = true;
      this.activeItems = [item];

      const uid = item.regionObj.uid_array[0];
      this.$emit("changeRegion", uid);

      const openTarget = target => {
        if (target && target.parentObj) {
          this.openTree.push(target.parentObj);
          openTarget(target.parentObj);
        }
      };
      openTarget(item);
    }
  }
};
</script>

<style lang="scss" scoped>
* {
  font-size: 13px;
  font-family: Roboto;
}

:deep {
  .v-treeview-node__checkbox {
    color: #7f8490;
    margin-left: 0;
  }
  .v-treeview-node__root {
    padding-left: 0 !important;
  }

  .v-treeview--dense .v-treeview-node__root {
    min-height: 28px !important;
    height: 28px;
  }

  .v-treeview-node__level {
    width: 8px !important;
  }

  .v-treeview-node__toggle {
    width: 18px !important;
    height: 28px !important;
  }

  .v-treeview {
    color: #ced4e4;
  }
}

:deep(.v-input--selection-controls__input) {
  width: 16px !important;
  height: 16px !important;
  margin: 0 !important;
}

:deep(.v-input) {
  padding: 0 !important;
  margin: 0 !important;
}

:deep(.v-icon) {
  font-size: 16px !important;
  color: #7f8490;
}

:deep(.v-input__control) {
  padding: 0 !important;
}

:deep(.v-icon.v-icon::after) {
  display: none;
}
</style>
