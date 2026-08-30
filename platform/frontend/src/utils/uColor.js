export function randomColor(opaticy = null) {
  let r = Math.floor(Math.random() * 255);
  let g = Math.floor(Math.random() * 255);
  let b = Math.floor(Math.random() * 255);
  let op = "";
  if (opaticy) {
    op = Math.floor(255 * opaticy).toString(16);
  }
  return (
    "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1) + op
  );
}

export function rgbToHex(r, g, b) {
  var hex = ((r << 16) | (g << 8) | b).toString(16);
  return "#" + new Array(Math.abs(hex.length - 7)).join("0") + hex;
}

export function hexToRgb(hexColor) {
  hexColor = hexColor.slice(1);
  if (hexColor.length === 3) {
    hexColor =
      hexColor[0] +
      hexColor[0] +
      hexColor[1] +
      hexColor[1] +
      hexColor[2] +
      hexColor[2];
  }

  if (hexColor.length === 6) {
    return [
      Number.parseInt(hexColor.slice(0, 2), 16),
      Number.parseInt(hexColor.slice(2, 4), 16),
      Number.parseInt(hexColor.slice(4, 6), 16)
    ];
  } else if (hexColor.length === 8) {
    return [
      Number.parseInt(hexColor.slice(0, 2), 16),
      Number.parseInt(hexColor.slice(2, 4), 16),
      Number.parseInt(hexColor.slice(4, 6), 16),
      Number.parseInt(hexColor.slice(6, 8), 16)
    ];
  }
}

export function gradient(startColor, endColor, step) {
  //Convert hex to rgb
  var sColor = hexToRgb(startColor),
    eColor = hexToRgb(endColor);

  //Compute the per-step delta for R/G/B
  var rStep = (eColor[0] - sColor[0]) / step,
    gStep = (eColor[1] - sColor[1]) / step,
    bStep = (eColor[2] - sColor[2]) / step;

  var gradientColorArr = [];
  for (var i = 0; i < step; i++) {
    //Compute the hex value for each step
    gradientColorArr.push(
      rgbToHex(
        parseInt(rStep * i + sColor[0]),
        parseInt(gStep * i + sColor[1]),
        parseInt(bStep * i + sColor[2])
      )
    );
  }
  return gradientColorArr;
}
