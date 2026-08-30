import EventEmitter2 from "eventemitter2";
import { deepClone, formatDecimal } from "./utils.js";

export default class heatMapChart extends EventEmitter2 {
  constructor(navId, canvasIds, parentIds, root, type, canvasWidth, lastWidth) {
    super();
    this.root = deepClone(root);
    this.type = type;
    
    this.leafWidth = 30;
    this.leafHeight = 14;
    this.leafHMargin = 1;
    this.leafVMargin = 6;
    this.leafHPadding = 1;
    this.leafVPadding = 4;
    this.fontLargeSize = 18;
    this.fontNormalSize = 16;
    this.fontSmallSize = 14;
    this.colorBarWidth = 14;
    this.colorBarHeight = 70;
    this.colorBarDomWidth = 60;

    this.maxNeuronWidth = 0;
    this.maxFamilyWidth = 0;
    this.maxParentWidth = 0;

    this.scrollLeftVal = 0;
    this.vpWidth = 0;

    this.navCanvas = document.getElementById(navId);
    this.ctx0 = this.navCanvas.getContext("2d");
    this.canvasIds = canvasIds;
    this.parentIds = parentIds;
    this._eventDomRefs = []; // Track registered event listeners for cleanup in destroy

    this.neuronIsPainted = {};
    this.brainIsPainted = {};

    this.lastWidth = lastWidth;
    this.canvasWidth = canvasWidth;
    this.oneCanvasCount = this.canvasWidth / this.leafWidth;
    this.selectedCol = "";
    this.redrawCount = 0;
    this.checkOpacity = 1;
    this.unCheckOpacity = 0.5;

    this.sameClickNum = 1;
    this.sameLastCol = false;

    this.brains = [];
    this.familys = [];
    this.mapFamily = {};
    this.mapBrain = this.root?.mapBrain;
    this.branX = 0;
    this.branY = 0;
    this.maxValue = 0;
    this.minValue = 0;
    this.imgData;

    this.whiteBorderWidth = 2;
    this.borderLeftX = Infinity;
    this.borderRightX = 0;
    this.borderTopY = Infinity;
    this.borderBottomY = 0;

    this.initPrimaryData();
    this.draw();
    this.initEvent();
  }

  generateRandomColor = (o = this.checkOpacity) => {
    // Generate random red, green, blue components
    var red = Math.floor(Math.random() * 256);
    var green = Math.floor(Math.random() * 256);
    var blue = Math.floor(Math.random() * 256);

    // Combine the RGB components into a color string
    var color = "rgba(" + red + "," + green + "," + blue + "," + o + ")";
    return color;
  };

  hex8ToRgba(hex8) {
    // Convert the hex color value to an RGBA value
    let r = parseInt(hex8?.substring(1, 3), 16);
    let g = parseInt(hex8?.substring(3, 5), 16);
    let b = parseInt(hex8?.substring(5, 7), 16);
    let a = parseInt(hex8?.substring(7, 9), 16) / 255; // Convert the alpha value to the 0-1 range

    // Return the color value in RGBA format
    return `rgba(${r}, ${g}, ${b}, ${a})`;
  }

  initPrimaryData = () => {
    // parents familys max Width
    this.root.brains.sort((a, b) => b.value - a.value);
    this.root.brains = this.root.brains
      ?.slice(0, 30)
      .sort((a, b) => (a.family > b.family ? 1 : -1));

    this.root?.brains?.forEach(item => {
      this.ctx0.font = this.fontSmallSize + "px arial";
      const parentWidth = this.ctx0.measureText(item?.parent).width;
      if (parentWidth > this.maxParentWidth) this.maxParentWidth = parentWidth;

      this.ctx0.font = this.fontNormalSize + "px arial";
      const familyWidth = this.ctx0.measureText(item?.family).width;
      if (familyWidth > this.maxFamilyWidth) this.maxFamilyWidth = familyWidth;
    });

    this.ctx0.font = this.fontLargeSize + "px arial";
    for (const name in this.root?.neurons) {
      const neuronWidth = this.ctx0.measureText(name).width;
      // colorbar height 70 + some margin
      if (neuronWidth > this.maxNeuronWidth)
        this.maxNeuronWidth = neuronWidth > 100 ? neuronWidth : 100;
    }

    this.maxFamilyWidth += this.leafVPadding * 2;
    // set brains x,y
    this.branX = this.maxFamilyWidth;
    this.brains = this.root?.brains.map((item, index) => {
      return {
        x: this.branX,
        y: index * this.leafHeight + this.maxNeuronWidth,
        color: this.hex8ToRgba(item?.familyColor) || this.generateRandomColor(),
        ...item
      };
    });
    this.root?.brains.map(item => {
      const val = this.familys.find(f => f.family === item.family);
      if (val) {
        val.count += 1;
      } else {
        this.familys.push({
          x: 0,
          y: 0,
          count: 1,
          family: item.family
        });
        this.mapFamily[item.family] =
          this.hex8ToRgba(item?.familyColor) || this.generateRandomColor();
      }
    });
  };

  draw = () => {
    this.drawNav();
    Object.keys(this.canvasIds).forEach(key => {
      this.drawResult(
        key === "brain",
        this.canvasIds[key],
        this.lastWidth[key]
      );
    });
  };

  drawNav = () => {
    this.navCanvas.width = this.maxFamilyWidth + this.maxParentWidth;
    this.navCanvas.height =
      this.brains[this.brains.length - 1].y +
      this.leafHeight +
      this.whiteBorderWidth * 2;

    // draw colorBar
    const startY = 15;
    const startX = 0;
    const grd = this.ctx0.createLinearGradient(
      startX,
      startY,
      startX,
      startY + this.colorBarHeight
    );

    const rdylbu_r = [
      "#67001f",
      "#b2182b",
      "#d6604d",
      "#f4a582",
      "#fddbc7",
      "#f7f7f7",
      "#d1e5f0",
      "#92c5de",
      "#4393c3",
      "#2166ac",
      "#053061"
    ];
    for (let i = 0; i < rdylbu_r.length; i++) {
      const index = i * (1 / (rdylbu_r.length - 1));
      grd.addColorStop(index, rdylbu_r[i]);
    }

    this.ctx0.fillStyle = grd;
    this.ctx0.fillRect(startX, startY, this.colorBarWidth, this.colorBarHeight);
    // fill item color: 4*70 rdylbu_r rgba values concatenated
    this.imgData = this.ctx0.getImageData(
      startX,
      startY,
      1,
      this.colorBarHeight
    ).data;
    // draw parent
    for (const parent of this.brains) {
      this.ctx0.fillStyle = this.mapFamily[parent.family];
      this.ctx0.fillRect(
        parent.x,
        parent.y,
        this.maxParentWidth,
        this.leafHeight
      );
      this.ctx0.fillStyle = "white";
      this.ctx0.textAlign = "center";
      this.ctx0.textBaseline = "middle";
      const centerX = parent.x + this.maxParentWidth * 0.5;
      const centerY = parent.y + this.leafHeight * 0.5;

      this.ctx0.fillText(parent.parent, centerX, centerY);
    }
    this.branX = 0;
    this.branY = this.maxNeuronWidth;

    // draw family
    for (const family of this.familys) {
      this.ctx0.fillStyle = this.mapFamily[family.family];
      this.ctx0.fillRect(
        this.branX,
        this.branY,
        this.maxFamilyWidth,
        family.count * this.leafHeight
      );
      this.ctx0.fillStyle = "#cccccc";
      this.ctx0.fillRect(
        this.branX + this.maxFamilyWidth,
        this.branY,
        1,
        family.count * this.leafHeight
      );
      this.ctx0.fillStyle = "white";
      this.ctx0.textAlign = "center";
      this.ctx0.textBaseline = "middle";
      family.x = this.branX + this.maxFamilyWidth * 0.5;
      family.y = this.branY + family.count * this.leafHeight * 0.5;
      this.ctx0.fillText(family.family, family.x, family.y);
      this.branY += family.count * this.leafHeight;
    }
  };

  isThisCanvasVisibleInViewport = index => {
    const leftEdgeOffsetLeft = index * 4080;
    const rightEdgeOffsetLeft = (index + 1) * 4080;
    // Skip drawing when the canvas's left edge is beyond the viewport's right edge, or its right edge is before the viewport's left edge

    if (leftEdgeOffsetLeft - this.scrollLeftVal > this.vpWidth) {
      return false;
    }
    if (rightEdgeOffsetLeft - this.scrollLeftVal < 0) {
      return false;
    }

    return true;
  };

  drawResult = (isBrain, ids, lastWidth) => {
    const elements = ids?.map(id => document.getElementById(id));
    this.redrawCount++;
    this.maxValue = isBrain
      ? this.root?.logValues?.brainMax
      : this.root?.logValues?.neuronMax;
    this.minValue = isBrain
      ? this.root?.logValues.brainMin
      : this.root?.logValues.neuronMin;

    const computedColorIndex = val => {
      const curVal = isFinite(Math.log10(val)) ? Math.log10(val) : 0;
      const result = (curVal - this.minValue) / (this.maxValue - this.minValue);
      // (69-(index*69)) * 4
      return (
        (this.colorBarHeight -
          1 -
          Math.round(result * (this.colorBarHeight - 1))) *
        4
      );
    };

    for (let index = 0; index < elements.length; index++) {
      const isPainted = isBrain ? this.brainIsPainted : this.neuronIsPainted;
      // Skip if it's already been painted
      if (isPainted[index]) continue;
      const el = elements[index] || {};
      el.width = index !== elements.length - 1 ? this.canvasWidth : lastWidth;
      el.height =
        this.brains[this.brains.length - 1].y +
        this.leafHeight +
        this.whiteBorderWidth * 2;

      const visible = this.isThisCanvasVisibleInViewport(index);
      if (!visible) continue;
      this.branX = 0;
      this.branY = 0;
      let nIndex = 0;
      isPainted[index] = true;

      const currentCtx = el?.getContext("2d");
      const currentDatas = Object.keys(
        isBrain ? this.mapBrain : this.root?.neurons
      );
      const currentIndexCount = index * this.oneCanvasCount;
      // Subtract the previous count
      let currentDataKeys =
        currentDatas.length - currentIndexCount < currentIndexCount
          ? currentDatas.slice(currentIndexCount)
          : currentDatas.slice(
              currentIndexCount,
              currentIndexCount + this.oneCanvasCount
            );

      if (isBrain) {
        currentCtx.fillStyle = "white";
        for (let i = 0; i < currentDataKeys.length; i++) {
          const b = currentDataKeys[i];
          currentCtx.fillStyle = "white";

          currentCtx.save();
          currentCtx.textAlign = "start";
          currentCtx.textBaseline = "alphabetic";
          currentCtx.translate(
            this.branX + this.leafWidth - 12,
            this.branY + this.maxNeuronWidth - 8
          );
          currentCtx.rotate(Math.PI / -2);

          currentCtx.fillText(b, 0, 0);
          currentCtx.restore();
          this.branX += this.leafWidth;

          const vals = this.mapBrain[b];
          let currentOpacity = this.checkOpacity;
          // if (this.redrawCount === 1) {
          //   // First render, everything is normal
          //   currentOpacity = this.checkOpacity;
          // } else {
          //   // Same click 3 times or more
          //   if (this.sameClickNum % 2) {
          //     this.sameLastCol = false;
          //   }
          //   // Neuron matching the compound condition, or the same neuron clicked a second time, restore everything
          //   if (this.selectedCol === b || this.sameLastCol) {
          //     currentOpacity = this.checkOpacity;
          //   } else {
          //     currentOpacity = this.unCheckOpacity;
          //   }
          // }
          let index = 0;
          // Loop over brains -- left side
          for (const brain of this.brains) {
            const x = this.leafWidth * nIndex;
            const y = index * this.leafHeight + this.maxNeuronWidth;
            const val = vals[brain.parent];
            if (val !== undefined) {
              const colorIndex = computedColorIndex(val);
              currentCtx.fillStyle = `rgba(${this.imgData[colorIndex]},${
                this.imgData[colorIndex + 1]
              },${this.imgData[colorIndex + 2]},${currentOpacity})`;
              currentCtx.fillRect(x, y, this.leafWidth, this.leafHeight);
            } else {
              const colorIndex = (this.colorBarHeight - 1) * 4;
              currentCtx.fillStyle = `rgba(${this.imgData[colorIndex]}, ${
                this.imgData[colorIndex + 1]
              }, ${this.imgData[colorIndex + 2]}, ${currentOpacity})`;
              currentCtx.fillRect(x, y, this.leafWidth, this.leafHeight);
            }
            index++;
          }
          nIndex++;
        }
      } else {
        for (let i = 0; i < currentDataKeys.length; i++) {
          const neuron = currentDataKeys[i];
          currentCtx.fillStyle = "white";

          currentCtx.save();
          currentCtx.textAlign = "start";
          currentCtx.textBaseline = "alphabetic";
          currentCtx.translate(
            this.branX + this.leafWidth - 12,
            this.branY + this.maxNeuronWidth - 8
          );
          currentCtx.rotate(Math.PI / -2);

          currentCtx.fillText(neuron, 0, 0);
          currentCtx.restore();
          this.branX += this.leafWidth;

          const vals = this.root?.neurons[neuron];
          let currentOpacity = this.checkOpacity;
          let index = 0;
          for (const brain of this.brains) {
            const x = this.leafWidth * nIndex;
            const y = index * this.leafHeight + this.maxNeuronWidth;
            const val = vals[brain.parent];
            if (val !== undefined) {
              const colorIndex = computedColorIndex(val);
              currentCtx.fillStyle = `rgba(${this.imgData[colorIndex]},${
                this.imgData[colorIndex + 1]
              },${this.imgData[colorIndex + 2]},${currentOpacity})`;
              currentCtx.fillRect(x, y, this.leafWidth, this.leafHeight);
            } else {
              const colorIndex = (this.colorBarHeight - 1) * 4;
              currentCtx.fillStyle = `rgba(${this.imgData[colorIndex]}, ${
                this.imgData[colorIndex + 1]
              }, ${this.imgData[colorIndex + 2]}, ${currentOpacity})`;
              currentCtx.fillRect(x, y, this.leafWidth, this.leafHeight);
            }
            index++;
          }
          nIndex++;
        }
      }

      //   if (this.redrawCount !== 1 && !all && !this.sameLastCol) {
      //     drawWhiteBorder(
      //       this.borderLeftX,
      //       this.borderTopY,
      //       this.borderRightX,
      //       this.borderBottomY,
      //       this.whiteBorderWidth
      //     );
      //   }

      //   this.borderLeftX = Infinity;
      //   this.borderRightX = 0;
      //   this.borderTopY = Infinity;
      //   this.borderBottomY = 0;
    }
  };

  initEvent = () => {
    const curType = this.type.brain ? "brain" : "neuron";
    Object.values(this.parentIds).forEach(id => {
      const curDom = document.getElementById(id);
      if (!curDom) return;

      // Avoid binding twice (updateMap may be called multiple times)
      if (curDom._heatMapEventsBound) return;
      curDom._heatMapEventsBound = true;

      const scrollHandler = e => {
        this.scrollLeftVal = e.target.scrollLeft;
        this.vpWidth = e.target.offsetWidth;
        this.drawResult(
          this.type.brain,
          this.canvasIds[curType],
          this.lastWidth[curType]
        );
      };
      const mousemoveHandler = e => {
        const hit = this.hitTest(e, curDom);
        this.emit("hover", hit, e);
      };
      const mouseleaveHandler = () => {
        this.emit("out");
      };

      curDom.addEventListener("scroll", scrollHandler);
      curDom.addEventListener("mousemove", mousemoveHandler);
      curDom.addEventListener("mouseleave", mouseleaveHandler);

      this._eventDomRefs.push({ dom: curDom, handlers: { scroll: scrollHandler, mousemove: mousemoveHandler, mouseleave: mouseleaveHandler } });
    });
  };

  destroy = () => {
    this._eventDomRefs.forEach(({ dom, handlers }) => {
      if (dom) {
        dom.removeEventListener("scroll", handlers.scroll);
        dom.removeEventListener("mousemove", handlers.mousemove);
        dom.removeEventListener("mouseleave", handlers.mouseleave);
        dom._heatMapEventsBound = false;
      }
    });
    this._eventDomRefs = [];
  };

  hitTest = (e, dom, type) => {
    const canvasInfo = dom.getBoundingClientRect();
    const currentX = parseInt(dom.scrollLeft + e.clientX - canvasInfo.left),
      currentY = parseInt(e.clientY - canvasInfo.top - this.maxNeuronWidth);
    let currentValueKeys = Object.keys(
      this.type.brain ? this.mapBrain : this.root?.neurons
    );
    // Within the current range
    if (
      currentX >= 0 &&
      currentX <= currentValueKeys.length * this.leafWidth &&
      currentY >= 0 &&
      currentY <= this.brains.length * this.leafHeight
    ) {
      const currentIndex = Math.ceil(currentX / this.leafWidth) - 1;
      if (currentIndex >= 0) {
        let currentItems, brainIndex, parent, value;
        brainIndex = Math.ceil(currentY / this.leafHeight) - 1;
        parent = this.brains[brainIndex]?.parent;

        if (this.type.brain) {
          currentItems = this.mapBrain[currentValueKeys[currentIndex]];
        } else {
          currentItems = this.root?.neurons[currentValueKeys[currentIndex]];
        }
        value = currentItems[parent] || 0;

        if (type === "click") {
          const f = this.selectedCol === currentValueKeys[currentIndex];
          if (f) {
            this.sameClickNum++;
            this.sameLastCol = true;
          } else {
            this.sameClickNum = 1;
            this.sameLastCol = false;
            this.selectedCol = currentValueKeys[currentIndex];
          }

          const w = this.leafWidth * currentIndex;
          // get border postion
          this.borderLeftX = Math.min(this.borderLeftX, w);
          this.borderRightX = Math.max(this.borderRightX, w + this.leafWidth);
          this.borderTopY = Math.min(this.borderTopY, this.maxNeuronWidth);
          this.borderBottomY = Math.max(
            this.borderBottomY,
            this.maxNeuronWidth +
              this.brains.length * this.leafHeight +
              this.whiteBorderWidth
          );
        }
        return {
          value: Number.isInteger(value)
            ? value || "n/a"
            : formatDecimal(value, 3),
          parent,
          valKey: currentValueKeys[currentIndex],
          selectCol: this.selectedCol
        };
      }
    } else {
      if (type === "click" && this.selectedCol) {
        this.selectedCol = "";
      }
    }

    return;
  };
}
