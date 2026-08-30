// init neuroViz

const init = successCallback => {
  let externalScript = document.createElement("script");
  externalScript.addEventListener("load", () => {
    window.neuroViz = new window.NeuroViz(
      process.env.VUE_APP_NEUROVIZ + "/experiments/lib/",
      process.env.VUE_APP_NEUROVIZ_SRV
    );

    window.neuroViz
      .init({
        useTHREE: process.env.VUE_APP_NEUROVIZ_USE_THREE === "true",
        background: [0, 0, 0],
        rootContainer: document.querySelector("#scene-view"),
        parseUndefined: false
      })
      .then(() => {
        window.neuroViz.setSpecies(
          process.env.VUE_APP_TARGET === "monkey"
            ? "macaque"
            : process.env.VUE_APP_TARGET
        );
        if (process.env.VUE_APP_SUBTYPE === "lc") {
          window.neuroViz.setSomaSize(5);
        } else if (process.env.VUE_APP_TARGET === "monkey") {
          window.neuroViz.setSomaSize(200);
        }
        window.neuroViz.setCamera("sagittal");
        if (process.env.VUE_APP_SUB_SPECIES === "rbm") {
          window.neuroViz.setSomaSizeScale(0.2);
        }
        successCallback();
      });
  });

  externalScript.setAttribute("id", "script-neuroviz");
  externalScript.setAttribute(
    "src",
    `${process.env.VUE_APP_NEUROVIZ}/dist/neuroviz.js`
  );
  document.head.appendChild(externalScript);
};

const neuroVizTool = {
  init
};
export default neuroVizTool;
