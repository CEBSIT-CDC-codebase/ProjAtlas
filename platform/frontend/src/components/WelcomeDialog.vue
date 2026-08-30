<template>
  <div class="main">
    <div class="content">
      <div class="header">
        <span class="header-text">What's New?</span>
        <v-icon size="24" class="header-icon" @click="onClose">$Close</v-icon>
      </div>
      <div class="video-container">
        <span class="video-header">{{ loopItems[currentIndex].title }}</span>
        <video
          ref="videoPlayer"
          class="video-player"
          controls
          autoplay
          muted
          playsinline
          @ended="onVideoEnded"
          @loadeddata="onVideoLoaded"
          @error="onVideoError"
          preload="auto"
          :src="currentVideoUrl"
        ></video>
        <div class="video-indicator">
          <div
            class="indicator-item"
            :class="{ 'active-indicator': currentIndex === index }"
            v-for="(item, index) in loopItems.length"
            :key="index"
            @click="onSwitchVideo(index)"
          ></div>
        </div>
      </div>

      <div class="operation-container">
        <v-checkbox
          color="#7fbefa"
          class="show-checkbox"
          label="Don't show this again"
          v-model="notShowAgain"
          @click="onNotShowAgain"
        ></v-checkbox>
        <div style="flex-grow: 1"></div>
        <div class="skip-button" @click="onClose">Skip</div>
        <div
          class="next-button"
          :style="{
            opacity: currentIndex !== loopItems.length - 1 ? 1.0 : 0.3,
            cursor:
              currentIndex !== loopItems.length - 1 ? 'pointer' : 'default'
          }"
          @click="onSwitchVideo(currentIndex + 1)"
        >
          Next
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "WelcomeDialog",
  data() {
    return {
      loopItems: [
        {
          title: "1. Online Data Analysis",
          url: (process.env.VUE_APP_ASSETS_URL || "") + "/projectome/data-analyzing.mp4",
          loaded: false
        },
        {
          title: "2. Custom Data Group & Sharing",
          url: (process.env.VUE_APP_ASSETS_URL || "") + "/projectome/custome-group.mp4",
          loaded: false
        },
        {
          title: "3. Animation",
          url: (process.env.VUE_APP_ASSETS_URL || "") + "/projectome/animation.mp4",
          loaded: false
        }
      ],
      currentIndex: 0,
      notShowAgain: false,
      isLoading: false
    };
  },
  computed: {
    currentVideoUrl() {
      return this.loopItems[this.currentIndex]?.url || "";
    }
  },
  mounted() {
    this.initVideo();
  },
  methods: {
    initVideo() {
      const video = this.$refs.videoPlayer;
      if (video) {
        video.load();
        this.tryAutoPlay(video);
      }
    },

    async tryAutoPlay(video) {
      try {
        await video.play();
      } catch (err) {
        console.log("Auto-play failed:", err);
        // If autoplay fails, show the play button
        video.controls = true;
      }
    },

    async loadVideo(index) {
      if (this.isLoading) return;

      try {
        this.isLoading = true;
        const video = this.$refs.videoPlayer;
        if (video) {
          video.pause();
          video.currentTime = 0;
          video.load();
          this.loopItems[index].loaded = true;
          await this.tryAutoPlay(video);
        }
      } catch (error) {
        console.error("Error loading video:", error);
      } finally {
        this.isLoading = false;
      }
    },

    async onSwitchVideo(index) {
      if (index >= this.loopItems.length || index < 0 || this.isLoading) return;

      this.currentIndex = index;
      await this.loadVideo(index);
    },

    onVideoLoaded() {
      const video = this.$refs.videoPlayer;
      if (video) {
        this.tryAutoPlay(video);
      }
    },

    onVideoError(e) {
      console.error("Video error:", e);
    },

    onVideoEnded() {
      const nextIndex = (this.currentIndex + 1) % this.loopItems.length;
      this.onSwitchVideo(nextIndex);
    },

    onClose() {
      const video = this.$refs.videoPlayer;
      if (video) {
        video.pause();
        video.removeAttribute("src");
        video.load();
      }
      this.$emit("close");
    },

    onNotShowAgain() {
      localStorage.setItem("show_welcome", !this.notShowAgain);
    }
  },

  beforeDestroy() {
    const video = this.$refs.videoPlayer;
    if (video) {
      video.pause();
      video.removeAttribute("src");
      video.load();
    }
  }
};
</script>

<style scoped lang="scss">
.main {
  width: 100vw;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 202;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.4) 0%,
    rgba(0, 0, 0, 0.4) 100%
  );

  .content {
    width: 900px;
    height: 620px;
    border-radius: 4px;
    background: #262e4a;
    box-shadow: 0px 0px 30px 0px rgba(0, 0, 0, 0.25);

    display: flex;
    flex-direction: column;
  }

  .header {
    height: 60px;
    flex-basis: 60px;
    flex-shrink: 0;
    padding: 10px;
    background-image: url("../assets/vectorHeader.svg");
    background-color: #3b4e8e;
    backdrop-filter: blur(2px);
    position: relative;
  }

  .header-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-size: 24px;
    font-weight: 400;
  }

  .header-icon {
    position: absolute;
    right: 24px;
    top: 50%;
    transform: translateY(-50%);
  }

  :deep(.header-icon) {
    cursor: pointer;
    path {
      fill: #ffffff !important;
    }
  }

  .video-container {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    margin: 22px 94px;

    .video-header {
      color: #ffc700;
      font-family: "Open Sans";
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 10px;
    }

    .video-player {
      flex-grow: 1;
    }

    .video-indicator {
      margin-top: 20px;
      display: flex;
      justify-content: center;
      .indicator-item {
        width: 32px;
        height: 2px;
        background: #7ebdf933;
        margin: 0 2px;
        cursor: pointer;
      }

      .active-indicator {
        background: #7ebdf9;
      }
    }
  }

  .operation-container {
    flex-basis: 60px;
    flex-grow: 0;
    height: 60px;
    display: flex;
    align-items: center;
    padding: 10px 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(2px);

    :deep .show-checkbox .v-input--selection-controls__input {
      width: 16px;
    }

    :deep .show-checkbox .v-input--selection-controls__ripple {
      display: none;
    }

    :deep .show-checkbox .v-label {
      color: #ffffffb2;
      font-size: 14px;
    }

    .next-button {
      padding: 6px 20px;
      border-radius: 20px;
      background: #2d68c3;
      margin-left: 20px;
      font-size: 14px;
      cursor: pointer;
    }

    .skip-button {
      font-size: 14px;
      cursor: pointer;
    }
  }
}

.video-player {
  width: 100%;
  height: 100%;
  background: #000;
  object-fit: contain;
  max-height: 400px;
}
</style>
