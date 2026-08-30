<!--  -->
<template>
  <div class="user-info">
    <div class="header">
      <div class="primary-main contact-slogan">
        <div>USER PROFILE</div>
        <div></div>
      </div>
    </div>
    <div class="info-detail primary-main">
      <div class="detail-item">
        <span>Name</span>
        <span>{{ userInfo?.nickname }}</span>
      </div>
      <div class="detail-item">
        <span>Email</span>
        <span>{{ userInfo?.email }}</span>
      </div>
      <div class="detail-item">
        <span>Phone</span>
        <span></span>
      </div>
      <div class="detail-item">
        <span>Organization</span>
        <span>{{ userInfo?.organization }}</span>
      </div>
      <div class="detail-item">
        <span>Department</span>
        <span>{{ userInfo?.department }}</span>
      </div>
      <div class="detail-item">
        <span>Title</span>
        <span>{{ userInfo?.title }}</span>
      </div>
      <div class="detail-item">
        <span>Academic Title</span>
        <span>{{ userInfo?.academicTitle }}</span>
      </div>
      <div class="detail-item">
        <span>Major</span>
        <span></span>
      </div>
      <div class="detail-item">
        <span>City</span>
        <span>{{ userInfo?.city }}</span>
      </div>
      <div class="detail-item">
        <span>Address</span>
        <span>{{ userInfo?.address }}</span>
      </div>
      <div class="detail-item">
        <span>Zipcode</span>
        <span>{{ userInfo?.zipcode }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
export default {
  data: () => ({}),
  components: {},
  computed: {
    ...mapGetters(["userInfo"])
  },
  methods: {}
};
</script>
<style lang="scss" scoped>
.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #151c2d;

  .info-title {
    font-weight: bold;
  }

  .info-detail {
    width: 100%;
    margin: 100px 0;
  }

  .detail-item {
    display: flex;
    padding: 10px 20px;
    background: rgba(176, 215, 252, 0.06);
    font-size: 16px;

    &:not(:last-child) {
      margin-bottom: 10px;
    }

    span {
      &:nth-of-type(1) {
        flex: 1;
        border-right: 2px solid rgba(255, 255, 255, 0.2);
        color: $white-Ghost;
        font-style: normal;
        line-height: normal;
      }

      &:nth-of-type(2) {
        flex: 5;
        color: #ced4e4;
        margin-left: 20px;
      }
    }
  }
}

.header {
  position: relative;
  height: 290px;
  width: 100%;
  background: $blue-Charcoal;
}

.contact-slogan {
  transform: translateY(100px);

  :nth-child(1) {
    color: $white-Ghost;
    font-weight: medium;
    font-size: 34px;
    line-height: normal;
    letter-spacing: 0px;
    margin-bottom: 10px;
  }

  :nth-child(2) {
    width: 70px;
    height: 2px;
    background: #a5abb9;
  }
}
</style>
