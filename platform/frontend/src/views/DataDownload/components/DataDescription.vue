<template>
  <div class="description-main">
    <div class="description-header">Data Description</div>
    <div class="description-detail">swc format specification:</div>
    <div class="description-detail" style="margin-bottom: 10px">
      Subsequent non-empty lines each represent a single neuron sample point
      with seven data items.
    </div>
    <div class="rule-table">
      <div class="table-cell table-header">Column No.</div>
      <div
        class="table-cell"
        v-for="(_, index) in 7"
        :key="index"
        :class="{ 'no-border-right': index === 6 }"
      >
        {{ index + 1 }}
      </div>
      <div class="table-cell table-header">Description</div>
      <div class="table-cell">
        Self-increasing number of the point<br />
        eg:1,2,3,4,5...
      </div>
      <div class="table-cell">
        The type of the point, eg: 0,1, 2, 3...
        <br />
        0: undefined <br />
        1: soma<br />
        2: axon<br />
        3: dendrite
      </div>
      <div class="table-cell">X-axis coordinates of the point</div>
      <div class="table-cell">Y-axis coordinates of the point</div>
      <div class="table-cell">Z-axis coordinates of the point</div>
      <div class="table-cell">Radius of the point</div>
      <div class="table-cell no-border-right">
        The number of the parent point, the soma point is “-1”
      </div>
    </div>
    <div class="description-detail" style="margin-bottom: 10px">
      The following is a sample of data
    </div>
    <div class="example-table">
      <div class="table-cell">1</div>
      <div class="table-cell">1</div>
      <div class="table-cell">4703.28117</div>
      <div class="table-cell">2454.14956</div>
      <div class="table-cell">5304.15592</div>
      <div class="table-cell">2.5859375000000e+00</div>
      <div class="table-cell no-border-right">-1</div>
      <div class="table-cell">2</div>
      <div class="table-cell">2</div>
      <div class="table-cell">4704.66815</div>
      <div class="table-cell">2453.83633</div>
      <div class="table-cell">5303.92884</div>
      <div class="table-cell">2.5859375000000e+00</div>
      <div class="table-cell no-border-right">1</div>
      <div class="table-cell">3</div>
      <div class="table-cell">2</div>
      <div class="table-cell">4705.19958</div>
      <div class="table-cell">2453.5913</div>
      <div class="table-cell">5302.58252</div>
      <div class="table-cell">1.8945312500000e+00</div>
      <div class="table-cell no-border-right">2</div>
    </div>
  </div>
</template>

<script>
export default {
  name: "DataDescription"
};
</script>

<style scoped lang="scss">
.description-main {
  display: flex;
  flex-direction: column;

  .description-header {
    color: #f5f8ff;
    font-size: 32px;
    font-weight: 500;
    padding: 16px 0;
  }

  .description-detail {
    color: #ffffff;
    font-size: 16px;
    font-weight: 400;
    margin-top: 10px;
  }

  .rule-table {
    display: grid;
    grid-template-columns: 130px 1.2fr 1.5fr 1fr 1fr 1fr 1fr 1fr;
    grid-template-rows: 48px 265px;
    border: 1px solid #586075;
    border-bottom: none;

    .table-header {
      color: #f5f8ff !important;
      background: #26272b;
    }

    .table-cell {
      font-size: 16px;
      font-weight: 400;
      padding: 10px 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ced4e4;
      border-right: 1px solid #586075;
      border-bottom: 1px solid #586075;
    }
  }

  .no-border-right {
    border-right: none !important;
  }

  .example-table {
    display: grid;
    grid-template-columns: 80px 80px 1fr 1fr 1fr 1fr 80px;
    grid-template-rows: 48px 48px 48px;
    border: 1px solid #586075;
    border-bottom: none;

    .table-cell {
      color: #ced4e4;
      padding: 10px 20px;
      font-size: 16px;
      font-weight: 400;
      border-right: 1px solid #586075;
      border-bottom: 1px solid #586075;
    }
  }
}
</style>
