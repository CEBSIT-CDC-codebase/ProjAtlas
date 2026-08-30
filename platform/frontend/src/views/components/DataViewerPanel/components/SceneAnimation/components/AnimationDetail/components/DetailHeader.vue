<template>
  <div class="detail-header">
    <div class="pb-1 d-flex">
      <Animation
        :size="16"
        fill="#CED4E4"
        style="margin-right: 5px; margin-top: -5px"
      ></Animation>
      <span>Animation Name</span>
    </div>
    <input
      type="text"
      class="edit-input"
      placeholder="Please input"
      v-model="sectionName"
      @focus="editNameFocus"
      @input="editNameInput($event)"
      @blur="editNameBlur"
      :style="inputStyle"
    />
  </div>
</template>

<script>
import Animation from "@/components/icons/Animation";
export default {
  name: "DetailHeader",

  props: {
    name: {
      type: String,
      default: ""
    }
  },
  // °
  components: { Animation },

  data() {
    return {
      isEditName: false,
      inputStyle: ""
    };
  },

  computed: {
    sectionName: {
      get() {
        return this.name;
      },
      set(newV) {
        this.$emit("changeNameFunc", newV);
      }
    }
  },

  // watch: {
  //   sectionName() {
  //     this.inputStyle = this.sectionName ? "" : "borderColor:#dc3737;";
  //   }
  // },

  methods: {
    editNameBlur() {
      this.isEditName = !this.isEditName;
      this.inputStyle = "";
    },

    editNameFocus() {
      this.inputStyle = this.sectionName
        ? "borderColor: #3b87fd"
        : "borderColor:#dc3737;";
    },

    editNameInput(e) {
      this.inputStyle = e.target.value
        ? "borderColor: #3b87fd"
        : "borderColor:#dc3737;";
    }
  }
};
</script>

<style lang="scss" scoped>
.detail-header {
  color: #ced4e4;
  font-size: 13px;
  font-weight: 400;
  margin-bottom: 10px;
  svg {
    transform: translateY(8px);
  }
  .edit-input {
    width: 100%;
    height: 32px;
    padding: 5px 10px;
    color: #ced4e4;
    font-size: 13px;
    border-radius: 2px;
    border: 1px solid;
    border-color: #343f5c;
    &:focus {
      border-color: #3b87fd;
    }
  }
  &:hover {
    .detail-edit-name {
      width: 24px;
      height: 24px;
      margin-left: 10px;
      visibility: visible;
    }
  }
  .detail-edit-name {
    cursor: pointer;
    visibility: hidden;
    transform: translateY(4px);
  }
}
</style>
