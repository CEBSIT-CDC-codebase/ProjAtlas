<template>
  <div>
    <div class="filter-header">
      <span class="accent-1--text" style="font-size: 16px; font-weight: 500">
        Temporary neuron group
      </span>
      <div
        class="accent-3"
        style="height: 1px; flex-grow: 1; margin-left: 10px"
      ></div>
      <div
        style="
          width: 24px;
          height: 24px;
          border: 1px solid #343f5c;
          border-radius: 2px;
          cursor: pointer;
          display: flex;
          margin-left: 10px;
          align-items: center;
          justify-content: center;
        "
        @click="showtemporaryGroups = !showtemporaryGroups"
      >
        <v-icon
          size="16"
          :style="{
            transform: this.showtemporaryGroups
              ? 'rotate(0deg)'
              : 'rotate(180deg)'
          }"
          >$ArrowDown</v-icon
        >
      </div>
    </div>

    <div v-show="!showtemporaryGroups" style="margin: 10px 0">
      <div
        class="d-flex align-center"
        style="justify-content: center; cursor: pointer"
        @click="showtemporaryGroups = true"
      >
        <v-icon size="16" style="margin-right: 6px">$Expand</v-icon>
        <span
          class="primary-light--text"
          style="font-size: 13px; font-weight: 400"
          >Expand hidden groups...</span
        >
      </div>
    </div>

    <div v-show="showtemporaryGroups">
      <div class="save-groups" v-if="temporaryGroups?.length">
        <div
          class="save-groups-item"
          v-for="group in temporaryGroups"
          :key="group.name"
          :style="groupsItemStyle(group)"
        >
          <div class="item-left">
            <!-- <v-checkbox
            :style="{
              visibility: isRenameItemStatus(group) ? 'hidden' : 'visible'
            }"
            hide-details
            dense
            :ripple="false"
            color="#7fbefa"
            :value="group"
            v-model="checkGroups"
          ></v-checkbox> -->
            <v-icon size="16" class="ml-2">$Folder</v-icon>
            <input
              type="text"
              class="edit-name"
              v-show="isRenameItemStatus(group)"
              v-model="temporaryGroupsItemName"
            />
            <span class="item-name" v-show="!isRenameItemStatus(group)">
              {{ group.name }}
            </span>
            <span class="item-count" v-show="!isRenameItemStatus(group)">
              {{ group.count || getGroupFilesLength(group?.parts) }}
            </span>
          </div>
          <div class="item-right">
            <div
              v-show="isRenameItemStatus(group)"
              class="bg-icon"
              @click="onRenameCancel(group)"
            >
              <v-icon size="16">$Close</v-icon>
            </div>
            <div
              v-show="isRenameItemStatus(group)"
              class="bg-icon"
              @click="onRenameSubmit(group)"
            >
              <v-icon size="16">$Check</v-icon>
            </div>

            <v-menu offset-y v-show="group.operation">
              <template v-slot:activator="{ on, attrs }">
                <div
                  v-bind="attrs"
                  v-on="on"
                  class="bg-icon item-menu"
                  v-show="!isRenameItemStatus(group)"
                  @click="onOperationFunc($event, group)"
                >
                  <v-icon size="16">$Menu</v-icon>
                </div>
              </template>
              <v-list>
                <v-list-item @click="onRenameFunc(group)">
                  <v-icon size="16">$EditName</v-icon>
                  <span class="item-text">Rename the group</span>
                </v-list-item>
                <v-list-item @click="onEditFunc(group)">
                  <v-icon size="16">$Edit</v-icon>
                  <span class="item-text">Edit the group</span>
                </v-list-item>
                <v-list-item @click="onCopyFunc(group)">
                  <v-icon size="16">$Copy</v-icon>
                  <span class="item-text">Copy the group</span>
                </v-list-item>
                <v-list-item @click="onDeleteFunc(group)">
                  <v-icon size="16">$Delete</v-icon>
                  <span class="item-text">Delete the group</span>
                </v-list-item>
              </v-list>
            </v-menu>

            <!-- <menu-operation
              :style="group.menuPosition"
              :visible="group.operation"
              @clickOutside="group.operation = false"
              @rename="onRenameFunc(group)"
              @edit="onEditFunc(group)"
              @copy="onCopyFunc(group)"
              @delete="onDeleteFunc(group)"
            ></menu-operation> -->

            <div
              class="bg-icon item-share"
              v-show="!isRenameItemStatus(group)"
              @click="onSaveFunc(group)"
            >
              <v-icon size="16">$Save</v-icon>
            </div>
          </div>
        </div>
      </div>

      <div class="group-tips" v-else>None</div>
    </div>

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
        <span>
          Are you sure you want to delete the '{{ operationGroup?.name }}'
          group?
        </span>
      </div>
    </a-dialog>

    <a-dialog
      :visible.sync="saveDialogVisible"
      width="320"
      @confirm="confirmSaveGroup"
      title="Save Group"
      cancelbtnText="Cancel"
      surebtnText="Save"
      :footerVisible="true"
    >
      <div class="save-dialog">
        <p>Group name</p>
        <input type="text" v-model="temporaryGroupsItemName" />
      </div>
    </a-dialog>
  </div>
</template>

<script>
import { mapState } from "vuex";
import ADialog from "@/components/ADialog";
// import MenuOperation from "@/components/MenuOperation";
import { createOrCopyGroupFunc } from "@/api/group";
export default {
  name: "UnsaveNeuron",

  components: {
    ADialog
    // MenuOperation,
  },

  data() {
    return {
      saveDialogVisible: false,
      deleteDialogVisible: false,
      showtemporaryGroups: true,
      renameStatus: false,
      temporaryGroupsItemName: "",
      operationGroup: null,
      checkGroups: [],
      neuronVal: "",
      menuMaxHeight: 128
    };
  },

  computed: {
    ...mapState({
      userInfo: state => state.userInfo,
      groups: state => state.groups,
      groupFolderTag: state => state.groupFolderTag,
      groupToScene: state => state.groupToScene,
      unsaveToScene: state => state.unsaveToScene,
      temporaryGroups: state => state.temporaryGroups,
      unSaveSceneGroups: state => state.unSaveSceneGroups,
      viewedNeurons: state => state.neuron.viewedNeurons,
      filteredNeurons: state => state.neuron.filteredNeurons,
      filteredSelected: state => state.neuron.filteredSelected,
      selectionRevision: state => state.neuron.selectionRevision,
      visualTarget: state => state.visualTarget
    }),

    selectedResult() {
      void this.selectionRevision;
      const selected = this.filteredSelected;
      if (!selected || selected.size === 0) return [];
      // lazy import-free: key format project::file
      return this.filteredNeurons.filter(el =>
        selected.has(`${el.project || el.projectFullName || ""}::${el.file || ""}`)
      );
    },

    disabledBtnTag() {
      return this.selectedResult?.length === 0 ? "disabled-button" : null;
    },

    operationGroupName: {
      get() {
        return this.operationGroup?.name;
      },
      set(newV) {
        this.operationGroup.name = newV;
      }
    }
  },
  watch: {
    checkGroups() {
      this.$store.commit("setUnSaveSceneGroups", [...this.checkGroups]);
    },

    groupToScene() {
      this.checkGroups = [];
    },

    unsaveToScene() {
      this.checkGroups.push(
        this.temporaryGroups[this.temporaryGroups.length - 1]
      );
    }
  },

  methods: {
    groupsItemStyle(group) {
      if (this.operationGroup?.id === group?.id && this.renameStatus) {
        return {
          background: "#283652"
        };
      }
    },

    isRenameItemStatus(group) {
      if (this.renameStatus === true && this.operationGroup?.id === group?.id) {
        return true;
      }
      return false;
    },

    getGroupFilesLength(parts) {
      let len = 0;
      parts?.forEach(item => {
        len += item.files.length;
      });
      return len;
    },

    onOperationFunc(e, group) {
      const val = e.target.getBoundingClientRect();
      const topVal = 30;
      if (val.top + topVal + this.menuMaxHeight > window.innerHeight) {
        group.menuPosition = {
          bottom: "30px",
          top: "unset"
        };
      }
      group.operation = true;
    },

    onSaveFunc(group) {
      if (this.userInfo) {
        this.renameStatus && (this.renameStatus = false);
        this.operationGroup = group;
        this.temporaryGroupsItemName = group.name;
        this.saveDialogVisible = true;
      } else {
        this.$store.commit("setLoginFlag", true);
      }
    },

    onRenameCancel(group) {
      this.operationGroup.name = group.name;
      this.renameStatus = false;
    },

    async onRenameSubmit(group) {
      if (this.temporaryGroupsItemName.length > 50) {
        this.$store.commit("setToolTipType", "error");
        this.$store.commit(
          "setToolTipMessage",
          "group name length should <= 50"
        );
        this.$store.commit("setToolTipVisible", true);
        return;
      }

      if (this.temporaryGroupsItemName !== group.name) {
        const tag_name = this.temporaryGroups.some(
          item => this.temporaryGroupsItemName === item.name
        );
        if (tag_name) {
          this.$emit(
            "toolTipFunc",
            "error",
            "An unsaved group cannot have the same name",
            true
          );
        } else {
          // This is a reference assignment, so direct assignment works here
          this.operationGroup.name = this.temporaryGroupsItemName;
          this.renameStatus = false;
        }
        this.$emit("renameGroup", group);
      }
    },

    onRenameFunc(group) {
      this.renameStatus = true;
      this.operationGroup = group;
      this.temporaryGroupsItemName = group.name;
      this.operationGroup.operation = false;
    },

    onEditFunc(group) {
      this.operationGroup = { ...group };
      this.$emit("editGroup", group, "unsave");
    },

    onCopyFunc(group) {
      this.$store.commit("setTemporaryGroups", [
        ...this.temporaryGroups,
        {
          id: group.name + " copy",
          name: group.name + " copy",
          species: this.visualTarget,
          selected: false,
          operation: false,
          parts: group.parts
        }
      ]);
      group.operation = false;
    },

    onDeleteFunc(group) {
      this.operationGroup = { ...group };
      this.deleteDialogVisible = true;
    },

    confirmDeleteGroup() {
      this.removetemporaryGroupsFunc();
      this.$emit("toolTipFunc", "success", "Delete successfully!", true);

      this.deleteDialogVisible = false;
    },

    removetemporaryGroupsFunc() {
      const index = this.temporaryGroups.findIndex(
        item => item.name === this.operationGroup.name
      );
      this.$store.commit("setTemporaryGroups", [
        ...this.temporaryGroups.slice(0, index),
        ...this.temporaryGroups.slice(index + 1)
      ]);
    },

    async confirmSaveGroup() {
      if (this.userInfo) {
        const tag = this.temporaryGroups.some(
          item =>
            // No duplicate && excludes the current one
            this.temporaryGroupsItemName !== this.operationGroup.name &&
            this.temporaryGroupsItemName === item.name
        );
        if (tag) {
          this.$store.commit("setToolTipType", "error");
          this.$store.commit(
            "setToolTipMessage",
            "An unsaved group cannot have the same name"
          );
          this.$store.commit("setToolTipVisible", true);
        } else {
          // This is a reference assignment, so direct assignment works here
          this.operationGroup.name = this.temporaryGroupsItemName;
          await createOrCopyGroupFunc({
            name: this.temporaryGroupsItemName,
            species: this.visualTarget,
            parts: this.operationGroup.parts
          });
          this.removetemporaryGroupsFunc();
          await this.$store.dispatch("getGroups");
          this.saveDialogVisible = false;
          this.viewedNeurons.forEach(item => {
            let val = item?.groups?.find(g => g.id === this.operationGroup.id);
            if (val) {
              val.save = "save";
              val.id = this.groups[this.groups.length - 1]?.id;
              val.name = this.groups[this.groups.length - 1]?.name;
            }
          });
          this.$store.commit("setGroupFolderTag", !this.groupFolderTag);
          // Add to groups, remove from unsave
        }
      } else {
        this.saveDialogVisible = false;
        this.$store.commit("setLoginFlag", true);
      }
    }
  }
};
</script>

<style lang="scss" scoped>
:deep {
  .v-input--checkbox {
    margin: 0 !important;
    padding: 0 !important;
  }
  // input:focus {
  //   outline: auto;
  // }
}

.save-dialog {
  height: 118px;
  color: #ced4e4;

  input {
    width: 100%;
    display: flex;
    color: #ced4e4;
    height: 32px;
    padding: 5px 10px;
    align-items: center;
    gap: 5px;
    align-self: stretch;
    border-radius: 2px;
    border: 1px solid var(--StrokeLine, #343f5c);
  }
}

.item-text {
  font-size: 13px;
  margin-left: 8px;
  color: var(--dark, #ced4e4);
}

.v-list {
  border-radius: 2px;
  background: var(--BG-, #303c56);
  box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.5);
  width: 220px;
  padding: 0;
}

.v-list-item {
  min-height: 32px;
  max-height: 32px;
  padding: 10px;
}
</style>
