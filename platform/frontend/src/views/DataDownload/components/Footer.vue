<template>
  <div id="footer">
    <div style="background: rgba(0, 0, 0,.1);padding-top:30px">
      <div class="primary-main footer-content">
        <div class="footer-content-left">
          <img
            :src="require('@/assets/digitalbrainLogo-footer.png')"
            @click="toDigitalBrain"
          />
        </div>

        <div class="footer-content-right">
          <div class="footer-content-link content-contact">
            <div class="content-link-title">CONTACT</div>
            <p
              v-for="item in contactLink"
              :key="item.title"
              :class="['opacity-75']"
            >
              <v-icon color="white" size="16">{{ item.icon }}</v-icon>
              <span>{{ item.title }}</span>
            </p>
          </div>

          <div class="footer-content-link content-link">
            <div class="content-link-title">QUICK LINKS</div>
            <div class="link-img-text">
              <img
                :src="require('@/assets/CEBSIT_logo_transparent.png')"
                style="margin-right:10px"
                @click="toIon"
              />
              <img :src="require('@/assets/ion-logo.png')" @click="toIon" />
              <p class="opacity-75 content-link-hover" @click="toIon">
                Center for Excellence in Brain Science and Intelligence
                Technology, CAS <br />
                ( Institute of Neuroscience, CAS )
              </p>
            </div>
            <div class="link-img-text">
              <img
                :src="require('@/assets/brain-science-data-center-logo.png')"
                @click="toBrainDataCenter"
              />
              <p
                class="opacity-75 content-link-hover"
                @click="toBrainDataCenter"
              >
                Brain Science Data Center, CAS
              </p>
            </div>
          </div>
        </div>
      </div>
      <div class="footer-divider"></div>
      <div class="primary-main footer-tips opacity-75">
        <p>Copyright © 2023 Digital Brain. All Rights Reserved.</p>
        <div class="tips-divider"></div>
        <p>沪ICP备20013257号-6</p>
        <div class="tips-divider"></div>
        <p>沪公网安备 31010402009914号</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data: () => ({
    contactLink: [
      {
        icon: "$Mail",
        title: "digitalbrain@ion.ac.cn",
        link: process.env.VUE_APP_CONTACT_URL || ""
      },
      {
        icon: "$Location",
        title: "320 Yue Yang Road, Shanghai, P.R.China",
        link: ""
      }
    ]
  }),
  methods: {
    toDigitalBrain() {
      this.$router.push("/");
    },
    toIon() {
      window.open("http://www.ion.ac.cn");
    },
    toBrainDataCenter() {
      // Set VUE_APP_DATACENTER_URL in your .env to link your own data portal.
      window.open(process.env.VUE_APP_DATACENTER_URL || "#");
    }
  }
};
</script>

<style lang="scss" scoped>
#footer {
  color: white;
  background: #151c2d;
}

.footer-content {
  display: flex;
  padding-bottom: 30px;
  font-size: 0.875rem;

  .footer-content-left {
    padding-right: 100px;

    img {
      cursor: pointer;
      width: 146px;
      height: 153px;
    }
  }

  .footer-content-right {
    flex: 1;
    display: flex;

    .content-contact {
      flex-basis: 250px;
      margin-right: 50px;
    }

    .content-link {
      flex: 1;
    }
  }

  .footer-content-link {
    .content-link-title {
      padding-bottom: 20px;
    }

    img {
      width: 48px;
      height: 48px;
      cursor: pointer;
    }

    p {
      display: flex;
      word-break: break-word;
      padding-bottom: 10px;
      margin-bottom: 0;

      .v-icon {
        padding-right: 10px;
        align-self: center;
        margin-right: 10px;
      }

      span {
        display: block;
        overflow: hidden;
      }
    }

    .content-link-hover {
      &:hover {
        opacity: 1;
        cursor: pointer;
      }
    }
  }
}

.footer-divider {
  height: 1px;
  background: #ccc;
  opacity: 0.4;
}

.footer-tips {
  display: flex;
  align-items: center;
  height: 48px;
  font-size: 12px;

  p {
    margin-bottom: 0;
  }

  .tips-divider {
    width: 1px;
    height: 10px;
    margin: 0 20px;
    background: #ffffff7f;
  }
}

.opacity-75 {
  opacity: 0.75;
}

@media screen and (max-width: 1024px) {
  .footer-content {
    display: block;

    .footer-content-right {
      margin-top: 30px;
    }
  }
}

@media screen and (max-width: 700px) {
  .footer-content {
    display: block;

    .footer-content-right {
      display: block;

      > div {
        margin-bottom: 30px;
        margin-right: 0;
      }
    }
  }

  .footer-tips {
    height: auto;
    display: block;
    margin: 10px 0;

    p:nth-of-type(2) {
      padding: 10px 0;
    }

    .tips-divider {
      display: none;
    }
  }
}
</style>
