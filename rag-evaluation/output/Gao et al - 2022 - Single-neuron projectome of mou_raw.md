<!-- Part 1 -->

Q: How many PFC projection neurons were reconstructed in this project?
A: 6,357 neurons were reconstructed.
Type: single-evidence
Source:
  - Evidence 1: "Using FNT, a total of 6,357 PFC projection neurons were reconstructed"

Q: What is the total length of all reconstructed axons from these PFC neurons?
A: The total axon length is 783.27 meters.
Type: single-evidence
Source:
  - Evidence 1: "The total length of all reconstructed axons is 783.27 m."

Q: How many computer programs does the Fast Neurite Tracer (FNT) software package include?
A: FNT includes 16 computer programs.
Type: single-evidence
Source:
  - Evidence 1: "We developed an integrated software package (FNT) that includes a total of 16 computer programs"

Q: How many projectome subtypes were identified among the PFC projection neurons?
A: 64 subtypes were identified: 44 intratelencephalic (IT), 12 pyramidal tract (PT), and 8 corticothalamic (CT).
Type: single-evidence
Source:
  - Evidence 1: "we further classified IT, PT and CT neurons into a total of 64 subtypes (44 for IT, 12 for PT and 8 for CT)"

Q: Which PFC subregions were included in the analysis?
A: The subregions are prelimbic (PL), infralimbic (ILA), frontal pole (FRP), orbito-frontal (ORB), dorsal and ventral agranular insular (AId/v), anterior cingulate (ACA), and secondary motor (MOs) areas.
Type: single-evidence
Source:
  - Evidence 1: "Here, we considered PFC regions including prelimbic (PL), infralimbic (ILA), frontal pole (FRP), orbito-frontal (ORB), dorsal and ventral agranular insular (AId/v), anterior cingulate (ACA) and secondary motor (MOs) areas"

Q: What are the three main classes of long-range projection neurons in the neocortex?
A: The three classes are intratelencephalic (IT), pyramidal tract (PT), and corticothalamic (CT) neurons.
Type: single-evidence
Source:
  - Evidence 1: "In the neocortex, long-range projection neurons are broadly divided into three classes: intratelencephalic (IT) neurons, pyramidal tract (PT) neurons and corticothalamic (CT) neurons"

Q: How many transcriptome subtypes were identified from PFC projection neurons using scRNA-seq?
A: Nine transcriptome subtypes were identified.
Type: single-evidence
Source:
  - Evidence 1: "We identified nine transcriptome subtypes with their respective gene markers"

Q: Which CT neuron subtype lacks projection to the mediodorsal thalamus (MD) and where does it project instead?
A: Subtype 46 lacks MD projection and instead projects to the submedial nucleus of the thalamus (SMT).
Type: single-evidence
Source:
  - Evidence 1: "the CT neurons of subtype 46 located in ventro-lateral (ORBvl) and lateral orbito-frontal (ORBl) areas clearly lack MD projection but project to submedial nucleus of the thalamus (SMT) instead"

Q: How many subdomains were identified in the striatum based on PFC IT neuron terminal arbors?
A: Nine striatal subdomains were identified.
Type: single-evidence
Source:
  - Evidence 1: "We found that these cubes can be clustered into nine striatal subdomains"

Q: What algorithm was used to calculate the pairwise dissimilarity of axon morphology among PFC neurons?
A: FNT-dist, a dynamic programming algorithm.
Type: single-evidence
Source:
  - Evidence 1: "We next aligned the axons of all PFC projection neurons and calculated the pairwise dissimilarity score of their axon morphology using a rigorous dynamic programming algorithm, FNT-dist"

Q: How do PFC IT neurons organize their projections to the four cortical subnetworks?
A: IT subtypes are organized into four groups, each preferentially projecting to one of the four subnetworks (prefrontal, lateral, central, medial). The first-order axon collaterals of IT neurons are sorted into four distinct clusters, each also targeting a specific subnetwork, enabling coordinated information routing across areas within that subnetwork.
Type: multi-evidence
Source:
  - Evidence 1: "We found that all four subnetworks receive ipsilateral projections from PFC IT neurons, and projectome-defined IT subtypes could, thus, be organized into four groups, with group 1 IT subtypes projecting only within PFC, and group 2, 3, and 4 IT subtypes projecting also to lateral, central and medial subnetworks, respectively"
  - Evidence 2: "We found that the first-order axon collaterals of all IT neurons in the ipsilateral cortex are sorted into four distinct clusters by FNT-dist algorithm, each preferentially projecting to one of the four subnetworks within the ipsilateral cortex"

Q: What are the three major classes of projection neurons and how many of each were reconstructed in this dataset?
A: The three classes are intratelencephalic (IT), pyramidal tract (PT), and corticothalamic (CT) neurons. The dataset includes 3,744 IT, 1,528 PT, and 1,085 CT neurons.
Type: multi-evidence
Source:
  - Evidence 1: "long-range projection neurons are broadly divided into three classes: intratelencephalic (IT) neurons, pyramidal tract (PT) neurons and corticothalamic (CT) neurons"
  - Evidence 2: "Among all PFC neurons we analyzed, IT neurons are the most abundant (3,744) and can be divided into ipsilaterally projecting only (IT-ipsi) and contralaterally projecting (IT-contra) neurons, followed by PT (1,528) and CT neurons (1,085)."

Q: How was hierarchical organization within PFC established and what evidence supports it?
A: Hierarchical scores were assigned to 60 PFC units by classifying the laminar patterns of intra-PFC axon terminals as feed-forward (FF) or feed-back (FB) projections. The global hierarchical score was significantly higher than that of a randomly connected network, confirming genuine hierarchical ordering.
Type: multi-evidence
Source:
  - Evidence 1: "We, thus, assigned the six patterns as FF and FB projections (three FF and three FB) accordingly and computed the hierarchical scores for each of the 60 PFC units"
  - Evidence 2: "we found that there was indeed a hierarchical ordering within PFC, because the global hierarchical score, defined as the measure of self-consistency of hierarchy across all PFC units, is significantly higher than that of randomly connected network"

Q: How does the soma location of PFC CT neurons relate to their thalamic projection targets?
A: The medio-lateral soma position in PFC is preserved in the primary axon tract and converts into an anterior-posterior order in the thalamus, which determines the distribution of terminal arbors. For instance, CT neurons in ORBm/vl project to anterior MD, while those in AId project to ventral MD.
Type: multi-evidence
Source:
  - Evidence 1: "The primary axons within the CT tract exhibited a medio-lateral order that preserved the soma location in the PFC, and this medio-lateral order turned into anterior-posterior order as the CT axon tract turned sharply before arriving at the thalamus."
  - Evidence 2: "CT neurons in ORBm/vl preferentially project to MDa, whereas those in AId mainly project to MDv."

Q: What are the three intra-PFC connectivity modules and their functional associations?
A: Module 1 includes parts of MOs and AId and is involved in somatosensory, motor, and gustatory functions. Module 2 includes parts of ORBvl, ORBl, ACA, and posterior MOs and is involved in visual and auditory functions. Module 3 includes PL, IL, ORBm, and AIv and is involved in memory.
Type: multi-evidence
Source:
  - Evidence 1: "module 1 included some units of anterior secondary motor cortex (MOs) and dorsal agranular insular cortex (AId); module 2 included some units of ORBvl, ORBl, ACA and posterior MOs; and module 3 included some units of PL, IL, ORBm and AIv"
  - Evidence 2: "We found that module 1 is mainly involved in somatosensory, motor and gustatory function; module 2 is involved in visual and auditory function; and module 3 is involved in memory function"

Q: How do transcriptome markers Nnat and Tpbg correspond to CT neuron projectome subtypes in PL/ORB?
A: Nnat and Tpbg are markers for CT transcriptome subtypes. In PL/ORB, MD-projecting CT subtypes (51 and 52) are predominantly Nnat+, while SMT-projecting subtypes (47 and 50) are predominantly Tpbg+.
Type: multi-evidence
Source:
  - Evidence 1: "We identified nine transcriptome subtypes with their respective gene markers: Lypd1 and Penk for L2/3 IT neurons; Rorb, Deptor and Nnat for L5/6 IT neurons; Npnt and Lypd1 for PT neurons; and Nnat and Tpbg for CT neurons"
  - Evidence 2: "Similarly, for CT neurons, we found that more MD-projecting (subtypes 51 and 52) CT neurons were Nnat+, whereas more SMT-projecting (subtypes 47 and 50) CT neurons were Tpbg+."

Q: How do PFC IT neuron soma locations relate to their striatal projection targets?
A: IT subtypes located in different PFC subregions project to distinct striatal subdomains: AId neurons primarily project to ventro-lateral striatum, ORBm/ILA neurons to anterior striatum, and ACAd/ORBvl neurons to central striatum.
Type: multi-evidence
Source:
  - Evidence 1: "IT subtypes residing at different PFC subregions and laminar layers projected to different combinations of subcortical targets"
  - Evidence 2: "IT neurons in AId preferentially project to STRvl, and those in ORBm and ILA preferentially project to STRa, whereas those in ACAd and ORBvl preferentially project to STRc"

Q: What is the relationship between the transcriptome marker Lypd1 and PT neuron projectome subtypes in PL/ORB?
A: Lypd1 marks a PT transcriptome subtype. In PL/ORB, PAG-projecting PT neurons (subtypes 57 and 62) contain a significantly higher proportion of Lypd1+ cells than PCG-projecting PT neurons (subtype 61).
Type: multi-evidence
Source:
  - Evidence 1: "We identified nine transcriptome subtypes with their respective gene markers: Lypd1 and Penk for L2/3 IT neurons; Rorb, Deptor and Nnat for L5/6 IT neurons; Npnt and Lypd1 for PT neurons; and Nnat and Tpbg for CT neurons"
  - Evidence 2: "For PT neurons, we found that PAG-projecting PT neurons (subtypes 57 and 62) contained a significantly higher proportion of Lypd1+ neurons than PCG-projecting PT neurons (subtype 61)"

---

<!-- Part 2 -->

Q: What is the temperature range for the housing conditions of the mice?
A: The mice were housed at 22 to 25 degrees Celsius.
Type: single-evidence
Source:
  - Evidence 1: Mice were raised under standard conditions (12-hour light/dark cycle, $22 - 25^{\circ}\mathrm{C}$ and $30 - 70\%$ humidity) with access to food and water ad libitum.

Q: What was the median quality score of the 600 sampled traced neurons?
A: The median score was 94.
Type: single-evidence
Source:
  - Evidence 1: Among our traced neurons, we sampled 600 neurons for further evaluations by an independent team of tracers and found a median score of 94 for the tracing results of sampled neurons (Extended Data Fig. 1f).

Q: How many neuron subtypes were identified based on the C-index?
A: 64 neuron subtypes were chosen.
Type: single-evidence
Source:
  - Evidence 1: We chose 64 neuron subtypes where the C-index was a local minimum.

Q: What compression method was applied to the data cubes from fMOST imaging?
A: The data cubes were compressed using high-efficiency video coding (HEVC).
Type: single-evidence
Source:
  - Evidence 1: The data cubes were then compressed with the high-efficiency video coding (HEVC) method.

Q: What microsyringe pump was used for virus injections?
A: A MO-10 microsyringe pump from Narashige was used.
Type: single-evidence
Source:
  - Evidence 1: Injections were performed using a microsyringe pump (MO-10, Narashige, 13012).

Q: How many units was the PFC divided into for unbiased analysis?
A: The PFC was divided into 60 units.
Type: single-evidence
Source:
  - Evidence 1: To unbiasedly divide PFC into a series of units $(n = 60)$, we first partitioned the surface of PFC into patches $(n = 60)$ with a similar area using a k-means style method.

Q: What was the inside diameter of the pipette tip used for virus injection?
A: The pipette tip had an inside diameter of 20 to 25 micrometers.
Type: single-evidence
Source:
  - Evidence 1: Virus was injected by using a pulled-glass pipette of $20\sim 25 - \mu \mathrm{m}$ inside diameter at the tip.

Q: What software was used for manual segmentation of brain regions during image registration?
A: ITK-SNAP was used.
Type: single-evidence
Source:
  - Evidence 1: We then manually segmented isocortex, hippocampal region, dorsal striatum, thalamus and hypothalamus in our data image using ITK-SNAP<sup>47</sup>.

Q: How many non-PFC cortical regions were included in the bulk tracing analysis?
A: Seven cortical regions were included.
Type: single-evidence
Source:
  - Evidence 1: We downloaded 14 bulk tracing experiments (resolution: $100\mu \mathrm{m}$ ) from the Allen Mouse Brain Connectivity Atlas ( with injection sites in seven cortical regions: MOp, SSp, SSs, VISC, ENT, AUD and VIS.

Q: How many clusters were identified in the integrated scRNA-seq analysis and how many were assigned to cortical neuron types?
A: 27 clusters were identified, and 9 of them were manually assigned to neuron types such as L2/3 IT, L5/6 IT, PT, and CT.
Type: single-evidence
Source:
  - Evidence 1: Finally, 27 clusters were identified, and nine of them were manually assigned as L2/3 IT ( $Penk^{+}$ and $Lypd1^{+}$ ), L5/6 IT ( $Rorb^{+}$ , $Deptor^{+}$ and $Nnat^{+}$ ), PT ( $Npnt^{+}$ and $Lypd1^{+}$ ) and CT ( $Tpbg^{+}$ and $Nnat^{+}$ ) neurons according to the expression of specific markers (Fig. 7a).

Q: How does the FNT software ensure correct tracing in real time and what additional validation step is performed after tracing?
A: During real-time tracing, users confirm each step to ensure correctness; afterwards, each neuron is independently traced by two human tracers to validate the result.
Type: multi-evidence
Source:
  - Evidence 1: In FNT, users' confirmation at each step ensures the correctness of tracing.
  - Evidence 2: To ensure the validity of tracing result, every neuron was traced by two independent human tracers.

Q: What is the typical size of a raw EGFP image and how does FNT make this data manageable on a personal computer?
A: A typical EGFP channel consists of about 10,000 images of 30,000 × 20,000 pixels; FNT uses a program called slice2cube to split the data into smaller three-dimensional (3D) cubes that can be loaded into memory.
Type: multi-evidence
Source:
  - Evidence 1: A typical EGFP channel consists of around 10,000 16-bit images in TIFF format of $30,000 \times 20,000$ pixels in size.
  - Evidence 2: In brief, to allow data loading into the memory of a personal computer, original image data are split to smaller three-dimensional (3D) data cubes by a program called 'slice2cube' in FNT.

Q: What volume of virus mixture was injected for sparse labeling and what volume was injected in the anterograde tracing experiment?
A: For sparse labeling, 20 to 50 nanoliters of virus mixture were injected per site; for anterograde tracing, approximately 60 nanoliters were injected over 10 minutes.
Type: multi-evidence
Source:
  - Evidence 1: For each injection site, $20 - 50\mathrm{nl}$ of virus mixture was injected.
  - Evidence 2: We injected AAV2/9-hSyn-EGFP-WPRE-pA (titer: $\sim 10^{13}$ genomes per milliliter; Shanghai Taitool Bioscience) into L2/3 of orbital area, ventrolateral part (ORBvl) and AAV2/9-hSyn-mCherry-WPRE-pA (titer: $\sim 10^{13}$ genomes per milliliter; Shanghai Taitool Bioscience) into L2/3 of anterior cingulate area (ACA) slowly ( $\sim 60\mathrm{nl}$ over $\sim 10$ minutes).

Q: What clustering method was used to identify neuron subtypes and what algorithm was used to find modules in the intra-PFC connectivity network?
A: Neuron subtypes were identified using hierarchical clustering with Ward's linkage; intra-PFC modules were found with the Louvain algorithm.
Type: multi-evidence
Source:
  - Evidence 1: Then, hierarchical clustering using Ward's linkage was applied to the dissimilarity matrix to identify neuron subtypes.
  - Evidence 2: To investigate the modular structure of connectivity, we used the Louvain algorithm from the Brain Connectivity Toolbox ( $^{46,58}$.

Q: How are PFC input-based striatal subdomains defined and which cortical areas outside PFC were analyzed for their projections to these subdomains?
A: Striatal subdomains are defined by unsupervised hierarchical clustering of cubes that receive similar PFC inputs; the non-PFC areas analyzed include MOp, SSp, SSs, VISC, ENT, AUD, and VIS.
Type: multi-evidence
Source:
  - Evidence 1: After obtaining the projection matrix, we conducted unsupervised hierarchical clustering, using Spearman's rank correlation coefficient as distance measure and Ward's linkage to obtain clustered cubes receiving similar PFC inputs.
  - Evidence 2: We downloaded 14 bulk tracing experiments (resolution: $100\mu \mathrm{m}$ ) from the Allen Mouse Brain Connectivity Atlas ( with injection sites in seven cortical regions: MOp, SSp, SSs, VISC, ENT, AUD and VIS.

Q: What structure defines the primary axon of PT neurons and what metric is used to summarize branch-point asymmetry across a neuron?
A: The primary axon of a PT neuron is the axon path from the soma to the most ventral branch point or endpoint within or near the medulla; overall branch-point asymmetry is quantified by the mean partition asymmetry.
Type: multi-evidence
Source:
  - Evidence 1: We, thus, designated the axon path from the soma to the most ventral branch point or axon endpoint within or near the medulla as the primary axon of PT neurons.
  - Evidence 2: The mean partition asymmetry of a neuron was calculated by averaging the partition asymmetry of all its branch points.

Q: What method creates the flattened PFC map for soma visualization and how many units were used to partition the PFC for connectivity analysis?
A: The flatmap is created by choosing an anchor vertex on the PFC surface, computing geodesic distances to other vertices, and projecting to 2D coordinates; the PFC was partitioned into 60 units using a k-means approach.
Type: multi-evidence
Source:
  - Evidence 1: We first chose a vertex on the surface of PFC as the anchor vertex and calculated the geodesic distance between all other vertices on the surface of PFC and an anchor vertex.
  - Evidence 2: To unbiasedly divide PFC into a series of units $(n = 60)$, we first partitioned the surface of PFC into patches $(n = 60)$ with a similar area using a k-means style method.

Q: How many samples contributed neurite tracings and what was the median quality score of the evaluated traced neurons?
A: Neurite tracings were collected from 161 samples, and the median quality score of the evaluated neurons was 94.
Type: multi-evidence
Source:
  - Evidence 1: Neurite tracings were collected from 161 samples, and neuron subtypes that we identified contained neurons from multiple samples.
  - Evidence 2: Among our traced neurons, we sampled 600 neurons for further evaluations by an independent team of tracers and found a median score of 94 for the tracing results of sampled neurons (Extended Data Fig. 1f).

---

<!-- Part 3 -->

Q: What software was used for image processing and reconstruction of axon morphologies?
A: Fast Neurite Tracer (FNT v0.99.1) was used.
Type: single-evidence
Source:
  - Evidence 1: "Customized software, Fast Neurite Tracer (FNT v0.99.1), was used for image processing and reconstruction of axon morphologies."

Q: How many samples were utilized for neurite tracing collection?
A: 161 samples were used.
Type: single-evidence
Source:
  - Evidence 1: "Neurite tracings were collected from 161 samples."

Q: What objective guided the choice of sample size in the study?
A: To ensure full coverage of the three main neuron classes (IT, PT, and CT neurons) in all PFC subregions.
Type: single-evidence
Source:
  - Evidence 1: "Sample size was chosen to ensure the full coverage of three main neuron class (IT, PT, and CT neurons) in all PFC subregions."

Q: Were investigators aware of which projection neuron types would be labeled at the injection sites?
A: No, they were blind to the types of projection neurons that could be labeled.
Type: single-evidence
Source:
  - Evidence 1: "Investigators were blind to the types of projection neurons that can be labeled in the injection sites across all PFC subregions."

Q: How is soma distance computed?
A: As the Euclidean distance between two somata.
Type: single-evidence
Source:
  - Evidence 1: "Soma distance was computed as the Euclidean distance between two somata."

Q: How many target brain regions were included in the retro-seq data from Tasic et al. in the anterolateral motor area?
A: 21 target brain regions were included.
Type: single-evidence
Source:
  - Evidence 1: "This data consists of results from 21 target brain regions."

Q: What did the smFISH experiment reveal about Npnt+ neurons in SCm-projecting cells?
A: They were enriched in SCm-projecting neurons (P = 3.5 × 10^-4, Fisher's exact test).
Type: single-evidence
Source:
  - Evidence 1: "smFISH experiment showed enriched Npnt+ neurons in SCm-projecting neurons (***P = 3.5 × 10^-4, Fisher's exact test)."

Q: Which IT subtypes exhibit highly symmetric projections to bilateral agranular insular areas?
A: Subtypes 23 and 34.
Type: single-evidence
Source:
  - Evidence 1: "Projection patterns of IT subtypes 23 and 34 are highly symmetry that project to bilateral agranular insular areas (AI)"

Q: What does the red arrow indicate in the comparison figures between single-neuron projectomes and bulk labeling experiments?
A: The number of sampled neurons that can largely recapitulate the bulk labeling experiment.
Type: single-evidence
Source:
  - Evidence 1: "The red arrow denotes the number of sampled neurons that can largely recapitulate the bulk labeling experiment."

Q: How many times were retrograde labeling experiments in SCm and PCG repeated for validation?
A: Three times.
Type: single-evidence
Source:
  - Evidence 1: "For validation of mutually exclusive projections in ACA, retrograde labeling experiments in SCm and PCG were repeated three times."

Q: What process ensures the quality of traced neurons before they are used in the analysis?
A: Each neuron is traced by two independent annotators and then merged by a third annotator; only tracings that pass the quality control are included in the analysis.
Type: multi-evidence
Source:
  - Evidence 1: "Each neuron was first traced by two independent annotators and then merged by a third annotator (see Methods for detailed information)."
  - Evidence 2: "All neurite tracings passed the quality control (described in the Extended Data Fig. 1) were used for analysis."

Q: How many neuron subtypes were identified, and what was the sampling goal regarding neuron classes?
A: 64 neuron subtypes were identified, and the sample size was chosen to ensure full coverage of IT, PT, and CT neurons in all PFC subregions.
Type: multi-evidence
Source:
  - Evidence 1: "The number of neurons in each of 64 neuron subtypes can be found in Supplementary Table 4."
  - Evidence 2: "Sample size was chosen to ensure the full coverage of three main neuron class (IT, PT, and CT neurons) in all PFC subregions."

Q: How were the mutually exclusive projections in ACA validated, and how many times were the experiments repeated?
A: Dual-color retrograde labeling in PCG and SCm validated the single-neuron projectome results, and these experiments were repeated three times.
Type: multi-evidence
Source:
  - Evidence 1: "Dual-color retrograde labeling in PCG and SCm validated our single-neuron projectome results."
  - Evidence 2: "For validation of mutually exclusive projections in ACA, retrograde labeling experiments in SCm and PCG were repeated three times."

Q: What measures were taken to reduce bias in data collection?
A: Investigators were blind to the types of projection neurons that could be labeled, and projection neurons were randomly labeled during the virus injection process.
Type: multi-evidence
Source:
  - Evidence 1: "Investigators were blind to the types of projection neurons that can be labeled in the injection sites across all PFC subregions."
  - Evidence 2: "In data collection, projection neurons were randomly labeled during the virus injection process."

Q: How is the consensus neuron model generated for each neuron subtype, and what is the pattern of axon conservation?
A: The consensus neuron model is generated using FNT-dist and FNT-merge; the primary axon is largely conserved within a subtype, whereas higher-order axons are less conserved.
Type: multi-evidence
Source:
  - Evidence 1: "For each neuron subtype, the consensus neuron model was generated using FNT-dist and FNT-merge (see also Supplementary Methods 2)."
  - Evidence 2: "The primary axon (zero-order) is largely conserved for neurons in the same neuron subtype, whereas axons in high order are less conserved, as exemplified by neurons (n = 27) in subtype 60 in f."

Q: What are the two steps of image registration, and how was the registration validated?
A: The two steps are affine registration and non-rigid registration; validation was performed by measuring the distance of mass centers of four brain structures across different fMOST samples.
Type: multi-evidence
Source:
  - Evidence 1: "Step 1 involves affine registration and step 2 involves non-rigid registration (see also Methods)."
  - Evidence 2: "Distance of mass center between 4 brain structures (fr, fasciculus; mtt, mammillothalamic tract; IPN, interpeduncular nucleus; AQ, cerebral aqueduct) from different fMOST samples (n = 5) were examined."

Q: Were there significant morphological differences among IT, PT, and CT neurons, and what are their power law exponents for axon length versus branch points?
A: Yes, morphological features showed significant differences (P < 1×10^-12, two-sided Wilcoxon signed-rank test); the fitted power law exponents were 0.9 for IT, 0.3 for CT, and 0.5 for PT with R^2 values of 0.8, 0.4, and 0.6 respectively.
Type: multi-evidence
Source:
  - Evidence 1: "As calculated by the method illustrated by the schematic diagram (top, see also Methods), morphological features of CT, IT and PT neurons showed significant difference (****P < 1×10^-12, two-sided Wilcoxon signed-rank test)."
  - Evidence 2: "The fitted power by linear regression is 0.9, 0.3 and 0.5, and R^2 is 0.8, 0.4 and 0.6 for IT, CT, and PT respectively."

Q: What software was used for axon morphology reconstruction, and what specific tools were used to build the consensus neuron model?
A: Fast Neurite Tracer (FNT v0.99.1) was used for reconstruction; the consensus neuron model for each subtype was generated using FNT-dist and FNT-merge.
Type: multi-evidence
Source:
  - Evidence 1: "Customized software, Fast Neurite Tracer (FNT v0.99.1), was used for image processing and reconstruction of axon morphologies."
  - Evidence 2: "For each neuron subtype, the consensus neuron model was generated using FNT-dist and FNT-merge (see also Supplementary Methods 2)."