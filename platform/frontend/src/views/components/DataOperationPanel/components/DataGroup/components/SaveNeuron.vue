<template>
  <div>
    <div class="filter-header">
      <span class="accent-1--text" style="font-size: 16px; font-weight: 500">
        Custom neuron group
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
        @click="showSaveGroups = !showSaveGroups"
      >
        <v-icon
          size="16"
          :style="{
            transform: this.showSaveGroups ? 'rotate(0deg)' : 'rotate(180deg)'
          }"
          >$ArrowDown</v-icon
        >
      </div>
    </div>

    <div v-show="!showSaveGroups" style="margin: 10px 0">
      <div
        class="d-flex align-center"
        style="justify-content: center; cursor: pointer"
        @click="showSaveGroups = true"
      >
        <v-icon size="16" style="margin-right: 6px">$Expand</v-icon>
        <span
          class="primary-light--text"
          style="font-size: 13px; font-weight: 400"
          >Expand hidden groups...</span
        >
      </div>
    </div>

    <div v-show="showSaveGroups">
      <div class="save-groups" v-if="groups?.length">
        <div
          class="save-groups-item"
          v-for="group in groups"
          :key="group.id"
          :style="groupsItemStyle(group)"
        >
          <div class="item-left">
            <!-- <v-checkbox
            hide-details
            :style="{
              visibility: isRenameItemStatus(group) ? 'hidden' : 'visible'
            }"
            dense
            :ripple="false"
            color="#7fbefa"
            :value="group.id"
            v-model="checkGroupsIds"
          ></v-checkbox> -->
            <v-icon size="16" class="ml-2">$FolderSaved</v-icon>
            <input
              type="text"
              class="edit-name"
              v-show="isRenameItemStatus(group)"
              v-model="operationItemName"
            />
            <span class="item-name" v-show="!isRenameItemStatus(group)">
              {{ group?.name }}
            </span>
            <span class="item-count" v-show="!isRenameItemStatus(group)">
              {{ group?.count }}
            </span>
            <div class="item-shared" v-show="isSharedGroup(group)">Shared</div>
            <lock style="margin-left: 5px" v-show="group?.locked"></lock>
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
            <!-- <div
            v-show="group?.locked"
            class="bg-icon item-menu"
            @click="onMenuFunc(group)"
          >
            <lock fill="#7FBEFA"></lock>
          </div> -->

            <v-menu offset-y v-show="menuGroupsVisible[group?.id]">
              <template v-slot:activator="{ on, attrs }">
                <div
                  v-show="!isRenameItemStatus(group)"
                  class="bg-icon item-menu"
                  v-bind="attrs"
                  v-on="on"
                  @click="onMenuFunc(group)"
                >
                  <v-icon size="16">$Menu</v-icon>
                </div>
              </template>
              <v-list>
                <v-list-item
                  @click="onRenameFunc(group)"
                  v-show="!group?.locked"
                >
                  <v-icon size="16">$EditName</v-icon>
                  <span class="item-text">Rename the group</span>
                </v-list-item>
                <v-list-item @click="onEditFunc(group)" v-show="!group?.locked">
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
              :lockStatus="group?.locked"
              :visible="menuGroupsVisible[group?.id]"
              @clickOutside="menuGroupsVisible[group?.id] = false"
              @rename="onRenameFunc(group)"
              @edit="onEditFunc(group)"
              @copy="onCopyFunc(group)"
              @delete="onDeleteFunc(group)"
            ></menu-operation> -->
            <div
              v-show="!isRenameItemStatus(group)"
              class="bg-icon item-share"
              @click="onShareFunc(group)"
            >
              <v-icon size="16">$Share</v-icon>
            </div>
          </div>
        </div>
      </div>
      <div class="group-tips" v-else>{{ currentGroupTips }}</div>
    </div>

    <a-dialog
      :visible.sync="shareDialogVisible"
      @confirm="confirmShareGroup"
      width="460"
      title="Share Data Group"
      cancelbtnText="Cancel"
      surebtnText="Share"
      :footerVisible="true"
    >
      <div class="share-dialog">
        <p style="margin-bottom: 20px">
          Anyone with the link can view the group.
        </p>
        <div
          class="share-item"
          @click="shareGroupValue = 'lock'"
          :class="shareGroupValue === 'lock' ? 'active-share-item' : ''"
        >
          <label class="radio-container"
            >Lock the current status of the group and share it
            <input
              type="radio"
              name="share"
              value="lock"
              v-model="shareGroupValue"
            />
            <span class="checkmark"></span>
          </label>

          <v-menu offset-y min-width="250" open-on-hover>
            <template v-slot:activator="{ on, attrs }">
              <div v-bind="attrs" v-on="on">
                <v-icon size="16" class="help-cirle">$HelpCircle</v-icon>
              </div>
            </template>
            <v-list style="height: 80px; width: 250px">
              <v-list-item style="min-height: 80px; width: 250px">
                <div class="help-info">
                  It means that any future changes in the group will not be
                  applied to the link.
                </div>
              </v-list-item>
            </v-list>
          </v-menu>
        </div>
        <div
          class="share-item"
          @click="shareGroupValue = 'share'"
          :class="shareGroupValue === 'share' ? 'active-share-item' : ''"
        >
          <label class="radio-container"
            >Share the group with future updates
            <input
              type="radio"
              name="share"
              value="share"
              v-model="shareGroupValue"
            />
            <span class="checkmark"></span>
          </label>

          <v-menu offset-y min-width="250" open-on-hover>
            <template v-slot:activator="{ on, attrs }">
              <div v-bind="attrs" v-on="on">
                <v-icon size="16" class="help-cirle">$HelpCircle</v-icon>
              </div>
            </template>
            <v-list style="height: 80px; width: 250px">
              <v-list-item style="min-height: 80px; width: 250px">
                <div class="help-info">
                  It means that any future changes in the group will be applied
                  in real-time to the link.
                </div>
              </v-list-item>
            </v-list>
          </v-menu>
        </div>
      </div>
    </a-dialog>
    <a-dialog
      :visible.sync="sharedDialogVisible"
      @confirm="confirmSharedGroup"
      width="460"
      title="Share Data Group"
      cancelbtnText="Cancel"
      surebtnText="Share"
      :footerVisible="true"
    >
      <div class="shared-dialog">
        <div class="shared-dialog-content">
          <div class="locked" v-if="operationItem?.locked">
            The data group has been shared. Anyone with the link can view the
            group.
          </div>
          <div class="unlocked" v-else>
            The data group has been shared.
            <span>
              Anyone with the link can view the group and the updates you made
              to the group.
            </span>
          </div>
        </div>
        <div class="d-flex mt-4">
          <div class="shared-link-location">
            <Link />
            <span id="sharedUrl">{{ sharedUrl }}</span>
          </div>
          <div class="shared-link-btn" @click="onCopyLinkFunc">
            <v-icon size="16">$Copy</v-icon>
            <span> Copy link</span>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="share-cancel-btn" @click="unlockedGroupFunc">
          <Close fill="#DC6060" />
          <span> Cancel sharing</span>
        </div>
      </template>
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
        <span class=""
          >Are you sure you want to delete the '{{ operationItem?.name }}'
          group?</span
        >
      </div>
    </a-dialog>
  </div>
</template>

<script>
import { mapState, mapGetters } from "vuex";
import Close from "@/components/icons/Close";
import Lock from "@/components/icons/Lock";
import Copy from "copy-to-clipboard";
import Link from "@/components/icons/Link";
import ADialog from "@/components/ADialog";
// import MenuOperation from "@/components/MenuOperation";
import {
  getGroupDetailFunc,
  updateGroupFunc,
  updateGroupShareFunc,
  deleteGroupFunc,
  createOrCopyGroupFunc
} from "@/api/group";
export default {
  name: "SaveNeuron",

  components: {
    ADialog,
    Close,
    Lock,
    Link
    // MenuOperation,
  },

  data() {
    return {
      shareDialogVisible: false,
      sharedDialogVisible: false,
      saveDialogVisible: false,
      deleteDialogVisible: false,
      renameStatus: false,
      shareGroupValue: "lock",
      menuGroupsVisible: {},
      operationItem: null,
      checkGroupsIds: [],
      neuronVal: "",
      showSaveGroups: true,
      menuMaxHeight: 128
    };
  },

  computed: {
    ...mapState({
      addGroupOption: state => state.addGroupOption,
      filteredNeurons: state => state.neuron.filteredNeurons,
      filteredSelected: state => state.neuron.filteredSelected,
      selectionRevision: state => state.neuron.selectionRevision,
      groupsDetailData: state => state.groupsDetailData,
      groups: state => state.groups,
      groupsDetail: state => state.groupsDetail,
      groupToScene: state => state.groupToScene,
      visualTarget: state => state.visualTarget
    }),

    ...mapGetters(["groupTips", "userInfo"]),

    currentGroupTips() {
      return this.userInfo ? "None" : this.groupTips;
    },

    sharedUrl() {
      return (
        process.env.VUE_APP_WWW_HOST + "?shareID=" + this.operationItem?.shareID
      );
    },

    selectedResult() {
      void this.selectionRevision;
      const selected = this.filteredSelected;
      if (!selected || selected.size === 0) return [];
      return this.filteredNeurons.filter(el =>
        selected.has(`${el.project || el.projectFullName || ""}::${el.file || ""}`)
      );
    },

    disabledBtnTag() {
      return this.selectedResult?.length === 0 ? "disabled-button" : null;
    },

    operationItemName: {
      get() {
        return this.operationItem?.name;
      },
      set(newV) {
        this.operationItem.name = newV;
      }
    }
  },

  watch: {
    groups() {
      this.groups?.forEach(group => {
        this.$set(this.menuGroupsVisible, group?.id, false);
      });
    },

    groupToScene() {
      this.checkGroupsIds = [];
    },

    // Add the file entries from groups
    checkGroupsIds() {
      let val = [];
      const promises = this.checkGroupsIds.map(async id => {
        if (!this.groupsDetailData[id]) {
          this.groupsDetailData[id] = await getGroupDetailFunc(id);
        }
        val.push(this.groupsDetailData[id]);
        return;
      });
      Promise.all(promises).then(() => {
        this.$store.commit("setSceneGroups", [...val]);
      });
    }
  },

  methods: {
    groupsItemStyle(group) {
      if (this.operationItem?.id === group?.id && this.renameStatus) {
        return {
          background: "#283652"
        };
      }
    },

    isRenameItemStatus(group) {
      if (this.renameStatus === true && this.operationItem?.id === group?.id) {
        return true;
      }
      return false;
    },

    isSharedGroup(group) {
      return parseInt(group.shareID) === 0 ? false : true;
    },

    onRenameCancel(group) {
      this.operationItem.name = group.name;
      this.renameStatus = false;
    },

    async onRenameSubmit(group) {
      if (this.operationItemName.length > 50) {
        this.$store.commit("setToolTipType", "error");
        this.$store.commit(
          "setToolTipMessage",
          "group name length should <= 50"
        );
        this.$store.commit("setToolTipVisible", true);
        return;
      }

      if (this.operationItemName !== group.name) {
        this.renameStatus = false;
        group.name = this.operationItemName;
        if (!this.groupsDetailData[this.operationItem.id]) {
          this.groupsDetailData[
            this.operationItem.id
          ] = await getGroupDetailFunc(this.operationItem.id);
        }
        await updateGroupFunc(this.operationItem.id, {
          name: this.operationItemName,
          species: this.groupsDetailData[this.operationItem.id]?.species,
          parts: this.groupsDetailData[this.operationItem.id]?.parts
        });
        this.$store.dispatch("getGroups");
        this.$emit("renameGroup", group);
      }
    },

    onMenuFunc(group) {
      // const val = e.target.getBoundingClientRect();
      // const topVal = 30;
      // if (val.top + topVal + this.menuMaxHeight > window.innerHeight) {
      //   group.menuPosition = {
      //     bottom: "30px",
      //     top: "unset"
      //   };
      // }
      this.renameStatus && (this.renameStatus = false);
      this.menuGroupsVisible[group?.id] = !this.menuGroupsVisible[group?.id];
    },

    onShareFunc(group) {
      this.renameStatus && (this.renameStatus = false);
      this.operationItem = group;
      // Already shared
      if (group?.locked || this.isSharedGroup(group)) {
        this.sharedDialogVisible = true;
      } else {
        // Not shared yet
        this.shareDialogVisible = true;
      }
    },

    onRenameFunc(group) {
      this.renameStatus = true;
      this.operationItem = { ...group };
      this.menuGroupsVisible[group?.id] = false;
    },

    async onEditFunc(group) {
      if (!this.groupsDetailData[group.id]) {
        this.groupsDetailData[group.id] = await getGroupDetailFunc(group.id);
      }
      this.operationItem = this.groupsDetailData[group.id];
      this.$emit("editGroup", this.operationItem, "save");
    },

    async onCopyFunc(group) {
      if (!this.groupsDetailData[group.id]) {
        this.groupsDetailData[group.id] = await getGroupDetailFunc(group.id);
      }
      await createOrCopyGroupFunc({
        name: group.name + " copy",
        species: this.visualTarget,
        parts: this.groupsDetailData[group.id]?.parts
      });
      this.$store.dispatch("getGroups");
    },

    onDeleteFunc(group) {
      this.operationItem = { ...group };
      this.deleteDialogVisible = true;
    },

    onCopyLinkFunc() {
      if (Copy(this.sharedUrl)) {
        this.$emit("toolTipFunc", "success", "Copy successfully!", true);
        return;
      }
      this.$emit("toolTipFunc", "error", "Copy error", true);
    },

    async unlockedGroupFunc() {
      await updateGroupShareFunc(this.operationItem.id, {
        lock: false,
        share: false
      });
      this.operationItem.locked = false;
      this.operationItem.shareID = "000000000000000000000000";
      this.sharedDialogVisible = false;
    },

    async confirmShareGroup() {
      const lockTag = this.shareGroupValue === "lock";
      await updateGroupShareFunc(this.operationItem.id, {
        lock: lockTag,
        share: true // Both are shared
      });

      const val = await getGroupDetailFunc(this.operationItem?.id);
      this.operationItem.shareID = val?.shareID;
      this.operationItem.locked = lockTag;
      this.$emit("toolTipFunc", "success", "Operation successfully!", true);

      this.shareDialogVisible = false;
      this.sharedDialogVisible = true;
    },

    confirmSharedGroup() {
      this.sharedDialogVisible = false;
    },

    async confirmDeleteGroup() {
      await deleteGroupFunc(this.operationItem.id);
      this.$store.commit(
        "setGroups",
        this.groups.filter(item => item.id !== this.operationItem.id)
      );
      this.$emit("toolTipFunc", "success", "Delete successfully!", true);

      this.deleteDialogVisible = false;
    }
  }
};
</script>

<style lang="scss" scoped>
:deep(.v-input--checkbox) {
  margin: 0 !important;
  padding: 0 !important;
}

#sharedUrl {
  white-space: nowrap;
  max-width: 276px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-text {
  font-size: 13px;
  margin-left: 8px;
  color: var(--dark, #ced4e4);
}

.shared-dialog-content {
  color: #ced4e4;
  font-size: 13px;
  font-weight: 400;
  .unlocked {
    span {
      color: #ffc42c;
    }
  }
}

.v-menu__content {
  border-radius: 0 !important;
}

.help-info {
  display: flex;
  justify-content: center;
  align-items: center;
  color: var(--Dark-, #ced4e4);
  font-size: 14px;
  font-weight: 400;
  // background: rgba(55, 70, 106, 0.7);
  // backdrop-filter: blur(5px);
}

.help-cirle {
  cursor: pointer;
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
