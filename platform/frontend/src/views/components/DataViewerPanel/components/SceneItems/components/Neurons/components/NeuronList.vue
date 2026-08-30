<template>
  <div v-click-outside="itemClickOutside" class="neuron-list" ref="neuronList">
    <div class="d-flex align-center" style="height: 36px; padding: 0 10px">
      <v-checkbox
        hide-details
        dense
        :ripple="false"
        style="margin-right: 10px"
        color="#7fbefa"
        :indeterminate="selectAllIndeterminate"
        v-model="selectAll"
        @change="onSelectAllChanged"
      ></v-checkbox>
      <span style="flex-grow: 1; margin-left: 10px"
        >select {{ selectedNeuron.length }} neuron</span
      >
      <span>{{ selectedNeuron.length }}/{{ viewedNeuronsData.length }}</span>
    </div>
    <!-- :max-height="windowHeight * 0.6 - 50" -->

    <v-virtual-scroll
      :items="viewedNeuronsData"
      :height="scrollHeight"
      item-height="36"
      :bench="scrollHeight / 32 + 1"
    >
      <template v-slot:default="{ item }">
        <div
          :id="item.file"
          class="d-flex align-center"
          style="height: 36px; padding: 0 10px; position: relative"
          @mouseenter="item.hovered = true"
          @mouseleave="item.hovered = false"
        >
          <div
            v-show="item.hovered || item.menuVisible"
            class="border-style hover-border"
          ></div>
          <div
            v-show="activeItem?.file === item.file"
            class="border-style active-border"
          ></div>

          <v-checkbox
            hide-details
            dense
            :ripple="false"
            color="#7fbefa"
            v-model="item.selected"
          ></v-checkbox>
          <v-icon
            size="24"
            style="margin-left: 14px; padding: 4px"
            @click="onChangeItemVisible(item)"
            >{{ item.visible ? "$Eye" : "$EyeHide" }}
          </v-icon>
          <v-menu
            v-model="item.colorPicker"
            offset-x
            :nudge-left="380"
            :close-on-content-click="false"
            content-class="neuron-color-picker-menu"
          >
            <template v-slot:activator="{ on, attrs }">
              <div
                v-bind="attrs"
                v-on="on"
                style="
                  width: 16px;
                  height: 16px;
                  margin: 10px;
                  border-radius: 2px;
                  cursor: pointer;
                  z-index: 10;
                  flex-shrink: 0;
                "
                @click.stop="item.colorPicker = true"
                :style="computeNeuronColor(item)"
              ></div>
            </template>

            <v-color-picker
              :value="hexToRgbaObj(item.currentColor)"
              width="285"
              flat
              dark
              mode="rgba"
              canvas-height="190"
              @input="val => onColorPickerInput(item, val)"
            ></v-color-picker>
          </v-menu>
          <!-- <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <span
                class="op-85"
                style="
                  flex: 1;
                  margin-left: 10px;
                  text-overflow: ellipsis;
                  white-space: nowrap;
                  overflow: hidden;
                "
                v-bind="attrs"
                v-on="on"
                @click.stop="onNeuronNameClick(item)"
              >
                {{ item.file.slice(0, -4) }}
              </span>
            </template>
            {{ item.file }}
          </v-tooltip> -->
          <span
            class="op-85"
            style="
              flex: 1;
              margin-left: 10px;
              text-overflow: ellipsis;
              white-space: nowrap;
              overflow: hidden;
            "
            @click.stop="onNeuronNameClick(item)"
          >
            {{ item.file.slice(0, -4) }}
          </span>

          <SingleNeuronOperations
            :ref="item.file"
            v-show="item.hovered || item.menuVisible"
            :neuron-item="item"
            @visibleChanged="
              visible => {
                item.menuVisible = visible;
              }
            "
            @viewInfo="onNeuronItemClick(item)"
          />

          <v-icon size="24" @click="onDeleteItem(item)" class="bg-icon">
            $DeleteCross
          </v-icon>
        </div>
      </template>
    </v-virtual-scroll>

    <div class="resize-handle"></div>

    <NeuronInfomation
      v-show="neuronInfoVisible"
      :currentItem="infoItem"
      :positionVisible="positionVisible"
      @close="closeNeuronInfo"
    ></NeuronInfomation>
    <a-dialog
      :visible.sync="operationDialogVisible"
      @confirm="operationGroupFunc"
      width="320"
      :title="neuronListOperation?.tag + ' Neurons'"
      cancelbtnText="Cancel"
      :surebtnText="neuronListOperation?.tag"
      :footerVisible="true"
    >
      <div class="operation-dialog">
        <div>
          <p class="operation-text">
            {{ neuronFileName }} neurons are selected
          </p>
          <p class="operation-text" style="margin-bottom: 10px">
            Select a group you want to {{ lowerText }} neurons to
          </p>
          <div>
            <com-select
              v-model="currentGroupId"
              color="info"
              item-text="name"
              item-value="id"
              :items="groupInfo"
              :menu-props="{
                bottom: true,
                contentClass: 'neuron-list-menu',
                offsetY: true
              }"
              height="32"
              placeholder="select"
              append-icon="$ArrowDown"
            >
              <template v-slot:item="{ item, attrs, on }">
                <v-list-item v-on="on" v-bind="attrs" :disabled="item?.locked">
                  <v-list-item-title class="d-flex">
                    <span
                      class="group-name-item"
                      :style="{
                        opacity: item?.locked ? '.5' : '.87'
                      }"
                    >
                      {{ item.name }}
                    </span>
                    <lock style="margin-left: 5px" v-show="item?.locked"></lock>
                  </v-list-item-title>
                </v-list-item>
              </template>
            </com-select>
          </div>
        </div>
      </div>
    </a-dialog>

    <a-dialog
      :visible.sync="deleteDialogVisible"
      width="320"
      @confirm="confirmDeleteGroup"
      title="Delete Confirmation"
      cancelbtnText="Cancel"
      surebtnText="Yes,delete!"
      :footerVisible="true"
    >
      <div class="delete-dialog">
        <v-icon>$Alert</v-icon>
        <span> {{ deleteText }} </span>
      </div>
    </a-dialog>
  </div>
</template>

<script>
import { mapState, mapGetters } from "vuex";
import ADialog from "@/components/ADialog";
import ComSelect from "@/components/ComSelect";
import SingleNeuronOperations from "./SingleNeuronOperations.vue";
import NeuronInfomation from "@/components/NeuronInfomation.vue";
import Lock from "@/components/icons/Lock";
import { hexToRgb, debounce } from "@/utils/utils.js";
import {
  getGroupDetailFunc,
  deleteGroupFunc,
  updateGroupFunc
} from "@/api/group";
import interact from "interactjs";
export default {
  name: "NeuronList",

  components: {
    ADialog,
    ComSelect,
    Lock,
    SingleNeuronOperations,
    NeuronInfomation
  },

  data() {
    return {
      selectAll: false,
      hoveredNeuronItem: null,
      lastActiveItem: {},
      activeItem: null,
      infoItem: null,
      currentGroupId: "",
      neuronInfoVisible: false,
      deleteText: "",
      neuronDelAll: false,
      viewInfo: false,
      windowHeight: window.innerHeight,
      positionVisible: false,
      scrollHeight: 36,
      maxContentHeight: 0,
      listHeaderHeight: 50,
      // Perf optimization: precompute Map<groupId, neuron[]> to avoid O(n) filter on every group switch
      groupToNeurons: new Map(),
      groupMapSize: 0
    };
  },

  computed: {
    ...mapState({
      groups: state => state.groups,
      groupsDetailData: state => state.groupsDetailData,
      groupFolderTag: state => state.groupFolderTag,
      temporaryGroups: state => state.temporaryGroups,
      sceneCurrentGroup: state => state.sceneCurrentGroup,
      currentNeuronData: state => state.neuron.currentNeuronData,
      delDialogVisible: state => state.neuron.delDialogVisible,
      neuronListOperation: state => state.neuron.neuronListOperation,
      viewedNeurons: state => state.neuron.viewedNeurons,
      settingValues: state => state.settingValues,
      neuronColorScheme: state => state.neuron.colorScheme,
      pickedNeuronItem: state => state.PickedInformation.neuronItem,
      isBatchSetColor: state => state.neuron.isBatchSetColor,
      batchCurrentColor: state => state.neuron.batchCurrentColor,
      neuronRegionRelation: state => state.neuron.neuronRegionRelation,
      regionData: state => state.region.regionData
    }),

    ...mapGetters(["groupTips"]),

    deleteDialogVisible: {
      get() {
        return this.delDialogVisible;
      },
      set(newV) {
        this.$store.commit("neuron/setDelDialogVisible", newV);
      }
    },

    selectedNeuron() {
      return this.viewedNeuronsData.filter(el => el.selected);
    },

    selectAllIndeterminate() {
      return (
        this.selectedNeuron.length > 0 &&
        this.selectedNeuron.length !== this.viewedNeuronsData.length
      );
    },

    viewedNeuronsData() {
      if (this.sceneCurrentGroup?.id === "all") {
        return this.viewedNeurons;
      }
      return this.groupToNeurons.get(this.sceneCurrentGroup?.id) || [];
    },

    groupInfo() {
      const n = {
        id: this.groupTips,
        name: this.groupTips,
        disabled: true
      };
      const s = this.groups?.length ? this.groups : [n];
      const u = this.temporaryGroups?.length ? this.temporaryGroups : [n];
      return [
        { header: "My Saved group" },
        ...s,
        { header: "Unsaved group" },
        ...u
      ].filter(item => item?.id !== this.sceneCurrentGroup?.id);
    },

    operationDialogVisible: {
      get() {
        return this.neuronListOperation?.visible;
      },
      set(newV) {
        this.$store.commit("neuron/setNeuronListOperation", {
          ...this.neuronListOperation,
          visible: newV
        });
      }
    },

    lowerText() {
      return (
        this.neuronListOperation?.tag?.slice(0, 1).toLowerCase() +
        this.neuronListOperation?.tag?.slice(1)
      );
    },

    neuronFileName() {
      return Array.isArray(this.currentNeuronData)
        ? this.currentNeuronData.length
        : `'${this.currentNeuronData?.file}'`;
    },

    maxAllowedHeight() {
      // Compute the max allowed height: the smaller of viewport height and content height
      return Math.min(this.windowHeight - 250, this.maxContentHeight);
    }
  },

  watch: {
    viewedNeurons: {
      handler() {
        this.scrollHeight = Math.min(
          this.windowHeight - 250,
          this.viewedNeurons.length * 36
        );
        this.updateMaxHeight();
        // Precompute a group->neurons Map to avoid O(n) filter on group switch
        // Batch via rAF: rebuild only once during rapid consecutive pushes, avoiding O(n^2)
        if (!this._groupRebuildScheduled) {
          this._groupRebuildScheduled = true;
          requestAnimationFrame(() => {
            this._groupRebuildScheduled = false;
            this.groupMapSize = this.viewedNeurons.length;
            this.groupToNeurons.clear();
            for (const n of this.viewedNeurons) {
              const groups = n.groups;
              if (groups && groups.length) {
                for (const g of groups) {
                  if (!this.groupToNeurons.has(g.id)) {
                    this.groupToNeurons.set(g.id, []);
                  }
                  this.groupToNeurons.get(g.id).push(n);
                }
              }
            }
          });
        }
      }
    },

    selectedNeuron() {
      if (this.selectedNeuron.length == 0) {
        this.selectAll = false;
      }

      if (this.selectedNeuron.length == this.viewedNeuronsData.length) {
        this.selectAll = this.viewedNeuronsData.length > 0;
      }
    },

    pickedNeuronItem() {
      this.onNeuronItemClick(this.pickedNeuronItem, "fromPick");

      const currentSliceDiv = document.getElementById(
        this.pickedNeuronItem.file
      );
      if (currentSliceDiv) {
        this.$nextTick(() => {
          currentSliceDiv.scrollIntoView({ behavior: "smooth" });
        });
      }
    },

    neuronListOperation() {
      // if (this.neuronListOperation?.visible) {
      // }
    },

    batchCurrentColor() {
      const selectedNeurons = this.viewedNeurons.filter(el => el.selected);
      selectedNeurons.forEach(item => {
        this.onColorChanged(item, this.batchCurrentColor);
      });
    },

    delDialogVisible() {
      if (this.delDialogVisible) {
        this.deleteText = "";
        this.neuronDelAll = false;
        let groupName = this.sceneCurrentGroup?.name;
        this.deleteText = `Are you sure you want to delete the ${this.neuronFileName} neuron from group '${groupName}' ?`;

        this.isDeleteAllNeuron();
        this.neuronDelAll &&
          (this.deleteText +=
            "The group will be also deleted as it contains no neurons.");
      }
    }
  },

  methods: {
    isDeleteAllNeuron() {
      let sum = 0;
      // Find how many neurons this group has
      this.viewedNeuronsData.forEach(item => {
        const val = item?.groups?.find(
          g => g.id === this.sceneCurrentGroup?.id
        );
        if (val) sum++;
      });
      if (
        this.viewedNeuronsData.length === 1 ||
        sum === this.currentNeuronData.length
      ) {
        // Deleting the neuron will also delete this group
        this.neuronDelAll = true;
      }
    },

    onNeuronNameClick(item, tag) {
      console.log("click neuron name", item.file);
      // window.neuroViz.revertSelection();
      window.neuroViz.setSelection(item.file);

      this.lastActiveItem.actived = false;
      this.activeItem = item;
      this.activeItem.hovered = false;
      this.activeItem.actived = true;
      this.lastActiveItem = item;
      this.positionVisible = tag === "fromPick" ? true : false;
    },

    onNeuronItemClick(item, tag) {
      this.onNeuronNameClick(item, tag);
      this.infoItem = item;
      this.neuronInfoVisible = true;
      this.viewInfo = true;
      setTimeout(() => {
        this.viewInfo = false;
      }, 100);
    },

    itemClickOutside() {
      if (this.viewInfo && this.activeItem) return;
      window.neuroViz?.revertSelection();
      this.lastActiveItem.actived = false;
      this.activeItem = null;
    },

    closeNeuronInfo() {
      this.neuronInfoVisible = false;
      this.infoItem = null;
    },

    onSelectAllChanged() {
      const isAll = this.sceneCurrentGroup?.id == "all";
      this.viewedNeuronsData.forEach(element => {
        if (isAll) {
          element.selected = this.selectAll;
        } else {
          const curr = element?.groups?.find(
            g => g?.id === this.sceneCurrentGroup?.id
          );
          if (curr) element.selected = this.selectAll;
        }
      });
    },

    onChangeItemVisible(item) {
      item.visible = !item.visible;
      if (item.visible) {
        this.settingValues.mode &&
          window.neuroViz.setSWCPartVisibility(
            item?.file,
            true,
            true,
            true,
            true,
            true
          );
      }
      if (item.visible) {
        window.neuroViz.load(item.file);
      } else {
        window.neuroViz.unload(item.file);
      }

      // for rbm add/remove hi-res dendrites when neuron show/hide
      if (process.env.VUE_APP_SUB_SPECIES === "rbm" && item.dendritic) {
        if (item.visible) {
          this.$store.commit("addHighResDendrites", item.dendritic);
        } else {
          this.$store.commit("removeHighResDendrites", item.dendritic);
        }
      }
    },

    onDeleteItem(item) {
      window.neuroViz.unload(item.file);
      this.$store.commit("neuron/setIsRemoveSwc", true);
      this.$store.commit("neuron/removeViewedNeurons", [item]);

      if (this.infoItem?.file === item.file) {
        this.closeNeuronInfo();
      }

      if (this.activeItem?.file === item.file) {
        this.activeItem = null;
      }

      // for rbm remove hi-res dendrites when neuron removed
      if (process.env.VUE_APP_SUB_SPECIES === "rbm" && item.dendritic) {
        this.$store.commit("removeHighResDendrites", item.dendritic);
      }
    },

    onNeuronItemHovered(item) {
      this.hoveredNeuronItem = item;

      // display  single neuron operations at hovered item
    },

    computeNeuronColor(item) {
      // Batch mode, but other items that haven't been changed shouldn't change the same way
      if (this.isBatchSetColor && item?.batchColor) {
        return {
          background: item?.batchColor
        };
      }
      switch (this.neuronColorScheme) {
        case "random":
          return { background: item.idColor };
        case "mouseLine":
          return {
            background: item.typeColor
          };
        case "structure":
          return {
            background: "#7d7d7d"
          };
        case "region":
          return { background: item.regionColor };
        default:
          return {}; // default case if no color rule matches
      }
    },

    onColorChanged(item, value) {
      item.currentColor = value;
      // Batch changes are temporary and not recorded, so they must not overwrite other items' color
      if (this.isBatchSetColor && item.selected) {
        const rgb = hexToRgb(value).map(el => el / 255.0);
        item.batchColor = value;
        window.neuroViz.setColor(item.file, rgb);
        if (process.env.VUE_APP_SUB_SPECIES === "rbm" && item.dendritic) {
          this.$store.commit("addHighResDendritesColor", {
            id: (Math.random() * 100000).toFixed(0),
            file: item.dendritic,
            color: rgb
          });
        }

        return;
      }
      if (this.neuronColorScheme === "random") {
        item.idColor = value;
      } else if (this.neuronColorScheme === "region") {
        item.regionColor = value;
        // update region soma color
        const projectName = item.projectFullName;
        const relationItem = this.neuronRegionRelation[projectName][item.id];
        const somaArray = relationItem.owner_region_array;
        if (somaArray.length !== 0) {
          this.regionData[somaArray[somaArray.length - 1]].somaColor = value;
        }

        this.$store.commit("neuron/setUpdateNeuronColor", {
          type: "region",
          trigger: Math.random() * 100000
        });
      } else if (this.neuronColorScheme === "mouseLine") {
        item.typeColor = value;

        const neuronType = Array.isArray(item.type_array)
          ? item.type_array[0]
          : item.type_array;
        this.$store.commit("neuron/updateTypeColors", {
          key: neuronType,
          value
        });

        // update all the other loaded neurons'color with the same type
        this.viewedNeuronsData.forEach(neuron => {
          if (neuron.mouseLine === item.mouseLine) {
            neuron.typeColor = value;
            neuron.currentColor = value;
            const rgb = hexToRgb(value).map(el => el / 255.0);
            window.neuroViz.setColor(neuron.file, rgb);
          }
        });
      }

      const rgb = hexToRgb(value).map(el => el / 255.0);
      window.neuroViz.setColor(item.file, rgb);
      if (process.env.VUE_APP_SUB_SPECIES === "rbm" && item.dendritic) {
        this.$store.commit("addHighResDendritesColor", {
          id: (Math.random() * 100000).toFixed(0),
          file: item.dendritic,
          color: rgb
        });
      }
    },

    async operationGroupFunc() {
      // Both move and copy need to trigger this
      this.onCopyNeuron();
      if (this.neuronListOperation?.tag === "Move") {
        // Delete its own
        this.confirmDeleteGroup();
      }
      this.$store.commit("neuron/setNeuronListOperation", {
        ...this.neuronListOperation,
        visible: false
      });
    },

    async onCopyNeuron() {
      // Update the view
      const currentGroup = this.temporaryGroups.find(
        item => item.id === this.currentGroupId
      );
      if (currentGroup) {
        this.operationNeuronItem(currentGroup);
      } else {
        // save -> update group
        if (!this.groupsDetailData[this.currentGroupId]) {
          this.groupsDetailData[this.currentGroupId] = await getGroupDetailFunc(
            this.currentGroupId
          );
        }
        this.operationNeuronItem(this.groupsDetailData[this.currentGroupId]);

        await updateGroupFunc(
          this.currentGroupId,
          this.groupsDetailData[this.currentGroupId]
        );
        this.$store.dispatch("getGroups");
      }

      // Find out whether the selected group exists in the view
      const vals = this.viewedNeurons.find(item =>
        item.groups.find(g => g?.id === this.currentGroupId)
      );

      if (vals) {
        const groupTag = currentGroup
          ? {
              ...currentGroup,
              save: "unsave"
            }
          : {
              ...this.groups.find(item => item?.id === this.currentGroupId),
              save: "save"
            };
        [this.currentNeuronData].flat(1).forEach(item => {
          if (!item.groups) item.groups = [];
          item?.groups.push({
            id: groupTag.id,
            name: groupTag.name,
            save: groupTag.save
          });
        });
      }
    },

    delGroupsFunc(item) {
      item?.groups.forEach((g, i) => {
        if (g?.id === this.sceneCurrentGroup?.id) {
          item.groups.splice(i, 1);
        }
        if (!item.groups.length) item.groups = null;
      });
    },

    operationNeuronItem(groupDetail, func = "") {
      // Merge objects or arrays
      const vals = [this.currentNeuronData].flat(1);
      vals.forEach(item => {
        const result = groupDetail?.parts.find((f, i) => {
          if (f?.project === item?.project) {
            const index = f?.files?.findIndex(
              neuronName => neuronName === item.file
            );
            if (func === "delete") {
              if (index !== -1) {
                f?.files.splice(index, 1);
              }
              if (f?.files?.length === 0) groupDetail?.parts.splice(i, 1);
            } else {
              // move || copy
              if (index === -1) {
                f?.files.push(item.file);
              }
            }

            return true;
          }
          return false;
        });
        if (!result) {
          groupDetail?.parts.push({
            project: item.project,
            files: [item.file]
          });
        }
      });
    },

    delUnsaveNeuron() {
      if (this.neuronDelAll) {
        this.$store.commit(
          "setTemporaryGroups",
          this.temporaryGroups.filter(
            item => item.id !== this.sceneCurrentGroup?.id
          )
        );
        this.$store.commit("setSceneCurrentGroup", {
          name: "All neurons",
          id: "all"
        });
      } else {
        const groupDetail = this.temporaryGroups.find(
          item => item?.id === this.sceneCurrentGroup?.id
        );
        this.operationNeuronItem(groupDetail, "delete");
      }
    },

    async delSaveNeuron() {
      if (this.neuronDelAll) {
        await deleteGroupFunc(this.sceneCurrentGroup?.id);
        this.$store.commit("setSceneCurrentGroup", {
          name: "All neurons",
          id: "all"
        });
      } else {
        if (!this.groupsDetailData[this.sceneCurrentGroup?.id]) {
          this.groupsDetailData[
            this.sceneCurrentGroup?.id
          ] = await getGroupDetailFunc(this.sceneCurrentGroup?.id);
        }
        this.operationNeuronItem(
          this.groupsDetailData[this.sceneCurrentGroup?.id],
          "delete"
        );
        await updateGroupFunc(
          this.sceneCurrentGroup?.id,
          this.groupsDetailData[this.sceneCurrentGroup?.id]
        );
      }
      this.$store.dispatch("getGroups");
    },

    async confirmDeleteGroup() {
      // Update the group info in viewedNeurons
      [this.currentNeuronData].flat(1).forEach(item => {
        this.delGroupsFunc(item);
      });

      this.$store.commit("setGroupFolderTag", !this.groupFolderTag);

      if (this.sceneCurrentGroup?.save === "unsave") {
        // Unsaved -> update the left-side group content
        this.delUnsaveNeuron();
      } else if (this.sceneCurrentGroup?.save === "save") {
        // Saved -> update the left-side group content
        this.delSaveNeuron();
      }
      this.$store.commit("neuron/setDelDialogVisible", false);
    },

    initializeResizable() {
      const element = this.$refs.neuronList;
      if (!element) return;

      interact(element).resizable({
        edges: { bottom: true },
        listeners: {
          move: event => {
            let { y } = event.target.dataset;
            y = (parseFloat(y) || 0) + event.deltaRect.height;

            const newHeight = Math.max(85, Math.min(y, this.maxAllowedHeight));
            Object.assign(event.target.dataset, { y });
            this.scrollHeight = newHeight - this.listHeaderHeight; // this.listHeaderHeight is the header's height
          }
        },
        modifiers: [
          interact.modifiers.restrictSize({
            min: { height: 85 },
            max: { height: this.maxAllowedHeight }
          })
        ]
      });
    },

    hexToRgbaObj(hex) {
      const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})/i.exec(hex || "");
      if (!m) return { r: 255, g: 255, b: 255, a: 1 };
      return {
        r: parseInt(m[1], 16),
        g: parseInt(m[2], 16),
        b: parseInt(m[3], 16),
        a: 1
      };
    },

    onColorPickerInput(item, val) {
      let hex;
      if (val && typeof val === "object") {
        const r = Math.round(val.r || 0);
        const g = Math.round(val.g || 0);
        const b = Math.round(val.b || 0);
        hex =
          "#" +
          r.toString(16).padStart(2, "0") +
          g.toString(16).padStart(2, "0") +
          b.toString(16).padStart(2, "0");
      } else {
        hex = val;
      }
      this.onColorChanged(item, hex);
    },

    updateMaxHeight: debounce(function() {
      this.windowHeight = window.innerHeight;
      this.maxContentHeight =
        this.viewedNeurons.length * 36 + this.listHeaderHeight; // this.listHeaderHeight is the header's height
      this.scrollHeight = Math.min(
        this.windowHeight - 250,
        this.viewedNeurons.length * 36
      );

      this.$nextTick(() => {
        this.initializeResizable();
        // Update the element's actual style
        if (this.$refs.neuronList) {
          // this.$refs.neuronList.style.height = `${
          //   this.scrollHeight
          // }px`;
          this.$refs.neuronList.dataset.y = `${this.scrollHeight +
            this.listHeaderHeight}px`;
        }
      });
    }, 500)
  },

  mounted() {
    this.$nextTick(() => {
      this.updateMaxHeight();
    });
  },

  created() {
    window.addEventListener("resize", this.updateMaxHeight);
  },

  beforeDestroy() {
    window.removeEventListener("resize", this.updateMaxHeight);
  }
};
</script>

<style lang="scss" scoped>
.neuron-list {
  position: relative;
  min-height: 85px;
  overflow-y: auto; // Changed to auto to show a scrollbar when content overflows
  overflow-x: hidden; // Hide the horizontal scrollbar
}

.resize-handle {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 10px;
  cursor: ns-resize;
  background: rgba(255, 255, 255, 0.1);
}

.operation-dialog {
  height: 136px;
  background: #151c2d;

  .operation-text {
    margin: 0;
    color: #ced4e4;
    font-size: 13px;
  }
  :deep {
    .v-select__selection--comma {
      margin: 7px;
    }
    .v-select__selections input {
      display: none;
    }
    .v-select__slot {
      padding-left: 0;
    }
  }
}

.delete-dialog {
  height: 108px;
  display: flex;
  align-items: flex-start;
  padding: 4px;
  gap: 10px;
  flex: 1 0 0;
  align-self: stretch;
  color: #ced4e4;
  font-family: Roboto;
  font-size: 13px;
}

.border-style {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  border: 1px solid;
}

.hover-border {
  border-color: #343f5c;
}

.active-border {
  border-color: #7fbefa;
}

.v-virtual-scroll {
  max-height: calc(100vh - 320px);
}

:deep(.v-input--selection-controls__input) {
  width: 16px !important;
  height: 16px !important;
  margin: 0 !important;
}
:deep(.v-input--checkbox) {
  padding: 0 !important;
  margin: 0 !important;
}

:deep(.v-input__control) {
  padding: 0 !important;
}
:deep(.v-icon.v-icon::after) {
  display: none;
}

:deep(.v-text-field > .v-input__control > .v-input__slot:before) {
  border: none;
}
</style>

<style>
/* Color picker popup — non-scoped so it targets the teleported menu content */
.neuron-color-picker-menu .v-color-picker__alpha {
  display: none !important;
}
.neuron-color-picker-menu
  .v-color-picker__edit
  .v-color-picker__input:nth-last-child(2) {
  display: none !important;
}
.neuron-color-picker-menu .v-color-picker__edit > button {
  display: none !important;
}
.neuron-color-picker-menu .v-color-picker__dot {
  width: 44px !important;
  height: 44px !important;
  border-radius: 50% !important;
  flex-shrink: 0;
}
.neuron-color-picker-menu .v-color-picker__input input {
  background: #2a2a2a;
  border: 1px solid #3a3a3a;
  border-radius: 6px;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  text-align: center;
  padding: 6px 4px;
}
.neuron-color-picker-menu .v-color-picker__input span {
  color: #888;
  font-size: 11px;
  letter-spacing: 0.05em;
}
</style>
