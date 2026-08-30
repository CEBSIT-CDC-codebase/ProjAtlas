import EventEmitter2 from 'eventemitter2';
export default class heatMapChart extends EventEmitter2 {
  constructor(canvasId, data) {
    super();
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');

    this.maxVal = data.maxVal;
    this.minVal = 0;
    this.data = data; // { columns: [], rows: [] }
    this.cellW = 30;
    this.cellH = 14;
    this.labelWidth = 0;  // Reserved width for row labels on the left
    this.labelHeight = 100; // Reserved height for column labels on top
    this.baseCharWidth = 8
    this.charMaxLength = data?.maxLength || 11
    // ColorBar configuration
    this.cbWidth = 100;
    this.cbHeight = 15;
    this.colors = [
      "#67001f", "#b2182b", "#d6604d", "#f4a582", "#fddbc7",
      "#f7f7f7", "#d1e5f0", "#92c5de", "#4393c3", "#2166ac", "#053061"
    ];
    this.init();
  }

  init() {
    const colCount = this.data.columns.length;
    const rowCount = this.data.rows.length;

    // Dynamically compute label space: measure actual text width to avoid excessive padding or overlap
    var ctx = this.ctx;
    ctx.font = "11px sans-serif";

    // Max row label pixel width → labelWidth
    var maxRowNameWidth = 60; // Minimum 60px
    for (var r = 0; r < this.data.rows.length; r++) {
      var w = ctx.measureText(this.data.rows[r].name).width;
      if (w > maxRowNameWidth) maxRowNameWidth = w;
    }
    this.labelWidth = Math.min(maxRowNameWidth + 16, 180); // +16 padding, cap at 180px

    // Max column label pixel width → labelHeight (width becomes height after 90° rotation)
    var maxColNameWidth = 100; // Minimum 100px
    for (var c = 0; c < this.data.columns.length; c++) {
      var wi = ctx.measureText(this.data.columns[c]).width;
      if (wi > maxColNameWidth) maxColNameWidth = wi;
    }
    this.labelHeight = Math.min(maxColNameWidth + 20, 220); // +20 padding, cap at 220px

    // Set the canvas's physical dimensions
    this.canvas.width = this.labelWidth + colCount * this.cellW;
    this.canvas.height = this.labelHeight + rowCount * this.cellH

    this.draw();
    this.initEvent();
  }

  getColor(value) {
    // NA value (-1 or NaN): show gray
    if (value < 0 || isNaN(Number(value)) || value === '' || value === null || value === undefined) {
      return '#808080';
    }
    if (value <= this.minVal) return this.colors[this.colors.length - 1];
    if (value >= this.maxVal) return this.colors[0];

    // Compute the normalized ratio (0.0 - 1.0). Note: based on the color array, 0 should be blue (end), max is red (start)
    // If 0 should be red instead, remove the (1 - ratio)
    const ratio = (value - this.minVal) / (this.maxVal - this.minVal);
    const scaledRatio = (1 - ratio) * (this.colors.length - 1);

    const index = Math.floor(scaledRatio);
    const nextIndex = Math.min(index + 1, this.colors.length - 1);
    const fraction = scaledRatio - index;

    return this.interpolateColor(this.colors[index], this.colors[nextIndex], fraction);
  }

  // Helper function to interpolate between hex colors
  interpolateColor(c1, c2, f) {
    const parse = (c) => [parseInt(c.slice(1, 3), 16), parseInt(c.slice(3, 5), 16), parseInt(c.slice(5, 7), 16)];
    const rgb1 = parse(c1);
    const rgb2 = parse(c2);
    const res = rgb1.map((v, i) => Math.round(v + f * (rgb2[i] - v)));
    return `rgb(${res[0]}, ${res[1]}, ${res[2]})`;
  }

  drawEmpty(message) {
    const { ctx, canvas } = this;

    // Fixed canvas dimensions
    canvas.width = 200;
    canvas.height = 200;

    // 1. Background: fill starting at y=20 (keeping top offset 20)
    ctx.fillStyle = "#1e1e1e";
    ctx.fillRect(0, 20, 200, 180);

    // 2. Text: white 16px centered
    ctx.fillStyle = "#FFFFFF";
    ctx.font = "16px sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    // Draw at the center of the remaining area (20-200), i.e. y = 20 + 180/2 = 110
    ctx.fillText(message, 100, 110);

    // 3. Dashed border: starting at y=40, margin 20
    ctx.strokeStyle = "#333";
    ctx.setLineDash([5, 5]);
    // Parameters: x=20, y=40, width=160, height=140
    ctx.strokeRect(20, 40, 160, 140);
    ctx.setLineDash([]);
  }

  drawColorBar() {
    const { ctx, colors, maxVal, minVal } = this;

    // Set the starting position (leave a small margin at the top-left)
    const x = 0;
    const y = 15;
    const cbW = 15;  // Narrower width since it's a vertical bar
    const cbH = 70;  // Taller height

    // 1. Create a vertical gradient: from y to y + cbH
    // Parameters: (x0, y0, x1, y1)
    const gradient = ctx.createLinearGradient(x, y, x, y + cbH);

    // 2. Fill in colors
    // Index 0 (#67001f red) is at the top (ratio 0)
    // Last index (#053061 blue) is at the bottom (ratio 1)
    colors.forEach((color, i) => {
      gradient.addColorStop(i / (colors.length - 1), color);
    });

    ctx.fillStyle = gradient;
    ctx.fillRect(x, y, cbW, cbH);

    // 3. Draw the text labels
    ctx.fillStyle = "#ccc";
    ctx.font = "bold 11px Arial";
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";

    // Max goes at the top right
    ctx.fillText(maxVal, x + cbW + 5, y + 2);

    // Min goes at the bottom right
    ctx.fillText(minVal, x + cbW + 5, y + cbH - 2);

    // Optional: add a 0 or median value in the middle
    // ctx.fillText((maxVal / 2).toFixed(1), x + cbW + 5, y + cbH / 2);
  }

  draw = () => {
    const { ctx, data, cellW, cellH, labelWidth, labelHeight } = this;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // 1. Draw the ColorBar in the top-left corner
    this.drawColorBar();

    // 2. Draw the column labels at the top (rotated vertically, drawn from bottom to top)
    ctx.fillStyle = "#ccc";
    ctx.font = "11px sans-serif";
    ctx.textAlign = "left";
    ctx.textBaseline = "bottom";
    data.columns.forEach((col, i) => {
      ctx.save();
      // Draw starting from the bottom of the column-label area, going upward
      ctx.translate(labelWidth + i * cellW + cellW / 2, labelHeight - 6);
      ctx.rotate(-Math.PI / 2);
      ctx.fillText(col, 0, 0);
      ctx.restore();
    });

    // 3. Draw the main body
    data.rows.forEach((row, rowIndex) => {
      const y = labelHeight + rowIndex * cellH;

      ctx.fillStyle = "#ccc";
      ctx.textAlign = "right";
      ctx.textBaseline = "middle"; // Set the baseline to dead center
      ctx.font = "11px sans-serif";
      // y + cellH / 2 keeps the text centered on the 14px row
      ctx.fillText(row.name, labelWidth - 10, y + cellH / 2);

      // Cells
      row.values.forEach((val, colIndex) => {
        const x = labelWidth + colIndex * cellW;
        ctx.fillStyle = this.getColor(val);
        // ctx.fillRect(x, y, cellW - 0.5, cellH - 0.5); // 0.5 padding creates a subtle grid feel
        ctx.fillRect(x, y, cellW, cellH); // 0.5 padding creates a subtle grid feel
      });
    });
  };

  initEvent = () => {
    this._mousemoveHandler = (e) => {
      const info = this.hitTest(e);
      if (info) {
        this.emit('hover', info, e);
        this.canvas.style.cursor = 'pointer';
      } else {
        this.canvas.style.cursor = 'default';
      }
    };

    this._mouseleaveHandler = () => {
      this.emit('hover-clear');
    };

    this._clickHandler = (e) => {
      const info = this.hitTest(e);
      if (info) this.emit('click-cell', info);
    };

    this.canvas.addEventListener('mousemove', this._mousemoveHandler);
    this.canvas.addEventListener('mouseleave', this._mouseleaveHandler);
    this.canvas.addEventListener('click', this._clickHandler);
  };

  destroy = () => {
    if (!this.canvas) return;
    if (this._mousemoveHandler) this.canvas.removeEventListener('mousemove', this._mousemoveHandler);
    if (this._mouseleaveHandler) this.canvas.removeEventListener('mouseleave', this._mouseleaveHandler);
    if (this._clickHandler) this.canvas.removeEventListener('click', this._clickHandler);
    this._mousemoveHandler = null;
    this._mouseleaveHandler = null;
    this._clickHandler = null;
  };

  /**
   * Hit test: get the corresponding row/column index and data from a mouse event
   */
  hitTest = (e) => {
    const rect = this.canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Check whether the point is within the heatmap's main body
    if (mouseX < this.labelWidth || mouseY < this.labelHeight) {
      return null;
    }

    const colIndex = Math.floor((mouseX - this.labelWidth) / this.cellW);
    const rowIndex = Math.floor((mouseY - this.labelHeight) / this.cellH);

    const rowData = this.data.rows[rowIndex];
    if (rowData && colIndex < this.data.columns.length) {
      return {
        rowIndex,
        colIndex,
        rowName: rowData.name,
        colName: this.data.columns[colIndex],
        value: rowData.values[colIndex],
      };
    }
    return null;
  };

}