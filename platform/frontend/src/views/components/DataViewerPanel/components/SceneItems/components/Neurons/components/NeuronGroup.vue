<template>
  <div class="group-container">
    <div
      class="group-item"
      :class="currentGroup?.id === group?.id ? 'active-group-item' : ''"
      v-for="group in neurongroups"
      :key="group?.id"
      @click="currentGroup = group"
    >
      <div class="group-item-left">
        <Folder
          v-if="group?.save === 'unsave' && group?.id !== 'all'"
          style="margin-right: 2px; width: 16px"
          :fill="closeIconFill(group)"
        ></Folder>
        <FolderSaved
          v-if="group?.save === 'save' && group?.id !== 'all'"
          style="margin-right: 2px; width: 16px"
          :fill="closeIconFill(group)"
        ></FolderSaved>
        <span class="item-name" style="flex: 1">{{ group?.name }}</span>
      </div>
      <div
        style="margin-top: 4px"
        v-if="group?.id !== 'all'"
        @click.stop="closeGroupFunc(group)"
      >
        <Close :fill="closeIconFill(group)"></Close>
      </div>
    </div>
    <div class="group-line"></div>
  </div>
</template>

<script>
import { mapState } from "vuex";
import Close from "@/components/icons/Close";
import Folder from "@/components/icons/Folder";
import FolderSaved from "@/components/icons/FolderSaved";
import { debounce } from "@/utils/utils";
const {
  removeHighResDendritesForNeurons
} = require("@/utils/highResDendrites");
export default {
  name: "NeuronGroup",
  components: { Folder, FolderSaved, Close },
  data() {
    return {
      neurongroups: [],
      primaryGroups: [
        {
          name: "All neurons",
          id: "all",
          createTime: +new Date()
        }
      ]
    };
  },

  watch: {
    viewedNeurons() {
      this.setGroupsFolder();
      setTimeout(() => {
        this.setCurrentGroupFunc();
      }, 500);
    },

    groupFolderTag() {
      this.setGroupsFolder();
      this.setCurrentGroupFunc();
    },

    userInfo() {
      if (!this.userInfo) {
        this.neurongroups = this.neurongroups?.filter(
          item => item?.save === "unsave" || item?.id === "all"
        );
      }
    }
  },

  computed: {
    ...mapState({
      addFromScene: state => state.addFromScene,
      isPublicSwc: state => state.isPublicSwc,
      sceneCurrentGroup: state => state.sceneCurrentGroup,
      groupFolderTag: state => state.groupFolderTag,
      userInfo: state => state.userInfo,
      viewedNeurons: state => state.neuron.viewedNeurons,
      isRemoveSwc: state => state.neuron.isRemoveSwc
    }),

    currentGroup: {
      get() {
        return this.sceneCurrentGroup;
      },
      set(newV) {
        this.$store.commit("setSceneCurrentGroup", newV);
      }
    }
  },

  methods: {
    setGroupsFolder: debounce(
      function() {
        const vals = this.viewedNeurons
          ?.map(item => {
            return item.groups;
          })
          .flat(1);
        // Deduplicate with a Map in O(n), replacing the original filter + findIndex O(n^2)
        const seen = new Map();
        this.neurongroups = this.primaryGroups.concat(
          vals.filter(item => item && !seen.has(item.id) && seen.set(item.id, true))
        );
        this.neurongroups.sort((a, b) => a.createTime - b.createTime);
      },
      300,
      true
    ),

    setCurrentGroupFunc: debounce(
      function() {
        if (this.isPublicSwc) {
          this.currentGroup = this.neurongroups[0];
          return;
        }
        if (this.isRemoveSwc) {
          this.$store.commit("neuron/setIsRemoveSwc", false);
          const val = this.neurongroups.find(
            g => g?.id === this.currentGroup?.id
          );
          if (!val) {
            this.currentGroup = this.neurongroups[this.neurongroups.length - 1];
          }
          return;
        }
        this.currentGroup = this.neurongroups[this.neurongroups.length - 1];
      },
      200,
      true
    ),

    computedCurrentGroupNeurons() {
      return this.viewedNeurons.filter(item => {
        const valIndex = item?.groups?.findIndex(
          g => g.id === this.currentGroup.id
        );
        return valIndex !== -1 ? true : false;
      });
    },

    closeIconFill(group) {
      return this.currentGroup?.id === group?.id ? "#ffc42c" : "#A5ABB9";
    },

    closeGroupFunc(group) {
      // These are the ones to delete
      const neurons = this.viewedNeurons.filter(item => {
        const index = item?.groups?.findIndex(g => g.id === group.id);
        // A neuron may belong to multiple groups
        // or it may just be temporary, belonging to no group
        if (index === -1 || index == undefined) return false;
        // Present, and still belongs to another group -> just remove the group info
        if (index !== -1 && item?.groups?.length > 1) {
          item.groups.splice(index, 1);
          return false;
        }
        // Delete this neuron directly
        return true;
      });
      neurons.map(item => {
        this.$store.commit("neuron/removeViewedNeurons", [item]);
        window.neuroViz.unload(item.file);
      });
      removeHighResDendritesForNeurons(
        this.$store,
        process.env.VUE_APP_SUB_SPECIES,
        neurons
      );
      // This group's neurons are contained in other groups, meaning no neuron will be deleted, only this group's info is removed from groups
      if (!neurons.length) {
        this.setGroupsFolder();
        this.currentGroup = this.neurongroups[0];
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.group-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin: 10px;
  .group-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 48%;
    height: 24px;
    padding: 0 6px;
    margin-top: 10px;
    border-radius: 2px;
    border: 1px solid #586075;
    &:hover {
      cursor: pointer;
      border-color: #6c7998;
      .item-name {
        color: #ced4e4;
      }
    }
  }
  .group-item-left {
    display: flex;
    align-items: center;
    overflow: hidden;
  }
  .item-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: #a5abb9;
    /* Roboto/regular-14 */
    font-family: Roboto;
    font-size: 13px;
    font-style: normal;
    font-weight: 400;
    line-height: normal;
  }
  .group-line {
    height: 1px;
    width: 100%;
    background: #343f5c;
    margin-top: 20px;
  }
}
.active-group-item {
  border-color: #ffc42c !important;
  border-radius: 0 !important;
  .item-name {
    color: #ffc42c !important;
  }
}
</style>
