<template>
  <div class="d-flex flex-column">
    <ASelect
      :showOptions="displaySearchOptions"
      @clickOutside="displaySearchOptions = false"
    >
      <template slot="display-part">
        <div
          class="d-flex flex-row"
          style="
            height: 40px;
            border-radius: 2px;
            flex-grow: 1;
            border: 1px solid #343f5c;
          "
        >
          <div
            class="d-flex align-center primary"
            style="
              height: 38px;
              border-radius: 2px;
              flex-grow: 1;
              border: 1px solid #343f5c;
            "
          >
            <v-icon
              size="16"
              style="margin-left: 10px; margin-right: 5px"
              color="#7F8491"
            >
              mdi-magnify
            </v-icon>
            <input
              v-model="searchText"
              class="id-input primary-text--text"
              style="flex-grow: 1"
              placeholder="Search brain area"
              @input="searchRegionTree"
              @click="searchRegionTree"
            />
          </div>
        </div>
      </template>

      <template slot="options-part">
        <div
          class="d-flex flex-column accent-6"
          style="
            width: 116px;
            font-size: 13px;
            font-family: Roboto;
            width: 100%;
            max-height: 200px;
            overflow-y: auto;
          "
        >
          <span
            style="
              height: 24px;
              line-height: 24px;
              margin: 2px 10px;
              cursor: pointer;
              font-size: 12px;
            "
            v-for="(searchItem, index) in searchResult"
            :key="index"
            v-html="highlightKeyWords(searchItem.name)"
            @click="chooseRegion(searchItem)"
          ></span>
        </div>
      </template>
    </ASelect>
    <div style="max-height: calc(100vh - 460px); overflow-y: auto">
      <v-treeview
        v-model="selectedItems"
        ref="regionTree"
        selectable
        :items="regionTree"
        :filter="filter"
        :selection-type="dynamicSelectionType"
        :active="activeItems"
        :open="openItems"
        dark
        dense
        return-object
        selected-color="#7fbefa"
        style="color: #c4c4c4; font-size: 13px; font-family: Roboto sans-serif"
      >
        <template slot="label" slot-scope="{ item }">
          <v-tooltip top>
            <template v-slot:activator="{ on, attrs }">
              <div
                v-bind="attrs"
                v-on="on"
                style="display: flex; align-items: center"
              >
                <span v-html="highlightKeyWords(item.name)"> </span>
                <v-icon
                  v-if="item.name === 'C Contour'"
                  color="#2d68c3"
                  style="margin-left: 4px; cursor: pointer;font-size: 20px;"
                  @click="onAddRootToView(item)"
                  >mdi-bookmark-plus</v-icon
                >
              </div>
            </template>
            <span v-html="highlightKeyWords(item.name)"></span>
          </v-tooltip>
        </template>
      </v-treeview>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
import ASelect from "@/components/ASelect.vue";
import { loadRegion } from "@/utils/neuronLoader";

export default {
  name: "RegionFilter",
  components: {
    ASelect
  },
  data() {
    return {
      regionTree: [],
      selectedItems: [],
      openItems: [],
      activeItems: [],
      search: "",
      toBeViewedItems: [],
      displaySearchOptions: false,
      searchText: "",
      searchResult: []
    };
  },
  computed: {
    ...mapState({
      visualTarget: state => state.visualTarget,
      regionType: state => state.region.regionType,
      regionData: state => state.region.regionData,
      viewedRegions: state => state.region.viewedRegions
    }),

    filter() {
      return (item, search, textKey) => {
        return item[textKey].indexOf(search) !== -1;
      };
    },

    dynamicSelectionType() {
      return "independent";
    }
  },

  watch: {
    regionType() {
      // build the tree according to region type
      this.buildRegionTree();
    },

    viewedRegions() {
      const viewedIds = this.viewedRegions.map(el => el.id);
      this.selectedItems = this.selectedItems.filter(
        item => viewedIds.indexOf(item.id) === -1
      );
    },

    selectedItems() {
      this.$store.commit("region/setFilteredRegions", this.selectedItems);
    }
  },

  mounted() {
    if (this.regionTree.length === 0 && this.regionType["sub_type_array"]) {
      this.buildRegionTree();
    }
  },

  methods: {
    buildRegionTree() {
      const addChildType = (parentObj, typeName) => {
        let obj = {};
        //id
        obj.id = itemCount;
        obj.depth = parentObj ? parentObj.depth + 1 : 0;
        itemCount++;
        //name
        if (typeName.includes("(") && typeName.includes(")")) {
          let parts = typeName.split("(");
          let arc = parts[0].trim().toLocaleUpperCase();
          let main = parts[1].split(")")[0].trim();
          obj.name = arc + " " + main;
        } else {
          obj.name = typeName;
        }

        //Children
        obj.children = [];

        if (parentObj == null) {
          obj.regionObj = this.regionType[typeName];
          obj.parentObj = null;
        } else {
          obj.regionObj = parentObj.regionObj[typeName];
          obj.parentObj = parentObj;
          parentObj.children.push(obj);
        }

        //if there are any subarray, iterate the subarray
        if (Object.keys(obj.regionObj).includes("sub_type_array")) {
          let subTypes = obj.regionObj["sub_type_array"];
          subTypes.forEach(type => {
            addChildType(obj, type);
          });
        }
        return obj;
      };

      this.regionTree = [];
      this.openItems = [];
      this.selectedItems = [];
      this.activeItems = [];

      let itemCount = 0;
      //creat the tree for region types
      let subTypes = this.regionType["sub_type_array"];
      for (let i = 0; i < subTypes.length; ++i) {
        let mainTypeName = subTypes[i];
        let obj = addChildType(null, mainTypeName);
        this.regionTree.push(obj);
      }
      this.openItems.push(this.regionTree[0]);
      this.openItems.push(this.regionTree[0].children[0]);
      this.openItems.push(this.regionTree[0].children[1]);

      // load root region if it is not loaded
      const viewedUIDs = this.viewedRegions.map(el => el.uid);
      const rootUID = this.regionTree[0].regionObj["uid_array"][0];
      const filteredRegions = [];
      if (viewedUIDs.indexOf(rootUID) === -1) {
        this.selectedItems.push(this.regionTree[0]);
        // filteredRegions.push(this.regionTree[0]);
        // this.$store.commit("region/setFilteredRegions", filteredRegions);
        if (process.env.VUE_APP_SUB_SPECIES === "rbm") {
          const defaultRegions = [
            1200,
            1201,
            834,
            851,
            842,
            10,
            496345664,
            496345668,
            496345672,
            27,
            706,
            1061,
            628,
            215,
            178,
            286,
            390,
            186,
            797,
            58
          ];
          const findRegionByUID = uid => {
            const stack = [...this.regionTree];
            while (stack.length) {
              const current = stack.pop();
              const uidArray =
                (current.regionObj && current.regionObj["uid_array"]) || [];
              if (uidArray.includes(String(uid))) {
                return current;
              }
              if (current.children && current.children.length) {
                stack.push(...current.children);
              }
            }
            return null;
          };

          defaultRegions.forEach(uid => {
            const matchedRegion = findRegionByUID(uid);
            if (
              matchedRegion &&
              !this.selectedItems.some(item => item.id === matchedRegion.id)
            ) {
              this.selectedItems.push(matchedRegion);
            }
          });
          // find eye region and add to view
          const eyeRegion = this.regionTree.find(item =>
            item.name.includes("Eyes")
          );
          if (eyeRegion) {
            this.selectedItems.push(eyeRegion);
          }
        }
        setTimeout(() => this.$emit("loadRoot"), 1);
      }

      if (this.$route.path === "/spcd") {
        // load spcd if it is not loaded
        const spcdID = this.regionTree[1].regionObj["uid_array"][0];
        if (viewedUIDs.indexOf(spcdID) === -1) {
          this.selectedItems.push(this.regionTree[1]);
          filteredRegions.push(this.regionTree[1]);
          this.$store.commit("region/setFilteredRegions", filteredRegions);
          this.$emit("loadRoot");
        }
      }

      this.$store.commit("region/setRegionAxonTreeArray", this.regionTree);
    },

    highlightKeyWords(content) {
      if (this.searchText && this.searchText.length > 1) {
        let text = "";
        let lowerCaseContent = content.toLocaleLowerCase();
        const parts = lowerCaseContent.split(
          this.searchText.toLocaleLowerCase()
        );

        let count = 0;
        for (let i = 0; i < parts.length; ++i) {
          if (parts[i].length === 0) {
            text += `<span style="color: #01d1ff; font-weight: bolder;" :style="{marginRight: i===0? '8px':'0}">${content.slice(
              count,
              count + this.searchText.length
            )}</span>`;
            count += this.searchText.length;
          } else {
            let words = content.slice(count, count + parts[i].length);
            count += parts[i].length;
            text +=
              words +
              `<span style="color: #01d1ff; font-weight: bolder;">${content.slice(
                count,
                count + this.searchText.length
              )}</span>`;
            count += this.searchText.length;
          }
        }
        return text;
      } else {
        let text = "";
        const tempStr = content.split(" ");
        if (this.visualTarget === "mouse") {
          for (let i = 0; i < tempStr.length; ++i) {
            if (this.isAllCapitalized(tempStr[i])) {
              text += `<span style="color: #ffffff; font-weight: bolder;margin-right: 8px">${tempStr[i]}</span>`;
            } else {
              const rest = tempStr.slice(i).join(" ");
              text += `<span >${rest}</span>`;
              break;
            }
          }
          return text;
        } else {
          for (let i = 0; i < tempStr.length; ++i) {
            if (i === 0) {
              text += `<span style="color: #ffffff; font-weight: bolder;margin-right: 8px">${tempStr[i]}</span>`;
            } else {
              const rest = tempStr.slice(i).join(" ");
              text += `<span >${rest}</span>`;
              break;
            }
          }
          return text;
        }
      }
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

    searchRegionTree() {
      this.displaySearchOptions = false;
      if (this.searchText.length < 2) {
        if (this.searchText.length === 0) {
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
      this.regionTree.forEach(item => {
        iterateSearch(item, this.searchText.toLocaleLowerCase().trim());
      });
    },

    chooseRegion(item) {
      this.searchText = item.name;
      this.displaySearchOptions = false;
      this.selectedItems = [];
      this.selectedItems.push(item);
      this.openItems = [];
      const openTarget = target => {
        if (target && target.parentObj) {
          this.openItems.push(target.parentObj);
          openTarget(target.parentObj);
        }
      };
      openTarget(item);

      this.$store.commit("region/setFilteredRegions", this.selectedItems);
    },

    clearSearch() {
      this.searchText = "";
      this.displaySearchOptions = false;

      this.openItems = [];
      this.openItems.push(this.regionTree[0]);
      this.openItems.push(this.regionTree[0].children[0]);
      this.openItems.push(this.regionTree[0].children[1]);

      this.selectedItems = [];
      this.$store.commit("region/setFilteredRegions", this.selectedItems);
    },

    onAddRootToView(item) {
      loadRegion(item);
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
  .v-treeview-node__children {
    .v-treeview-node--disabled {
      .v-icon--disabled {
        display: none !important;
      }
    }
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
