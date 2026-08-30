function getUrlParam(name) {
  const qs =
    arguments[1] || location.search.length > 0
      ? location.search.substring(1)
      : "";
  const searchParams = new URLSearchParams(qs);
  return searchParams.get(name)
    ? decodeURIComponent(searchParams.get(name))
    : "";
}

function isToday(dateStr) {
  const today = new Date();
  const inputDate = new Date(dateStr);

  return (
    inputDate.getFullYear() === today.getFullYear() &&
    inputDate.getMonth() === today.getMonth() &&
    inputDate.getDate() === today.getDate()
  );
}

function debounce(func, wait, immediate) {
  var timeout, result;

  var debounced = function() {
    var context = this;
    var args = arguments;

    if (timeout) clearTimeout(timeout);
    if (immediate) {
      // If it has already run, don't run it again
      var callNow = !timeout;
      timeout = setTimeout(function() {
        timeout = null;
      }, wait);
      if (callNow) result = func.apply(context, args);
    } else {
      timeout = setTimeout(function() {
        result = func.apply(context, args);
      }, wait);
    }
    return result;
  };

  debounced.cancel = function() {
    clearTimeout(timeout);
    timeout = null;
  };

  return debounced;
}

function formatDecimal(num, decimalPlaces = 3) {
  // Convert the number to a string to compute the number of decimal digits
  let numStr = num.toString();
  // Find the position of the decimal point
  let decimalIndex = numStr.indexOf(".");
  // If there is no decimal point, or no digits after it, no formatting is needed
  if (decimalIndex === -1 || decimalIndex === numStr.length - 1) {
    return num;
  }
  // Compute the number of decimal digits
  let decimalLength = numStr.length - decimalIndex - 1;
  // If the decimal digit count exceeds the specified places, format with toFixed
  if (decimalLength > decimalPlaces) {
    return num.toFixed(decimalPlaces);
  }
  // Otherwise, leave it unchanged
  return num;
}

function throttle(fn, limit = 500) {
  // Timestamp of the last time fn was executed
  let previous = 0;
  // Return the throttled result as a function
  return function(...args) {
    // Get the current time as a millisecond timestamp
    let now = +new Date();
    // Compare the current time with the last execution time
    // If greater than the wait time, set previous to the current time and run fn
    if (now - previous > limit) {
      previous = now;
      fn.apply(this, args);
    }
  };
}

function hexToRgb(hexColor) {
  hexColor = hexColor?.slice(1);
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

const deepClone = (target, map = new Map()) => {
  // Primitive types
  if (typeof target !== "object") {
    return target;
  }

  // Special handling for reference types (recursive)
  // Determine whether it's an array or an object
  const temp = Array.isArray(target) ? [] : {};

  if (map.get(target)) {
    // Map, which allows using an object as a key for storage
    // If the value/object already exists, return its stored value directly to avoid infinite recursion below
    return map.get(target);
  }
  // Handles cases like a.key = a, using the object as a key with temp as the value
  map.set(target, temp);

  for (let key in target) {
    // Recursion needs to pass along both the current object's key and the map
    temp[key] = deepClone(target[key], map);
  }
  return temp;
};

function randomColor(opacity = null) {
  let r = Math.floor(Math.random() * 255);
  let g = Math.floor(Math.random() * 255);
  let b = Math.floor(Math.random() * 255);
  let op = "";
  if (opacity) {
    op = Math.floor(255 * opacity).toString(16);
  }
  return (
    "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1) + op
  );
}

function downloadBase64Img(base64URL, fileName) {
  // Create an <a> element to trigger the download
  const a = document.createElement("a");
  // Set the <a> element's download attribute to the desired file name
  a.download = fileName || "image";
  // Create a Blob object and get the base64 data's MIME type
  const mimeType = base64URL.match(/:(.*?);/)[1];
  // Convert the base64 data to a byte array
  const byteCharacters = atob(base64URL.split(",")[1]);
  const byteNumbers = new Array(byteCharacters.length);
  // Fill the byte array into a Uint8Array
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  // Create the Blob object
  const blob = new Blob([byteArray], { type: mimeType });
  // Assign the Blob object's URL to the <a> element's href attribute
  a.href = URL.createObjectURL(blob);
  // Temporarily append the <a> element to the body to trigger the download
  document.body.appendChild(a);
  a.click();
  // Remove the <a> element from the body once the download completes
  document.body.removeChild(a);
}

function downloadCSV(csv, fileName) {
  // Create a Blob object
  const blob = new Blob([csv], { type: "text/csv" });

  // Create a download link
  const url = URL.createObjectURL(blob);

  // Create an <a> element and set the download link
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName + "_data.csv";

  // Simulate a click on the download link
  link.click();

  // Release the URL object
  URL.revokeObjectURL(url);
}

export {
  isToday,
  downloadCSV,
  getUrlParam,
  formatDecimal,
  deepClone,
  debounce,
  throttle,
  hexToRgb,
  randomColor,
  downloadBase64Img
};
