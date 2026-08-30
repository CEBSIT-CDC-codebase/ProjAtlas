<template>
  <div class="container-input" :class="{ 'active-textarea ': inputIsActive }">
    <textarea
      ref="userInput"
      class="input-textarea"
      rows="1"
      maxlength="1200"
      v-model="userInput"
      :disabled="inputDisabled"
      @focus="inputIsActive = true"
      @blur="inputIsActive = false"
      placeholder="Ask what you want to know"
      @keyup.enter="sendMessage"
      @input="textareaInputFunc"
    ></textarea>

    <v-btn
      icon
      id="icon-send"
      color="#7281ab"
      @click="handleAction"
    >
      <v-icon color="white" size="16">{{ isLoading ? '$Stop' : '$AI_Send' }}</v-icon>
    </v-btn>
  </div>
</template>
<script>
import { mapState } from "vuex";
import { debounce } from "@/utils/utils";

export default {
  props: {
    currentFunction: {
      type: Object,
      default: () => {}
    }
  },
  data: () => ({
    userInput: "",
    inputIsActive: false,
    inputDisabled: false
  }),

  computed: {
    ...mapState({
      isLoading: state => state.session.isLoading
    })
  },

  watch: {
    userInput() {
      this.handleSendStyleFunc();
    },

    isLoading() {
      // Refresh the button style when loading state changes (including after abort/recovery)
      this.handleSendStyleFunc();
    },

    currentFunction() {
      // if (this.currentFunction?.type?.includes("summarization")) {
      //   this.userInput = this.currentFunction?.type;
      //   this.inputDisabled = true;
      // } else {
      //   this.inputDisabled = false;
      // }
      // this.userInput = "";
    }
  },

  methods: {
    handleSendStyleFunc: debounce(function() {
      const dom = document.getElementById("icon-send");
      if (!dom) return;
      if (this.isLoading) {
        // Waiting: show as a "Stop" button, prominent and clickable (red)
        dom.style.background = "#E0524C";
        dom.style.cursor = "pointer";
        dom.style.opacity = "1";
        return;
      }
      if (!this.userInput) {
        dom.style.background = "#7281ab";
        dom.style.cursor = "no-drop";
        dom.style.opacity = ".3";
        return;
      }
      dom.style.background = "#2D68C3";
      dom.style.cursor = "pointer";
      dom.style.opacity = "1";
    }),

    handleAction() {
      if (this.isLoading) {
        // Clicking while sending → abort the current wait
        this.$store.dispatch("session/abortMessage");
        return;
      }
      this.sendMessage();
    },

    sendMessage(event) {
      if ((event && event.shiftKey) || this.isLoading) {
        return;
      }
      if (!this.userInput.trim()) {
        alert("Please enter valid questions！");
        return;
      }
      this.$emit("sendMessage", {
        content: this.userInput,
        type: this.currentFunction?.type
      });
      this.$refs["userInput"].style.height = "24px";
      this.userInput = "";
    },

    textareaInputFunc(event) {
      const textarea = event.target;
      // Handle key events
      const lineHeight = 24; // Assume each line is 24px tall
      const minRows = 1; // Minimum number of rows
      const maxRows = 4; // Maximum number of rows

      // First set the height to auto to allow shrinking
      textarea.style.height = "auto";

      // Calculate the current number of rows
      let currentRows = Math.floor(textarea.scrollHeight / lineHeight);

      // Clamp the row count between minRows and maxRows
      if (currentRows < minRows) {
        currentRows = minRows;
      } else if (currentRows > maxRows) {
        currentRows = maxRows;
      }

      // Set the new height
      textarea.style.height = `${currentRows * lineHeight}px`;
    }
  }
};
</script>
<style scoped lang="scss">
.container-input {
  position: relative;
  display: flex;
  align-items: center;
  padding: 8px 8px 8px 16px;
  gap: 20px;
  border-radius: 14px;
  border: 1px solid #586b9c;
  transition: all 0.3s;
  .input-textarea {
    flex: 1;
    font-size: 16px;
    resize: none;
    outline: none;
    color: white;
    overflow-y: auto;
    min-height: 24px;
    max-height: 96px;
    transition: all 0.3s;
  }
  &:hover {
    border: 1px solid #7fbefa;
    box-shadow: 0px 0px 10px 0px #7fbefa;
  }
}

.active-textarea {
  border: 1px solid #7fbefa;
  box-shadow: 0px 0px 10px 0px #7fbefa;
}

.icon-send-style {
  display: flex;
  min-width: 32px !important;
  width: 32px;
  height: 32px !important;
  justify-content: center;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  border-radius: 40px;
  opacity: 0.3;
  background: #7281ab;
  transition: all 0.3s;
  &:hover {
    cursor: no-drop;
  }
}

[disabled] {
  cursor: no-drop;
  opacity: 0.5;
}
</style>
