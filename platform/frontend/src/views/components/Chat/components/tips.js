const mouseTips = {
  paper: `Hello! I'm your **research paper assistant**. I can help you search and retrieve information from neuroscience research papers and documentation.

I can help you with:\n
• Querying neuroscience research findings\n
• Extracting information from brain atlas documentation\n  
• Finding methodology and experimental protocols\n
• Retrieving anatomical and functional knowledge\n

**Try asking me questions like:**\n
What is the prefrontal cortex projectome?\n
What are the main projection patterns in the cortex?\n
How are neurons classified by morphology?\n
What methods are used for neural tracing?\n
Describe the organization of the mouse brain atlas\n

What would you like to know about neuroscience research?`,
  form: `
Hello! I'm your **neuron query assistant**. I can help you filter and search for specific neurons in the brain atlas based on various anatomical and morphological criteria.

I can help you:\n  
• Filter neurons by morphological structure (axon-only, axon+dendrite)\n  
• Select neurons by soma location in brain regions\n  
• Query neurons by axonal projection targets\n  
• Filter by transgenic mouse line\n  
• Add selected neurons to the visualization scene\n  

**Try commands like:**\n  
Add neurons into scene\n  
Query neurons with axon only structure\n  
Query neurons whose soma in HPF\n  
Query neurons whose axons project into ACAD\n  
Query neurons whose in line C57\n  

What neurons are you looking for today?`,
  neuroviz: `
Hello! I'm your **neural visualization assistant**. I can help you control the 3D brain atlas interface, including camera positions, rendering modes, coloring schemes, and visual properties.

I can help you:\n
• Set camera views (sagittal, coronal, horizontal)\n
• Control coloring schemes for neurons and brain regions\n
• Adjust rendering modes (backbone, full morphology)\n
• Manage reference planes and coordinate systems\n
• Configure interaction modes and visual properties\n

**Try commands like:**\n
Set camera to horizontal view\n
I want a sagittal view\n
Set neuron coloring scheme by mouse line\n
Set neuron coloring scheme to random\n
Set region coloring scheme to random\n
Show sagittal reference plane in viewport\n
Scale soma size by factor of 8\n
Set background color to dark gray\n
Take a screenshot of current view\n

How would you like to visualize the brain atlas?`,
  summarization: `Welcome! I can help you **analyze neuronal soma distribution and regional projection patterns**. Please select neurons of interest to explore their features. \n
  **Please select the neuron population to analyze.** If you have not done so yet, use **Filter** or **Neuron Selection**. Click **"View details"** in the corresponding analysis module to view the **analysis figures**.`
};

const macaqueTips = {
  paper: `Hello! I'm your **research paper assistant**. I can help you search and retrieve information from neuroscience research papers and documentation.

I can help you with:\n
• Querying neuroscience research findings\n
• Extracting information from brain atlas documentation\n  
• Finding methodology and experimental protocols\n
• Retrieving anatomical and functional knowledge\n

**Try asking me questions like:**\n
What is a single-neuron projectome?\n
How are macaque PFC neurons classified into projectome subtypes?\n
What distinguishes ITi, ITs and ITc neurons?\n
How do macaque and mouse PFC projections differ?\n

What would you like to know about neuroscience research?`,
  form: `
Hello! I'm your **neuron query assistant**. I can help you filter and search for specific neurons in the brain atlas based on various anatomical and morphological criteria.

I can help you:\n  
• Filter neurons by reconstruction type (axon only / axon and dendrite)\n  
• Filter neurons by soma hemisphere (Left / Right)\n  
• Select neurons by soma location in brain areas\n  
• Query neurons by axonal projection targets\n  
• Filter by neuron type and data group\n  
• Add selected neurons to the visualization scene\n  

**Try commands like:**\n  
Query neurons with axon only structure\n  
Query neurons whose soma in dlPFC\n  
Query neurons whose axons project into MD\n  
Query neurons with neuron type CT\n  
Add neurons into scene\n  

What neurons are you looking for today?`,
  neuroviz: `
Hello! I'm your **neural visualization assistant**. I can help you control the 3D brain atlas interface, including camera positions, rendering modes, coloring schemes, and visual properties.

I can help you:\n
• Set camera views (sagittal, coronal, horizontal)\n
• Control coloring schemes for neurons and brain regions\n
• Adjust rendering modes (backbone, full morphology)\n
• Manage reference planes and coordinate systems\n
• Configure interaction modes and visual properties\n

**Try commands like:**\n
Set camera to horizontal view\n
I want a sagittal view\n
Set neuron coloring scheme by neuron type\n
Set neuron coloring scheme to random\n
Set region coloring scheme to random\n
Show sagittal reference plane in viewport\n
Scale soma size by factor of 8\n
Set background color to dark gray\n
Take a screenshot of current view\n

How would you like to visualize the brain atlas?`,
  summarization: `Welcome! I can help you **analyze neuronal soma distribution and regional projection patterns**. Please select neurons of interest to explore their features. \n
  **Please select the neuron population to analyze.** If you have not done so yet, use **Filter** or **Neuron Selection**. Click **"View details"** in the corresponding analysis module to view the **analysis figures**.`
};

const summarizationItems = [
  {
    "link-text": "Soma Distribution",
    type: "soma_distribution",
    description: "Soma counts and regional proportions"
  },
  {
    "link-text": "Projection Overview",
    type: "projection",
    description: "Regional neuron counts or bilateral projection lengths"
  },
  {
    "link-text": "Projection Heatmap (by Axon Length)",
    type: "axon",
    description: "Source-to-target patterns based on axon length"
  },
  {
    "link-text": "Projection Heatmap (by Terminal Points)",
    type: "terminal",
    description: "Source-to-target patterns based on terminal counts"
  }
];

const summarizationWarning = `**If multiple Result windows are open, the analysis will use the neuron data from the currently active Result window.**`;
export { mouseTips, macaqueTips, summarizationItems, summarizationWarning };
