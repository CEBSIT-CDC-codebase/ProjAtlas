<template>
  <div class="main">
    <div class="data-info">
      <span style="font-weight: 600">Data:</span>
      <span class="primary-text--text truncate">{{ dataSource }}</span>
      <span style="font-weight: 600; margin-left: 30px">Analyzing:</span>
      <span class="primary-text--text truncate">&nbsp;Projection Overview</span>
    </div>
    <div class="statistics-header">
      <span class="accent-1--text" style="margin-right: 10px">
        Statistics by
      </span>
      <span
        :class="{
          'active-header': activeHeaderItem === 'length',
          accent: activeHeaderItem !== 'length',
          'primary-light-1--text': activeHeaderItem !== 'length'
        }"
        @click="activeHeaderItem = 'length'"
      >
        Projection length
      </span>
      <span
        :class="{
          'active-header': activeHeaderItem === 'number',
          accent: activeHeaderItem !== 'number',
          'primary-light-1--text': activeHeaderItem !== 'number'
        }"
        @click="activeHeaderItem = 'number'"
      >
        Neuron number
      </span>

      <div
        v-if="isSummarization"
        class="download-button"
        @click="summarizationProjectionFunc"
      >
        <span class="accent-1--text truncate" style="margin-left: 4px">
          Summarization projection
        </span>
      </div>
    </div>

    <div class="query-container">
      <ASelect
        :showOptions="showOptions"
        @clickOutside="showOptions = false"
        style="z-index: 1"
      >
        <template slot="display-part">
          <div
            class="d-flex align-center query-input"
            @click="showOptions = true"
          >
            <v-icon
              size="16"
              style="margin-left: 10px; margin-right: 5px"
              color="#7F8491"
            >
              $Search
            </v-icon>
            <input
              v-model="keyWords"
              class="primary-text--text"
              placeholder="Search brain area"
              style="flex-grow: 1"
            />
          </div>
        </template>

        <template slot="options-part">
          <div
            class="d-flex flex-column accent-6"
            style="font-size: 13px; max-height: 400px; overflow: auto; z-index: 2"
          >
            <span
              v-for="(item, index) in searchResult"
              :key="index"
              style="padding: 5px 10px; cursor: pointer"
              @click="onSelectTreeItem(item)"
              v-html="highlightKeyWords(item)"
            ></span>
          </div>
        </template>
      </ASelect>

      <div
        v-if="!forbiddenDownload"
        class="download-button"
        @click="onDownloadData"
      >
        <v-icon size="16" color="#CED4E4">$Download</v-icon>
        <span class="accent-1--text truncate" style="margin-left: 4px">
          Download this data as JSON
        </span>
      </div>
    </div>

    <div class="tree-container">
      <div
        class="tree-header accent"
        :style="{
          'grid-template-columns': isNumberActive
            ? '250px 1fr'
            : '250px 1fr 1fr'
        }"
      >
        <span>Structure</span>
        <span class="truncate" v-if="isNumberActive"
          >Neuron projecting to this region(pcs)</span
        >
        <span class="truncate" v-if="isLengthActive">Left Hemisphere(μm)</span>
        <span class="truncate" v-if="isLengthActive">Right Hemisphere(μm)</span>
      </div>

      <v-treeview
        v-show="isLengthActive"
        ref="regionTree1"
        :items="regionTree"
        :dense="true"
        selected-color="light-blue"
        :activatable="true"
        :hoverable="true"
        :active.sync="activeItems"
        :open.sync="openItems"
        color="#c4c4c4;"
        open-on-click
        item-key="id"
      >
        <template v-slot:label="{ item, open }">
          <div class="tree-item">
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <span
                  v-bind="attrs"
                  v-on="on"
                  :style="{
                    paddingLeft: `${item.depth * 10 +
                      (item.children.length === 0 ? 16 : 0)}px`
                  }"
                >
                  <v-icon v-if="item.children.length > 0" size="16">{{
                    open ? "mdi-menu-down" : "mdi-menu-right"
                  }}</v-icon>
                  {{ item.name }}
                </span>
              </template>
              <span>{{ item.name }}</span>
            </v-tooltip>

            <div class="side-container">
              <div
                style="height: 100%; width: calc(100% - 80px); position: relative"
              >
                <div
                  class="percent-bar"
                  :style="{
                    width: (item?.leftLength / maxLength) * 100 + '% '
                  }"
                ></div>
              </div>

              <span class="primary-text--text">{{
                item?.leftLength?.toFixed(2)
              }}</span>
            </div>
            <div class="side-container">
              <div
                style="height: 100%; width: calc(100% - 80px); position: relative"
              >
                <div
                  class="percent-bar"
                  :style="{
                    width: (item.rightLength / maxLength) * 100 + '%'
                  }"
                ></div>
              </div>
              <span class="primary-text--text">{{
                item?.rightLength?.toFixed(2)
              }}</span>
            </div>
          </div>
        </template>
      </v-treeview>

      <v-treeview
        v-show="isNumberActive"
        ref="regionTree2"
        :items="regionTree"
        :dense="true"
        selected-color="light-blue"
        :activatable="true"
        :hoverable="true"
        :active="activeItems"
        :open.sync="openItems"
        color="#c4c4c4;"
        open-on-click
        item-key="id"
      >
        <template v-slot:label="{ item, open }">
          <div class="tree-item" style="grid-template-columns: 250px auto">
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <span
                  v-bind="attrs"
                  v-on="on"
                  :style="{
                    paddingLeft: `${item.depth * 10 +
                      (item.children.length === 0 ? 16 : 0)}px`
                  }"
                >
                  <v-icon v-if="item.children.length > 0" size="16">{{
                    open ? "mdi-menu-down" : "mdi-menu-right"
                  }}</v-icon>
                  {{ item.name }}
                </span>
              </template>
              <span>{{ item.name }}</span>
            </v-tooltip>
            <div class="side-container">
              <div
                style="height: 100%; width: calc(100% - 80px); position: relative"
              >
                <div
                  class="percent-bar"
                  :style="{
                    width: (item.count / maxNeuronCount) * 100 + '%'
                  }"
                ></div>
              </div>
              <span class="primary-text--text">{{ item.count }}</span>
            </div>
          </div>
        </template>
      </v-treeview>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
import ASelect from "@/components/ASelect.vue";
import { md5 } from "js-md5";
import workerScript from "@/workers/projectionTreeWorker.js";

export default {
  name: "NeuronProjection",
  components: {
    ASelect
  },
  props: {
    neuronItems: {
      type: Array,
      default: () => []
    },
    dataSource: {
      type: String,
      default: ""
    },
    isRegionType: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      activeHeaderItem: "length",
      regionTree: [],
      // totalLeftLength: 1,
      maxLength: 1,
      maxNeuronCount: 1,
      // totalRightLength: 1,
      keyWords: "",
      showOptions: false,
      regionNamesMap: new Map(),
      searchResult: [],
      openItems: [],
      activeItems: [],
      regionList: [],
      // Worker computation state and waiting queue
      isComputing: false,
      analyzeResolvers: [],
      pendingMd5: ""
    };
  },
  computed: {
    ...mapState({
      regionAxonTreeArray: state => state.region.regionAxonTreeArray,
      regionNeuronRelation: state => state.neuron.regionNeuronRelation,
      neuronRegionRelation: state => state.neuron.neuronRegionRelation,
      sessionUserInfo: state => state.session.userInfo,
      regionData: state => state.region.regionData,
      cachedTrees: state => state.analyze.cachedAxonTrees,
      cachedMaxLength: state => state.analyze.cachedAxonMaxLength,
      cachedMaxCount: state => state.analyze.cachedAxonMaxCount
    }),

    isMouse() {
      return process.env.VUE_APP_TARGET === "mouse";
    },

    forbiddenDownload() {
      return process.env.VUE_APP_SUB_SPECIES === "rbm";
    },

    isSummarization() {
      return this.sessionUserInfo && this.isMouse && !this.forbiddenDownload;
    },

    isLengthActive() {
      return this.activeHeaderItem === "length";
    },

    isNumberActive() {
      return this.activeHeaderItem === "number";
    }

    // totalNeuronCount() {
    //   return this.neuronItems.length;
    // }
  },
  watch: {
    regionAxonTreeArray: {
      handler() {
        if (!this.isRegionType) {
          this.computeTree();
        }
      },
      deep: true
    },
    neuronItems() {
      if (!this.isRegionType) {
        this.computeTree();
      }
    },
    keyWords: {
      handler() {
        this.searchRegionTree();
      }
    },
    openItems() {
      this.updatePercentBarStyle();
    },

    activeHeaderItem() {
      this.updatePercentBarStyle();
    }
  },
  methods: {
    onDownloadData() {
      const dataStr =
        "data:text/json;charset=utf-8," +
        encodeURIComponent(JSON.stringify(this.regionTree));
      const downloadAnchorNode = document.createElement("a");
      downloadAnchorNode.setAttribute("href", dataStr);
      downloadAnchorNode.setAttribute(
        "download",
        "projection-overview" + ".json"
      );
      document.body.appendChild(downloadAnchorNode); // required for firefox
      downloadAnchorNode.click();
      downloadAnchorNode.remove();
    },

    computeTree() {
      this.regionTree = [];
      this.regionNamesMap = new Map();
      this.maxLength = 0;
      this.maxNeuronCount = 0;

      if (this.regionAxonTreeArray.length === 0) {
        this.isComputing = false;
        return;
      }

      const md5Code = md5(JSON.stringify(this.neuronItems));

      if (this.cachedTrees[md5Code]) {
        this.regionTree = JSON.parse(this.cachedTrees[md5Code]);
        this.maxLength = this.cachedMaxLength[md5Code];
        this.maxNeuronCount = this.cachedMaxCount[md5Code];
        this.isComputing = false;
        return;
      }

      // Prepare the data to send to the worker
      const workerData = {
        regionAxonTreeArray: this.regionAxonTreeArray,
        neuronItems: this.neuronItems,
        regionNeuronRelation: this.regionNeuronRelation,
        neuronRegionRelation: this.neuronRegionRelation,
        target: process.env.VUE_APP_TARGET
      };

      // Send data to the worker for processing
      this.isComputing = true;
      this.pendingMd5 = md5Code;
      this.worker.postMessage(workerData);
    },

    searchRegionTree() {
      if (this.keyWords.length < 2) {
        this.searchResult = [];
        this.openItems = [];
        this.activeItems = [];
        return;
      }
      const names = [...this.regionNamesMap.keys()];
      this.searchResult = names
        .filter(name =>
          name.toLocaleLowerCase().includes(this.keyWords.toLocaleLowerCase())
        )
        .sort((a, b) => {
          return (
            a.toLocaleLowerCase().indexOf(this.keyWords) -
            b.toLocaleLowerCase().indexOf(this.keyWords)
          );
        });
    },

    onSelectTreeItem(name) {
      this.keyWords = name;
      this.showOptions = false;
      this.openItems = [];
      this.activeItems = [];

      const id = this.regionNamesMap.get(name);
      const isOpen = (id, node) => {
        if (node.id === id) {
          return true;
        } else if (node.children) {
          return node.children.some(child => isOpen(id, child));
        } else {
          return false;
        }
      };

      const addID = (id, node) => {
        if (isOpen(id, node)) {
          this.openItems.push(node.id);
          this.activeItems.push(node.id);
        }

        if (node.children) {
          node.children.forEach(child => addID(id, child));
        }
      };

      this.regionTree.forEach(el => {
        addID(id, el);
      });

      this.$nextTick(() => {
        const element = this.$refs.regionTree1.$el.querySelector(
          ".v-treeview-node--active"
        );
        if (element) element.scrollIntoView();
      });

      this.$nextTick(() => {
        const element = this.$refs.regionTree2.$el.querySelector(
          ".v-treeview-node--active"
        );
        if (element) element.scrollIntoView();
      });
    },

    highlightKeyWords(content) {
      if (this.keyWords && this.keyWords.length > 0) {
        let text = "";
        let lowerCaseContent = content.toLocaleLowerCase();
        const parts = lowerCaseContent.split(this.keyWords.toLocaleLowerCase());

        let count = 0;
        for (let i = 0; i < parts.length; ++i) {
          if (parts[i].length === 0) {
            text += `<span style="color: #01d1ff; font-weight: bolder;" :style="{marginRight: i===0? '8px':'0}">${content.slice(
              count,
              count + this.keyWords.length
            )}</span>`;
            count += this.keyWords.length;
          } else {
            let words = content.slice(count, count + parts[i].length);
            count += parts[i].length;
            text +=
              words +
              `<span style="color: #01d1ff; font-weight: bolder;">${content.slice(
                count,
                count + this.keyWords.length
              )}</span>`;
            count += this.keyWords.length;
          }
        }
        return text;
      } else {
        let text = "";
        const tempStr = content.split(" ");
        for (let i = 0; i < tempStr.length; ++i) {
          if (this.isAllCapitalized(tempStr[i])) {
            text += `<span style="color: #ffffff; font-weight: bolder;margin-right: 8px">${tempStr[i]}</span>`;
          } else {
            const rest = tempStr.slice(i).join(" ");
            text += `<span >${rest}</span>`;
            break;
          }
        }
        return text;
      }
    },

    isAllCapitalized(str) {
      const len = str.length;
      for (let i = 0; i < len; ++i) {
        if (str.charAt(i) !== str.charAt(i).toUpperCase()) {
          return false;
        }
      }
      return true;
    },

    updatePercentBarStyle() {
      this.$nextTick(() => {
        const percentBarDivs = document.querySelectorAll(".percent-bar");
        percentBarDivs.forEach(div => {
          const widthInPercent = div.style.width.replace("%", "") * 1;
          const widthInPixel = window
            .getComputedStyle(div)
            .getPropertyValue("width")
            .replace("px", "");
          if (widthInPercent > 0 && widthInPixel < 1) {
            div.style.borderLeftWidth = "1px";
            div.style.borderLeftStyle = "solid";
            div.style.borderImage =
              "linear-gradient(to bottom, black 20%, transparent 20%,     black 40%, transparent 40%,     black 60%, transparent 60%,     black 80%, transparent 80%,     black 100%) 1 100%";
          }
        });
      });
    },
    summarizationProjectionFunc() {
      this.$store.commit("session/setChatIsVisible", true);
      this.$store.commit("session/setAnalyzingValues", {
        result: this.regionList,
        type: "projection",
        projectionType: this.activeHeaderItem
      });
    },
    getAnalyzeResult() {
      // If the worker is currently computing, wait for it to return before resolving; otherwise return the current result immediately
      if (this.isComputing) {
        return new Promise(resolve => {
          this.analyzeResolvers.push(resolve);
        });
      }
      return Promise.resolve(this.buildAnalyzeResult());
    },

    buildAnalyzeResult() {
      return {
        result: this.regionList,
        type: "projection",
        projectionType: this.activeHeaderItem
      };
    },

    onWorkerMessage(e) {
      const {
        regionTree,
        regionList,
        maxLength,
        maxNeuronCount,
        regionNamesMap
      } = e.data;

      this.regionList = regionList;
      this.regionTree = regionTree;
      this.maxLength = maxLength;
      this.maxNeuronCount = maxNeuronCount;
      this.regionNamesMap = new Map(regionNamesMap);

      // Worker has returned, end the computing state and resolve all waiters
      this.isComputing = false;
      const result = this.buildAnalyzeResult();
      this.analyzeResolvers.forEach(resolve => resolve(result));
      this.analyzeResolvers = [];

      // Reuse the md5 from when the computation was initiated, to avoid re-stringifying a huge amount of data
      if (this.pendingMd5) {
        this.$store.commit("analyze/addCachedAxonTree", {
          key: this.pendingMd5,
          tree: JSON.stringify(regionTree),
          maxLength: maxLength,
          maxCount: maxNeuronCount
        });
        this.pendingMd5 = "";
      }
    }
  },
  created() {
    // Create a separate worker per instance, to avoid a shared singleton causing one response to be handled repeatedly by multiple instances
    this.worker = new Worker(workerScript);
    this.worker.addEventListener("message", this.onWorkerMessage);
  },
  beforeDestroy() {
    // Destroy this instance's worker
    this.worker.removeEventListener("message", this.onWorkerMessage);
    this.worker.terminate();
  }
};
</script>

<style lang="scss" scoped>
* {
  font-size: 13px;
  font-family: Roboto;
  font-weight: 400;
}
.main {
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.data-info {
  padding: 10px;
  display: flex;
  align-items: center;
  border-left: 2px solid #ffc42c;
  background: #ffc42c1a;
  margin-bottom: 20px;
}

.statistics-header {
  display: flex;
  align-items: center;
  height: 24px;

  span {
    height: 24px;
    line-height: 24px;
  }

  :nth-child(2) {
    padding: 0 10px;
    border-radius: 2px 0 0 2px;
    cursor: pointer;
  }

  :nth-child(3) {
    padding: 0 10px;
    border-radius: 0px 2px 2px 0px;
    cursor: pointer;
  }
}

::v-deep .active-header {
  color: #ffffff !important;
  background: #2d68c3 !important;
}

.query-container {
  display: flex;
  align-items: center;
  margin-top: 10px;
}

.tree-container {
  display: flex;
  flex-direction: column;
  margin-top: 10px;
}

.tree-header {
  height: 32px;
  display: grid;
  align-items: center;
  padding: 0 10px;
}

.tree-item {
  display: grid;
  grid-template-columns: 250px 1fr 1fr;
  align-items: center;
  height: 32px;

  :nth-child(1) {
    // max-width: 250px;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

.side-container {
  position: relative;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: right;

  .percent-bar {
    position: absolute;
    left: 0;
    height: 20px;
    bottom: 0;
    transform: translateY(-25%);
    background: #48d2ff;
  }

  :nth-child(2) {
    margin-right: 10px;
    width: 80px;
  }
}

::v-deep .v-treeview-node__level {
  width: 0;
}

::v-deep .v-treeview-node__toggle {
  display: none !important;
}

::v-deep .v-treeview-node__content {
  margin: 0;
}

::v-deep .v-treeview-node__root {
  padding: 0;
}

.query-input {
  height: 32px;
  width: 440px;
  user-select: none;
  cursor: pointer;
  justify-content: space-between;
  border-radius: 2px;
  border: 1px solid #343f5c;
  background: #0b101c;
}
</style>
