<template>
  <div>
    <ASelect :showOptions="displayOptions" @clickOutside="displayOptions = false">
      <template slot="display-part">
        <div
          class="d-flex align-center secondary"
          style="
            min-height: 30px;
            padding: 10px;
            user-select: none;
            cursor: pointer;
            justify-content: space-between;
          "
          @click="displayOptions = true"
        >
          <span
            v-show="selectedClasses.length === 0"
            class="accent-7--text"
            style="flex-grow: 1; font-size: 13px"
          >
            Select neuron subtype
          </span>
          <div
            v-show="selectedClasses.length !== 0"
            class="selected-classes-container"
            style="max-height: 68px; overflow-y: auto"
          >
            <div
              v-for="(item, index) in selectedClasses"
              :key="index"
              class="selected-class-item"
            >
              <span class="selected-class-text">
                {{ item.value }}
              </span>
              <v-icon size="14" @click="removeChoosenItem(item)">$DeleteCross</v-icon>
            </div>
          </div>
          <v-icon size="16" :style="arrowStyle">$ArrowDown</v-icon>
        </div>
      </template>

      <template slot="options-part">
        <div
          class="d-flex flex-column accent-6"
          style="
            width: 116px;
            font-size: 13px;
            width: 100%;
            max-height: 425px;
            overflow-y: auto;
          "
        >
          <div v-for="(displayItem, index) in displayItems" :key="index">
            <div class="d-flex align-center" style="padding: 10px">
              <v-icon
                size="16"
                style="margin-right: 10px; cursor: pointer"
                @click="toggleVisibility(index)"
                :style="{
                  transform: displayItem.visible ? 'rotateZ(0deg)' : 'rotateZ(180deg)',
                }"
              >
                $ArrowDown
              </v-icon>
              <span class="primary-text--text" style="font-size: 13px">{{
                displayItem.author
              }}</span>
              <v-icon
                size="16"
                style="margin-left: 10px; cursor: pointer"
                color="primary-text"
                @click="openURL(displayItem.url)"
              >
                $Link
              </v-icon>
            </div>

            <div v-show="displayItem.visible">
              <div
                :id="displayItem.id"
                :class="isFishSC ? 'fish-sc-content' : displayItem.id"
              >
                <span
                  v-for="(classItem, classIndex) in displayItem.data"
                  :key="classIndex"
                  @click="onChooseItem({ type: displayItem.type, value: classItem })"
                  :class="{
                    highlighted:
                      selectedClasses.map((item) => item.value).includes(classItem) &&
                      displayItem.type ===
                        selectedClasses.find((item) => item.value === classItem)?.type,
                  }"
                  >{{ classItem }}</span
                >
              </div>
            </div>
          </div>
        </div>
      </template>
    </ASelect>
  </div>
</template>

<script>
import ASelect from "@/components/ASelect.vue";
import { mapState } from "vuex";
export default {
  name: "SubtypeFilter",
  components: {
    ASelect,
  },
  data() {
    return {
      displayOptions: false,
      classAddedBorder: false,
      class1AddedBorder: false,
      displayItems: [],
      selectedClasses: [],
    };
  },
  computed: {
    ...mapState({
      filterCondition: (state) => state.neuron.filterCondition,
      neuronClass: (state) => state.neuron.neuronClass,
      projects: (state) => state.projects,
      visualTarget: (state) => state.visualTarget,
      neuronTypeOrder: (state) => state.neuron.neuronTypeOrder,
    }),

    isFishSC() {
      return process.env.VUE_APP_SUB_SPECIES === "SC";
    },

    arrowStyle() {
      if (this.displayOptions) {
        return {
          transform: "rotateZ(180deg)",
        };
      }

      return {};
    },
    currentPublicGroup() {
      return this.filterCondition.publicGroup;
    },

    isGroupValid() {
      return (
        this.projects &&
        this.currentPublicGroup !== "" &&
        this.currentPublicGroup !== "All public data"
      );
    },

    author() {
      if (this.isGroupValid) {
        const item = this.projects.find((el) => el.name === this.currentPublicGroup);
        return item.author;
      }

      return "";
    },

    displayedClass() {
      if (!this.isGroupValid) {
        return [];
      }

      const projectItem = this.projects.find((el) => el.name === this.currentPublicGroup);

      const classItems = [];
      const customTypes = projectItem.customTypes;
      for (let i = 0; i < customTypes.length; i++) {
        classItems.push({
          author: customTypes[i].header || "",
          type: customTypes[i].label,
          data: this.neuronClass[this.currentPublicGroup]?.[customTypes[i].label] || [],
          showData: true,
          id: `${customTypes[i].label}-content`,
          url: customTypes[i].paperURL,
          visible: true,
        });
      }

      return classItems;
    },

    classPaperLink() {
      if (this.isGroupValid) {
        const item = this.projects.find((el) => el.name === this.currentPublicGroup);

        const customTypes = item.customTypes;
        const target = customTypes.filter((el) => el.label === "class");
        if (target.length === 0) {
          return "";
        } else {
          return target[0].paperURL;
        }
      }

      return "";
    },

    classHeader() {
      if (this.isGroupValid) {
        const item = this.projects.find((el) => el.name === this.currentPublicGroup);

        const customTypes = item.customTypes;
        const target = customTypes.filter((el) => el.label === "class");
        if (target.length === 0) {
          return "";
        } else {
          return target[0].header;
        }
      }

      return "";
    },

    class1PaperLink() {
      if (this.isGroupValid) {
        const item = this.projects.find((el) => el.name === this.currentPublicGroup);

        const customTypes = item.customTypes;
        const target = customTypes.filter((el) => el.label === "class1");
        if (target.length === 0) {
          return "";
        } else {
          return target[0].paperURL;
        }
      }
      return "";
    },

    class1Header() {
      if (this.isGroupValid) {
        const item = this.projects.find((el) => el.name === this.currentPublicGroup);

        const customTypes = item.customTypes;
        const target = customTypes.filter((el) => el.label === "class1");
        if (target.length === 0) {
          return "";
        } else {
          return target[0].header;
        }
      }

      return "";
    },
  },

  watch: {
    displayOptions() {
      if (!this.classAddedBorder) {
        setTimeout(() => {
          this.classAddedBorder = this.addBorder("class-content", 34);
        }, 300);
      }

      if (!this.class1AddedBorder) {
        setTimeout(() => {
          this.class1AddedBorder = this.addBorder("class1-content", 30);
        }, 300);
      }
    },

    displayedClass: {
      immediate: true,
      handler(newVal) {
        const items = JSON.parse(JSON.stringify(newVal));

        console.log(items);

        this.displayItems = items;
      },
    },
  },

  methods: {
    addBorder(targetID, unitHeight) {
      const target = document.getElementById(targetID);
      if (!target) {
        return false;
      }
      const height = target.clientHeight;

      if (height === 0) {
        return false;
      }

      const numOfChildren = Math.floor(height / unitHeight);
      for (let i = 0; i < numOfChildren; i += 1) {
        const div = document.createElement("div");
        div.style.top = (i + 1) * unitHeight + "px";
        div.style.width = "calc(100% - 34px)";
        div.style.height = "1px";
        div.style.background = "rgba(255,255,255,.1)";
        div.style.position = "absolute";
        div.style.left = "24px";
        target.appendChild(div);
      }

      return true;
    },

    reset() {
      this.selectedClasses = [];
      this.displayOptions = false;
      this.$emit("choose", [...this.selectedClasses]);
    },

    onChooseItem(item) {
      const index = this.selectedClasses.findIndex(
        (i) => i.value === item.value && i.type === item.type
      );
      if (index === -1) {
        this.selectedClasses.push(item);
        this.$emit("choose", [...this.selectedClasses]);
      }
    },

    removeChoosenItem(item) {
      this.selectedClasses = this.selectedClasses.filter((i) => i !== item);
      this.$emit("choose", [...this.selectedClasses]);
    },

    openURL(url) {
      window.open(url, "_blank");
    },

    toggleVisibility(index) {
      this.displayItems[index].visible = !this.displayItems[index].visible;
    },
  },
};
</script>

<style scoped lang="scss">
* {
  font-size: 13px;
  font-family: Roboto;
}

.selected-classes-container {
  font-size: 13px;
  border-radius: 2px;
  padding: 2px;
  display: flex;
  flex-wrap: wrap;
  gap: 2px 6px;
  flex-grow: 1;
  min-width: 0;
}

.selected-class-item {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
}

.selected-class-text {
  padding: 0 4px;
  line-height: 16px;
  white-space: normal;
  word-break: break-word;
}

.fish-sc-content {
  display: flex !important;
  flex-direction: column;
  width: 100%;
  text-align: left;
  position: relative;
  box-sizing: border-box;

  span {
    display: block;
    color: rgba(255, 255, 255, 0.63);
    font-size: 12px;
    font-weight: 400;
    padding: 0 10px;
    height: 34px;
    line-height: 34px;
    margin-left: 24px;
    width: calc(100% - 34px);
    box-sizing: border-box;
    cursor: pointer;
    text-align: left;
  }

  span:hover {
    background: rgba(255, 255, 255, 0.1);
  }
}

.class-content {
  display: grid;
  padding-left: 10px;
  padding-right: 10px;
  grid-auto-flow: row dense;
  grid-template-columns: repeat(10, 1fr);
  position: relative;

  span {
    display: flex;
    justify-content: center;
    align-items: center;
    white-space: nowrap;
    color: rgba(255, 255, 255, 0.63);
    font-size: 12px;
    font-weight: 400;
    height: 34px;
    margin: 0 5px 0 0;
    cursor: pointer;
  }

  span:hover {
    background: rgba(255, 255, 255, 0.1);
  }
}

.class1-content {
  display: flex;
  flex-wrap: wrap;
  padding-left: 10px;
  padding-right: 10px;
  position: relative;

  span {
    display: flex;
    justify-content: center;
    align-items: center;
    color: rgba(255, 255, 255, 0.63);
    font-size: 12px;
    font-weight: 400;
    padding: 0 10px;
    height: 30px;
    cursor: pointer;
  }

  span:hover {
    background: rgba(255, 255, 255, 0.1);
  }
}

.class2-content {
  display: flex;
  flex-wrap: wrap;
  padding-left: 10px;
  padding-right: 10px;
  position: relative;

  span {
    display: flex;
    justify-content: center;
    align-items: center;
    color: rgba(255, 255, 255, 0.63);
    font-size: 12px;
    font-weight: 400;
    padding: 0 10px;
    height: 30px;
    cursor: pointer;
  }

  span:hover {
    background: rgba(255, 255, 255, 0.1);
  }
}

.highlighted {
  background: #2d68c3;
  color: #fff;
}

:deep(.v-icon.v-icon::after) {
  display: none;
}
</style>
