<template>
  <div class="data-group">
    <save-neuron
      @renameGroup="renameGroup"
      @editGroup="editGroup"
      @toolTipFunc="toolTipFunc"
    ></save-neuron>
    <unsave-neuron
      @renameGroup="renameGroup"
      @editGroup="editGroup"
      @toolTipFunc="toolTipFunc"
    ></unsave-neuron>

    <a-dialog
      :visible.sync="editDialogVisible"
      width="460"
      @confirm="confirmEditGroup"
      title="Edit Group"
      cancelbtnText="Cancel"
      surebtnText="Save"
      :footerVisible="false"
    >
      <div class="edit-dialog">
        <p style="margin: 0">Group:{{ operationGroup?.name }}</p>
        <div class="edit-search">
          <div class="edit-search-icon">
            <v-icon size="16">$Search</v-icon>
          </div>
          <input
            type="text"
            placeholder="Search neurons"
            v-model.trim="neuronVal"
          />
        </div>

        <div class="d-flex align-center" style="height: 36px; margin: 0 11px">
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
          <span style="flex-grow: 1"
            >select {{ selectedNeuron.length }} neuron</span
          >

          <div class="bg-icon" style="height: 24px" @click="onDeleteAll">
            <delete fill="#7FBEFA"></delete>
          </div>

          <div class="edit-del" v-show="delAllDialogVisible">
            <span class="edit-del-text">
              {{ delAllText }}
            </span>

            <div class="d-flex justify-end">
              <span
                class="dialog-button cancel-button"
                @click="delAllDialogVisible = false"
              >
                <close fill="#A5ABB9"></close>
              </span>
              &nbsp;
              <span
                class="dialog-button confirm-button"
                @click="onDeleteAllJudge"
              >
                <check fill="#ffffff"></check>
              </span>
            </div>
          </div>
        </div>

        <v-virtual-scroll
          :items="groupNeuronsData"
          max-height="324"
          item-height="36"
          :bench="324 / 36 + 1"
        >
          <template v-slot:default="{ item }">
            <div class="edit-group-item">
              <v-checkbox
                hide-details
                dense
                :ripple="false"
                color="#7fbefa"
                v-model="item.selected"
              ></v-checkbox>

              <span class="op-85" style="flex-grow: 1">{{
                item.file.slice(0, -4)
              }}</span>

              <!-- <div class="bg-icon edit-copy-icon" style="height: 24px" @click="onCopyItem(item)">
                <copy
                  style="cursor: pointer"
                  fill="#7FBEFA"
                ></copy>
              </div> 
              -->
              <div
                class="bg-icon"
                style="height: 24px"
                @click="delVisibleFunc(item)"
              >
                <delete style="cursor: pointer" fill="#7FBEFA"></delete>
              </div>
              <div class="edit-del" v-show="item.deleted">
                <span class="edit-del-text">{{ delText }}</span>

                <div class="d-flex justify-end">
                  <span
                    class="dialog-button cancel-button"
                    @click="item.deleted = false"
                  >
                    <close fill="#A5ABB9"></close>
                  </span>
                  &nbsp;
                  <span
                    class="dialog-button confirm-button"
                    @click="onDeleteItemConfirm(item)"
                  >
                    <check fill="#ffffff"></check>
                  </span>
                </div>
              </div>
            </div>
          </template>
        </v-virtual-scroll>
      </div>
    </a-dialog>
  </div>
</template>

<script>
import { mapState } from "vuex";
import ADialog from "@/components/ADialog";
// import Copy from "@/components/icons/Copy";
import Close from "@/components/icons/Close";
import Check from "@/components/icons/Check";
import Delete from "@/components/icons/Delete";
import SaveNeuron from "./components/SaveNeuron.vue";
import UnsaveNeuron from "./components/UnsaveNeuron.vue";
import { updateGroupFunc, deleteGroupFunc } from "@/api/group";
import { deepClone } from "@/utils/utils";
export default {
  name: "DataGroup",
  components: {
    ADialog,
    Close,
    Check,
    Delete,
    SaveNeuron,
    UnsaveNeuron
  },
  data() {
    return {
      selectAll: false,
      editDialogVisible: false,
      neuronVal: "",
      operationGroup: null,
      groupNeurons: [],
      delAllDialogVisible: false
    };
  },
  watch: {
    selectedNeuron() {
      if (this.selectedNeuron.length == 0) {
        this.selectAll = false;
      }

      if (this.selectedNeuron.length == this.groupNeuronsData.length) {
        this.selectAll = this.groupNeuronsData.length > 0;
      }
    }
  },
  computed: {
    ...mapState({
      groups: state => state.groups,
      groupFolderTag: state => state.groupFolderTag,
      temporaryGroups: state => state.temporaryGroups,
      currentChooseGroup: state => state.neuron.currentChooseGroup,
      filteredNeurons: state => state.neuron.filteredNeurons,
      viewedNeurons: state => state.neuron.viewedNeurons
    }),

    delAllText() {
      return this.selectedNeuron?.length === this.groupNeurons?.length
        ? "Are you sure to delete? The group will be also deleted."
        : `Are you sure to delete these ${this.selectedNeuron?.length} neurons?`;
    },

    delText() {
      return this.groupNeuronsData.length > 1
        ? "Are you sure to delete? "
        : "Are you sure to delete? With the remaining neuron, deleting this group will also be deleted";
    },

    selectAllIndeterminate() {
      return (
        this.selectedNeuron.length > 0 &&
        this.selectedNeuron.length !== this.groupNeurons.length
      );
    },

    groupNeuronsData() {
      return this.groupNeurons.filter(el => el?.file.includes(this.neuronVal));
    },

    selectedNeuron() {
      return this.groupNeurons.filter(el => el.selected);
    }
  },
  methods: {
    onSelectAllChanged() {
      this.groupNeuronsData.forEach(element => {
        element.selected = this.selectAll;
      });
    },

    delVisibleFunc(item) {
      this.groupNeuronsData.forEach(g => {
        g.deleted = false;
      });
      item.deleted = true;
    },

    confirmEditGroup() {
      this.editDialogVisible = false;
    },

    editGroup(...val) {
      val[0].save = val[1];
      this.operationGroup = val[0];
      this.groupNeurons = [];

      val[0]?.parts?.forEach(n => {
        n?.files?.forEach(file => {
          this.groupNeurons.push({
            project: n.project,
            file,
            selected: false,
            deleted: false
          });
        });
      });

      this.editDialogVisible = true;
    },

    async onDeleteAll() {
      if (this.selectedNeuron.length) this.delAllDialogVisible = true;
    },

    async onDeleteAllJudge() {
      const isAll = this.selectedNeuron?.length === this.groupNeurons?.length;

      if (isAll) {
        await this.onDeleteAllConfirm();
      } else {
        const curr = deepClone(this.selectedNeuron);
        for (let i = 0; i < curr?.length; i++) {
          const item = curr[i];
          await this.onDeleteItemConfirm(item);
        }
      }
      this.delAllDialogVisible = false;
    },

    async onDeleteAllConfirm() {
      // Should be equivalent to deleting this group
      if (this.operationGroup.save === "unsave") {
        this.$store.commit(
          "setTemporaryGroups",
          this.temporaryGroups.filter(
            item => item.id !== this.operationGroup.id
          )
        );
      } else {
        await deleteGroupFunc(this.operationGroup.id);
        // this.$store.commit(
        //   "setGroups",
        //   this.groups.filter((item) => item.id !== this.operationGroup.id)
        // );
        this.$store.dispatch("getGroups");
      }
      this.groupNeurons = [];
      this.editDialogVisible = false;
      this.delAllDialogVisible = false;
      this.updateNeuronList("all");
      this.$store.commit("setGroupFolderTag", !this.groupFolderTag);
    },

    async onDeleteItemConfirm(item) {
      const parts = this.operationGroup.parts;
      parts.some((g, index) => {
        if (g.project === item.project) {
          g.files = g.files.filter(f => f !== item.file);
          if (g.files?.length === 0) {
            parts.splice(index, 1);
          }
          return true;
        }
      });

      if (!parts || parts?.length == 0) {
        this.onDeleteAllConfirm();
        return;
      }

      if (this.operationGroup.save !== "unsave") {
        await updateGroupFunc(this.operationGroup.id, {
          name: this.operationGroup?.name,
          species: this.operationGroup?.species,
          parts: parts
        });
        this.$store.dispatch("getGroups");
      }
      this.groupNeurons = this.groupNeurons.filter(g => g.file !== item.file);
      this.updateNeuronList("once", item);
    },

    renameGroup(group) {
      // Many neurons may belong to a given group, so use forEach
      this.viewedNeurons.forEach(item => {
        const cur = item.groups?.find(g => g.id === group.id);
        if (cur) cur.name = group.name;
      });
    },

    updateNeuronList(tag, curr) {
      // Here there is only one neuron, so use some
      this.viewedNeurons.some(item => {
        const index = item.groups?.findIndex(
          g => g.id === this.operationGroup.id
        );

        if (index !== -1) {
          if (tag === "all") {
            item.groups.splice(index, 1);
            return;
          }
          if (item.file === curr.file) {
            item.groups.splice(index, 1);
            return true;
          }
        }
      });
    },

    toolTipFunc(...vals) {
      this.$store.commit("setToolTipType", vals[0]);
      this.$store.commit("setToolTipMessage", vals[1]);
      this.$store.commit("setToolTipVisible", vals[2]);
    }
  },
  mounted() {}
};
</script>

<style lang="scss">
.v-virtual-scroll__item {
  height: 36px;
}

.group-tips {
  display: flex;
  height: 36px;
  padding: 0px 10px;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  color: #7f8490;
  font-size: 13px;
}

.data-group {
  display: flex;
  flex-direction: column;
  padding: 10px;
  overflow-y: auto;
  overflow-x: hidden;
  height: calc(100vh - 92px);
  .save-groups-item {
    position: relative;
    display: flex;
    width: 100%;
    height: 36px;
    padding: 0px 10px;
    justify-content: space-between;
    align-items: center;

    &:hover {
      background: #283652;

      .item-menu {
        visibility: visible !important;
      }
    }

    .item-left {
      flex: 1;
      width: 85%;
      height: 100%;
      display: flex;
      align-items: center;

      .item-name {
        margin: 0 5px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .item-count {
        display: flex;
        font-size: 12px;
        font-weight: 400;
        color: #ced4e4;
        padding: 2px 6px;
        flex-direction: column;
        align-items: center;
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.2);
      }

      .item-shared {
        display: flex;
        height: 20px;
        padding: 10px 8px;
        justify-content: center;
        align-items: center;
        gap: 10px;
        border-radius: 28px;
        border: 1px solid rgba(52, 210, 49, 0.5);
        background: rgba(52, 210, 49, 0.1);
        margin: 0 5px;
        color: #3de33a;
        font-family: Roboto;
        font-size: 12px;
        font-style: normal;
        font-weight: 400;
        line-height: normal;
      }
    }

    .item-right {
      display: flex;
      position: relative;

      .item-menu {
        margin-right: 5px;
        visibility: hidden;
      }
    }
  }

  .edit-name {
    display: flex;
    height: 24px;
    line-height: 24px;
    padding: 0px 4px;
    align-items: center;
    flex: 1 0 0;
    background: #151c2d;
    color: #f5f8ff;
    margin-left: 5px;
  }
}

.filter-header {
  display: flex;
  align-items: center;
  margin: 10px 0;
}

.share-dialog,
.shared-dialog {
  height: 208px;
}

.edit-dialog {
  height: 470px;
  .edit-search {
    display: flex;
    align-items: center;
    margin: 16px 0;
    padding: 5px 10px;
    width: 100%;
    color: #ced4e4;
    height: 32px;
    gap: 5px;
    border-radius: 2px;
    border: 1px solid #343f5c;

    .edit-search-icon {
      height: 32px;
      transform: translateY(4px);
    }
    input {
      font-size: 13px;
      color: #ffffff;
    }
  }
  .v-input--checkbox {
    margin: 0 !important;
    padding: 0 !important;
  }
  .edit-group-item {
    height: inherit;
    display: flex;
    align-items: center;
    padding: 0 10px;
    border: 1px solid transparent;
    .edit-copy-icon {
      visibility: hidden;
    }
    &:hover {
      border-color: #343f5c;
      .edit-copy-icon {
        visibility: visible;
      }
    }
  }
  .edit-del {
    position: fixed;
    transform: translate(441px, 33px);
    display: flex;
    width: 180px;
    padding: 10px;
    flex-direction: column;
    justify-content: center;
    border-radius: 2px;
    background: #151c2d;
    box-shadow: 0px 0px 12px 0px rgba(0, 0, 0, 0.5);
    .edit-del-text {
      color: #ced4e4;
      font-family: Roboto;
      font-size: 13px;
      font-style: normal;
      font-weight: 400;
      line-height: normal;
      margin-bottom: 10px;
    }
  }
}

.shared-link-location {
  flex: 1;
  display: flex;
  height: 36px;
  padding: 5px 10px;
  margin-right: 10px;
  align-items: center;
  gap: 10px;
  flex: 1 0 0;
  border-radius: 2px;
  border: 1px solid var(--StrokeLine, #343f5c);

  span {
    color: var(--dark, #ced4e4);

    /* Roboto/regular-14 */
    font-family: Roboto;
    font-size: 13px;
    font-style: normal;
    font-weight: 400;
    line-height: normal;
  }
}

.shared-link-btn {
  width: 105px;
  display: flex;
  height: 36px;
  padding: 6px 14px;
  justify-content: center;
  align-items: center;
  gap: 4px;
  border-radius: 2px;
  background: #2d68c3;
  white-space: nowrap;

  &:hover {
    background: #3f7ddc !important;
  }

  span {
    color: var(--, #fff);
    text-align: center;

    /* Roboto/regular-14 */
    font-family: Roboto;
    font-size: 13px;
    font-style: normal;
    font-weight: 400;
    line-height: normal;
  }

  &:hover {
    cursor: pointer;
  }
}

.share-cancel-btn {
  width: 150px;
  display: flex;
  height: 24px;
  padding: 6px 14px;
  justify-content: center;
  align-items: center;
  gap: 4px;
  border-radius: 2px;
  border: 1px solid #dc6060;
  margin-left: 10px;
  span {
    color: #dc6060;
    text-align: center;

    /* Roboto/regular-14 */
    font-family: Roboto;
    font-size: 13px;
    font-style: normal;
    font-weight: 400;
    line-height: normal;
  }

  &:hover {
    cursor: pointer;
  }
}

.delete-dialog {
  height: 108px;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  flex: 1 0 0;
  align-self: stretch;
}

.share-item {
  height: 40px;
  padding: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--dark, #a5abb9);
  font-size: 13px;
  font-weight: 400;
  margin-bottom: 20px;
  border: 1px solid var(--StrokeLine, #343f5c);
}

input:focus {
  outline: none;
}

input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.active-share-item {
  border: 1px solid var(--dark-2, #7fbefa);
  color: var(--dark, #ced4e4);
}

::v-deep {
  .v-input--selection-controls__input {
    margin-right: 0;
  }

  .v-input--selection-controls {
    margin-top: 0;
    padding-top: 8px;
  }
}

:deep(.v-input--checkbox) {
  margin: 0 !important;
  padding: 0 !important;
}
</style>
