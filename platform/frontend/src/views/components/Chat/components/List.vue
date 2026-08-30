<template>
  <div :class="['side-container']" :style="`width:${sidebarWidth}px`">
    <div class="icon-style" v-show="!listVisible" @click="$emit('createNewChat')">
      <v-icon color="#7FBEFA" size="16">$AI_NewChat</v-icon>
    </div>

    <v-btn
      color="#2D68C3"
      v-show="listVisible"
      class="chat-full-btn"
      @click="$emit('createNewChat')"
    >
      <v-icon color="white" size="16" class="mr-1">$AI_NewChat</v-icon>
      New Chat
    </v-btn>

    <div class="card-list" v-show="listVisible">
      <div class="card-list-title">Today</div>
      <div
        v-for="item in todaySession"
        :key="item.id"
        @click="$emit('selectHistory', item)"
        :class="{ 'active-list-item ': currentSession?.id === item?.id }"
        class="card-list-text"
      >
        <span class="list-name"> {{ item?.name }}</span>

        <div class="delete-icon" @click.stop="deleteHistory(item)">
          <v-icon size="12">$Delete</v-icon>
        </div>
      </div>

      <div class="card-list-title">Recent 30 days</div>
      <div
        v-for="item in notTodaySession"
        :key="item.id"
        @click="$emit('selectHistory', item)"
        :class="{ 'active-list-item ': currentSession?.id === item?.id }"
        class="card-list-text"
      >
        <span class="list-name"> {{ item?.name }}</span>

        <div class="delete-icon" @click.stop="deleteHistory(item)">
          <v-icon size="12">$Delete</v-icon>
        </div>
      </div>
    </div>

    <div class="icon-style mt-5" @click="toggleSidebar">
      <v-icon color="#7FBEFA" size="16">$AI_ShowSideBar</v-icon>
    </div>
  </div>
</template>
<script>
import { mapState } from "vuex";
import { isToday } from "@/utils/utils";
export default {
  data: () => ({
    sidebarWidth: 160,
  }),

  computed: {
    ...mapState({
      currentSession: (state) => state.session.currentSession,
      sessions: (state) => state.session.sessions,
    }),

    listVisible() {
      return this.sidebarWidth === 160;
    },

    todaySession() {
      return this.sessions.filter((item) => isToday(item?.updatedAt || item?.createdAt));
    },

    notTodaySession() {
      return this.sessions.filter((item) => !isToday(item?.updatedAt || item?.createdAt));
    },
  },

  methods: {
    toggleSidebar() {
      this.sidebarWidth = this.sidebarWidth === 160 ? 40 : 160;
    },

    deleteHistory(item) {
      this.$store.dispatch("session/deleteSession", item?.id);
    },
  },
};
</script>
<style scoped lang="scss">
.side-container {
  display: flex;
  flex-direction: column;
  padding-right: 20px;
  border-radius: 0;
  border-right: 1px solid #343f5c;
  .chat-full-btn {
    display: flex;
    height: 24px;
    padding: 4px 10px;
    justify-content: center;
    align-items: center;
    gap: 4px;
    align-self: stretch;
    border-radius: 4px;
    margin-bottom: 20px;
  }
  .card-list {
    text-align: left;
    flex: 1;
    overflow: auto;
    .card-list-title {
      color: rgba(255, 255, 255, 0.4);
      font-size: 12px;
      margin-bottom: 10px;
    }

    .card-list-text {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 4px;
      margin: 0 4px 10px;
      &:hover {
        cursor: pointer;
        color: #7fbefa;
        border-radius: 4px;
        background: rgba(190, 210, 254, 0.1);
      }
      &:last-of-type {
        margin-bottom: 0;
      }
      .list-name {
        max-width: 80%;
        @include one-row-ellipsis();
      }
    }

    .active-list-item {
      color: #7fbefa;
      font-weight: 400;
      border-radius: 4px;
      background: rgba(190, 210, 254, 0.1);
    }
  }
}

.delete-icon {
  padding: 2px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  &:hover {
    background: rgba(190, 210, 254, 0.1);
  }
}
</style>
