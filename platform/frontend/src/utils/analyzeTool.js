import store from "@/store";

export function formatResult(data) {
  return {
    id: store.state.analyze.results.length + 1,
    name: "Result",
    data,
    value: (Math.random() * 100000).toFixed(0)
  };
}
 