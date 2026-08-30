export const buildGroupPartsFromNeurons = neurons => {
  const projectSet = [...new Set((neurons || []).map(item => item.project))];
  const parts = projectSet.map(project => ({
    project,
    files: []
  }));
  // Pre-build a project→part Map to avoid an O(n²) find
  const partsMap = new Map(parts.map(p => [p.project, p]));

  (neurons || []).forEach(item => {
    const currentProject = partsMap.get(item.project);
    if (currentProject && !currentProject.files.includes(item.file)) {
      currentProject.files.push(item.file);
    }
  });

  return parts;
};

export const attachGroupToNeurons = ({
  neurons,
  viewedNeurons,
  groupId,
  groupName,
  save = "unsave"
}) => {
  let existingCount = 0;
  const createTime = +new Date();
  // Pre-build a file→neuron Map to avoid an O(n²) find
  const viewedMap = new Map((viewedNeurons || []).map(v => [v.file, v]));

  (neurons || []).forEach(neuron => {
    if (!neuron?.file) return;
    const viewed = viewedMap.get(neuron.file);
    // Use the viewed object (writable), or create a shallow copy to avoid mutating the frozen neuron in the store
    const target = viewed || { ...neuron };

    if (viewed) {
      existingCount++;
    }

    if (!target.groups) {
      target.groups = [];
    }

    const hasGroup = target.groups.find(g => g.id === groupId);
    if (!hasGroup) {
      target.groups.push({
        id: groupId,
        name: groupName,
        save,
        createTime
      });
    }
  });

  return { existingCount };
};
