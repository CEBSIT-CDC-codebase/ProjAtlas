function splitInitialRbmRegions(regions) {
  const regionList = regions || [];
  const rootRegion = regionList.find(
    region => region && (region.depth === 0 || region.parentObj === null)
  );

  if (!rootRegion) {
    return {
      rootRegion: null,
      remainingRegions: regionList
    };
  }

  return {
    rootRegion,
    remainingRegions: regionList.filter(region => region !== rootRegion)
  };
}

async function loadInitialRbmRegions(regions, loadRegionFn) {
  const { rootRegion, remainingRegions } = splitInitialRbmRegions(regions);

  if (!rootRegion) {
    await Promise.all(remainingRegions.map(region => loadRegionFn(region)));
    return;
  }

  await loadRegionFn(rootRegion);

  remainingRegions.forEach(region => {
    loadRegionFn(region);
  });
}

module.exports = {
  splitInitialRbmRegions,
  loadInitialRbmRegions
};
