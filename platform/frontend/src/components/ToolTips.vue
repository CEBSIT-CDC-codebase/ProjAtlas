<template>
  <div class="tool-tips" :class="classStatusFunc" v-show="visible">
    <div class="icon-status icon-success" v-if="type === 'success'">
      <vector265></vector265>
    </div>
    <div class="icon-status icon-error" v-else-if="type === 'error'">
      <union></union>
    </div>
    <alert
      style="width: 24px; height: 24px"
      v-else-if="type === 'warning'"
    ></alert>
    <span style="padding-right: 23px;">{{ message }}</span>
    <close
      fill="#CED4E4"
      class="icon-close"
      @click.native="$emit('close')"
    ></close>
  </div>
</template>

<script>
import Alert from "./icons/Alert.vue";
import Close from "./icons/Close.vue";
import Union from "./icons/Union.vue";
import Vector265 from "./icons/Vector265.vue";
export default {
  name: "ToolTips",
  props: {
    type: {
      type: String,
      default: "success"
    },
    visible: {
      type: Boolean,
      default: false
    },
    visibleDuration: {
      type: Number,
      default: 1500
    },
    message: {
      type: String,
      default: ""
    }
  },
  components: {
    Alert,
    Close,
    Union,
    Vector265
  },
  watch: {
    visible() {
      if (this.visible) {
        setTimeout(() => {
          this.$emit("close");
        }, this.visibleDuration);
      }
    }
  },
  computed: {
    classStatusFunc() {
      switch (this.type) {
        case "success":
          return "tool-success";
        case "error":
          return "tool-error";
        case "warning":
          return "tool-warning";
        default:
          return "";
      }
    }
  },
  methods: {},
  data() {
    return {};
  }
};
</script>

<style lang="scss" scoped>
.tool-tips {
  z-index: 999;
  position: fixed;
  top: 30px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  min-width: 340px;
  padding: 16px;
  align-items: center;
  gap: 10px;
  border-radius: 4px;
  backdrop-filter: blur(5px);
  color: var(--dark, #f5f8ff);
  font-size: 13px;
  font-weight: 400;
  transition: all 0.5s;
}

.icon-status {
  display: flex;
  width: 24px;
  height: 24px;
  justify-content: center;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  border-radius: 100px;
}

.icon-success {
  background: #15b241;
}

.icon-error {
  background: #eb4f7e;
}

.icon-close {
  width: 16px;
  height: 16px;
  position: absolute;
  right: 16px;
  top: 21px;
  cursor: pointer;
}

.tool-success {
  background: rgba(55, 106, 69, 0.6);
}

.tool-error {
  background: rgba(106, 55, 70, 0.6);
}

.tool-warning {
  background: rgba(96, 96, 96, 0.6);
}
</style>
