# Mouse Single-neuron Projectome Atlas

This is the online user's guide for the Mouse Single-neuron Projectome Atlas web application. Using fMOST technology, we have reconstructed the axonal and dendritic morphology of mouse isocortex neurons at micron resolution. This online database supports interactive query, visualization, data analyzing, data sharing, and animation creating of reconstructed brain-wide single-cell projectomes. *version 2.0*

## Version 2.0 Launched

**A new version** of the Mouse Single-neuron Projectome Atlas Web Application has been launched on 30th May, 2024. This version incorporates enhancements to the interface and interaction, which will facilitate a more intuitive and user-friendly experience for users in visualising, analysing and managing the data. The following section provides a brief overview of the recently implemented features.

### Online Data Analysis

A data analysis module has been integrated into the web application. Users can have a quick overview about the filtered dataset, including soma distribution and projection information. Furthermore, users are able to view the two analysis results simultaneously by clicking the window splitting button. For detailed instructions, please refer to the chapter on data analyzing.

### Custom Data Group & Sharing

Users can save the selected neurons as a custom data group when exploring the data. This can then be set as a data source, allowing users to apply further filters. This feature is designed to streamline the management of data and facilitate comparisons between two groups. Furthermore, users can share the data via a link, enabling collaboration with other parties.

### Animation

There are two types of camera animation available for users to choose from: rotation animation and custom animation. Users can simply set the camera parameters to obtain a preview of the animation.

## User Interface

The web application interface is shown below, consisting mainly of a header on the top(A), a data filter and operation panel on the left(B), a data viewer in the center(C) and a data analyzing panel on the right(D).

### Header

The header at the top of the page provides access to the Digital Brain home page, the User Guide page, the Data Download page, the Contact Us page, and the Login and Register pages.

### Data Filter and Operation Panel

**Query**

In the Query panel, users can first select a data source as a prerequisite for further queries of all data. Here we provide some public datasets and also allow user defined groups as a data source. There are two types of data in this panel, Neuron and Region. The Neuron panel is displayed by default when the website is opened. Users can select neurons according to anatomical regions, such as the location of somas in specific brain regions or the projection of axons to specific brain regions. In addition, users can set multiple conditions and perform Boolean operations. Moreover, users can search specific neurons by mouse lines or IDs. In the Region sub-panel, users can select regions by the region tree. Once the user has filtered and selected the data that they wish to view or analyse, they can then use the buttons at the bottom of the Query panel to add the neurons or regions to the Data Viewer, analyse the data, download it and so on.
**Data Management**

The Data Management panel displays the custom and temporary neuron groups. Once logged in to our web application, users are permitted to edit and share the groups.

### Data Viewer

This panel will display reconstructed neurons and brain models in a visual format. A list of all currently rendered neurons and regions will be displayed on the right-hand side of this panel. Users may interact with the items by clicking on the operation icons located at the top of the interface or by dragging and clicking with the mouse. Furthermore, users are able to manipulate the data presented in the view, including the ability to change the visibility, set the colour, and display information.

### Analyzing Panel

The panel will display the analysis result. The analysis is based on neuron projection features, including soma distribution, projection overview, and projection heatmap. Furthermore, the window can be split to enable users to compare two results simultaneously.

## Data Analysis

After completing data filtering, users have the capability to employ our analysis functionality to conduct basic data analysis tasks.

### How to analyze neuron data

Users can filter the data of interest in the **Data Filtering & Operation** section on the far left. Then, they can click the **Analyze** button in the **Analyzing** tab at the bottom to perform the analysis. The entire online analysis process takes a few seconds to a few minutes, depending on the amount of data to be analyzed.

### View Results

After the data analysis is complete, follow these steps to view the results:

Upon completing the analysis, the results will be displayed under the Analyzing tab on the far right. The results include:

* Soma Distribution: Displays the distribution of soma within the dataset
* Projection Overview: Provides a comprehensive overview of the projections
* Projection Heatmap (by axon length): Displays a projection heatmap based on the length of neuron axons
* Projection Heatmap (by terminal points): Displays a projection heatmap based on the terminal points of neurons

Additionally, users can enlarge the analysis results to view details by clicking the fullscreen button located in the top right corner.
### Compare Results

* **Horizontal and Vertical Comparison Modes**: To compare two sets of analysis results, users can employ the horizontal split and vertical split buttons. These buttons enable the horizontal or vertical arrangement of the respective datasets, allowing for a side-by-side or top-bottom comparison.
* **Flexible View Customization**: The analysis tool offers further customization options to enhance the comparison experience. Users can select the "Move View Left" or "Move View Right" buttons to adjust the position of the datasets within the horizontal layout. Similarly, the "Move" buttons allow for vertical positioning adjustments.

### Download Results

Our analysis tool empowers users to download their desired analysis results, enabling them to conduct further analysis or create customized visualizations using their preferred tools and software. This feature provides flexibility and control over the data, allowing users to tailor the analysis and visualization process to their specific needs and preferences. Users can download the data for both Projection Overview and Projection Heatmap visualizations in JSON or CSV format. These formats ensure compatibility with a wide range of analysis and visualization tools.

### Explore Results

* **Soma Distribution**: Our analysis tool provides a comprehensive visualization of soma distribution, offering insights into the spatial distribution and density of neurons within the brain. This visualization encompasses two key components:
  * **Axial Distribution (Top Panel)**: The top panel depicts the distribution of neuron soma along the three axes of the brain: anterior-posterior (AP), dorsal-ventral (DV), and later-medial (LM).
  * **Neuron Summation (Middle Panel)**: The middle panel presents an overview of the number of neuron soma in each brain region. It can be seen as the distribution of neuron soma in different brain regions.
  * **Regional Distribution and Density (Bottom Panel)**: The bottom panel presents the distribution of neuron counts and densities(/um3) across various brain regions. Users can explore the neuron count distribution within specific brain regions by expanding the hierarchical tree structure of the brain regions.
* **Projection Overview**: Our analysis tool offers a comprehensive visualization tool, Projection Overview, that unveils the distribution of axon lengths and projection patterns across distinct brain regions. Users can seamlessly switch between two visualization modes using the provided slider:
  * **Axon Length**: This mode displays the distribution of axon lengths (um) across various brain regions, including both left and right hemispheres.
  * **Neuron Number**: This mode displays the number of neurons projecting to each brain region.
  * **Targeted Exploration**: Users can utilize the search bar to efficiently locate specific brain regions and instantly display their corresponding axon length distributions or projection neuron counts.
* **Projection Heatmap (by axon length)**: Our analysis tool offers a powerful visualization tool that unveils the distribution of axon lengths and projection patterns across key brain regions. This visualization focuses on the top 30 brain regions based on axon length distribution, offering a granular view of neural connectivity.
  * **Neuron-Level Axon Length Distribution**: This mode presents a detailed distribution of axon lengths for individual neurons.
  * **Brain Region-Level Projection Distribution**: This mode aggregates axon lengths based on the soma location of neurons, providing a comprehensive overview of projection patterns from each brain region.
* **Projection Heatmap (by terminal points)**: Our analysis tool offers a powerful visualization tool that unveils the distribution of terminal points and projection patterns across key brain regions. This visualization focuses on the top 30 brain regions based on axon length distribution, offering a granular view of neural connectivity.
  * **Neuron-Level Terminal Points Distribution**: This mode presents a detailed distribution of Terminal Points for individual neurons.
  * **Brain Region-Level Projection Distribution**: This mode aggregates Terminal Points based on the soma location of neurons, providing a comprehensive overview of projection patterns from each brain region.

## Data Download

There are two ways to download data:

1. After filtering the data, users can directly download the selected neurons.
2. Click on the "Download" button in the header and go to the data download page. This page lists the available dataset. Users can click on the blue link button to go to the data center and download the full dataset.

## Data Viewer

The data viewer comprises a toolbar at the top, a 3D preview area in the middle, a list showing the items in the scene and a coordinate axis at the bottom.

### Mouse Interaction

The selected and rendered items are displayed in the data viewer. Users can interact with items in the viewer by mouse:

- Hold the left button to rotate freely
- Hold the wheel to rotate in the 2D plane
- Scroll the wheel to zoom in/out
- Hold the right button to drag
### Toolbar

At the top of the window, a toolbar is provided for the manipulation of the field of view and the settings controlling the data visualization.

- **Horizontal**: Display the horizontal angle
- **Sagittal**: Display the sagittal angle
- **Coronal**: Display the coronal angle
- **Pitch-90**: Rotate -90 degrees along the Y axis
- **Pitch+90**: Rotate +90 degrees along the Y axis
- **Yaw-90**: Rotate -90 degrees along the Z axis
- **Yaw+90**: Rotate +90 degrees along the Z axis
- **Rotate Clockwise**: Rotate +90 degrees along the X axis
- **Rotate Anticlockwise**: Rotate -90 degrees along the X axis
- **Flip from Left to Right**: Flip the neurons from the left brain to the right brain in the data viewer
- **Flip from Right to Left**: Flip the neurons from the right brain to the left brain in the data viewer
- **Reset**: Reset the view to its original state
- **Coloring Scheme**: Click the icon to open the coloring scheme setting panel. This panel offers a selection of coloring schemes for both regions and neurons.
- **Reference**: Click the icon to open the reference image setting panel
- **Screenshot**: Click the icon to take a screenshot of the current view and it will be saved to your desktop
- **Animation**: Click the icon to open the animation control panel
- **More Setting**: Click the icon to open the more settings panel

### Coloring Scheme

The following coloring schemes are available for regions and neurons: by CEBSIT scheme, by Allen scheme, by random scheme, by random color, by mouse line, by soma location area, by neuron structure.

### Reference

We offer two types of references. To view the reference image from three different angles, simply click on the switch button. You can also adjust the image's location and opacity using the slider bars.
### Animation

This function enables users to create simple camera animations using the data displayed in the data viewer. There are two types of camera animation available for users to choose from: rotation animation and custom animation. Users can simply set the camera parameters to obtain a preview of the animation. Firstly, users may add some neurons or regions into the data viewer and click on the "Create new" button to open the parameters setting page.

**Rotation animation**: Users may use the mouse to zoom in/out or rotate to obtain a nice view of the data and click "Set" to record the current screen angle as the first frame of the animation. If the view is changed, the recorded screen angle can be viewed by clicking the clock icon. Alternatively, if a different start view is wished, clicking "Set" again will initiate this process. Next, input the rotation angle of three coordinate axis directions. This feature allows for positive and negative number input to distinguish rotation direction. Finally, enter the number of seconds for this animation and click Preview button to view the result.

**Custom animation**: Users may set two different camera views as the start and end frames of the animation, input the duration, and the computer will automatically generate the fill-in animation between two views. Once the parameters have been set, please click the Preview button to view the result. It is possible for users to add multiple sections to the animation and to preview the entire series by clicking the play button. Each section can be relocated by dragging it to a new position. It is important to remember to input an animation name and to save it.

### More Setting

Further settings can be configured in the More Settings panel. Individual neurons and regions can be selected in the middle view by clicking on them. However, this can be disabled in the Preferences using the toggle button. Additionally, users may choose to view the neuron backbone, which provides a simplified representation of neurons, making it easier to understand the projection overview. It is also possible to change the size of the soma. Furthermore, the background colour can be modified.

### Coordinate Axis

The coordinate axis shows anatomical directions. Anterior is towards the head, posterior is towards the tail. Dorsal is towards the back, ventral is towards the abdomen. Left and right sides can also be referred to as lateral sides.

### Items in the Scene Panel

This panel lists the neurons and regions rendered in the data viewer.

**Neurons**: Users can change the visibility of neurons by clicking the "hide" or "show" icon. The items can also be removed by the "remove" icon. The color of the neuron can also be changed. Upon hovering over an individual neuron and selecting the "more" icon, a drop-down menu will be displayed. The "set structure" function allows users to set the visibility of the soma, axon and dendrite of the neuron. Users can also move or copy the selected item to another custom group or temporary group, or alternatively, delete it from the group. Once selecting several neurons, users can do batch operations by clicking the blue "edit" button at the top.

**Region**: Users may adjust the visibility of a region by clicking the "hide" or "show" icon. To remove items, simply click the "remove" icon. Furthermore, users may alter the color of a region or add neurons whose somas are in this region in a shortcut.
## Data Filtering & Operation

### Neuron Query

Users can select neurons according to anatomical regions, such as the location of somas in specific brain regions or the projection of axons to specific brain regions. In addition, users can set multiple conditions and perform Boolean operations. Moreover, users can search specific neurons by mouse lines or IDs.

- **Soma Location**: Users can select neurons by the location of their somas. The brain regions are organized in a hierarchical tree structure. Users can expand the tree to select specific brain regions.
- **Projection Target**: Users can select neurons by their projection targets. The brain regions are organized in a hierarchical tree structure. Users can expand the tree to select specific brain regions.
- **Boolean Operations**: Users can set multiple conditions and perform Boolean operations (AND, OR, NOT) to filter neurons.
- **Search by Mouse Line or ID**: Users can search specific neurons by mouse lines or IDs.

### Region Query

In the Region sub-panel, users can select regions by the region tree.

### Neuron Operation

- **Add to scene**: To display the selected neurons in the middle Data Viewer window, click the button. All these displayed neurons are also listed on the right side of the Data Viewer window. The neurons will be saved as a temporary group under the Data Management panel. The group will be listed as a temporary group under the Data Management panel on the left side of the page, as well as in the "items in the scene" panel in the Data Viewer window.
- **Add to scene with soma only**: This function enables users to display only neurons' somas in the scene, thus providing a rapid overview of the distribution of somas throughout the whole brain.
- **Analyze**: Once users have filtered some neurons, please click the 'Analyse' button to view the results in the Analyzing window on the right of the page. We provide four analysis options: 'Soma Distribution', 'Projection Overview', 'Projection heatmap (by axon length)' and 'Projection heatmap (by terminal points)'. Click on each relevant option to see the details for each analysis.
- **Save as Group**: The selected neurons can be saved as a neuron group or saved to an existing group via the save button located under the more tab. The saved group will be listed in the Custom Neuron Group panel under the Data Management tab.
- **Download**: This function allows users to download neuron files (.swc) in accordance with the query result.

### Region Operation

- **Add to scene**: To display the selected brain areas in the middle Data Viewer window, click the button. All these displayed regions are also listed on the right side of the Data Viewer window.
- **Add to scene with its neurons**: This function enables users to display the brain area and simultaneously display the neurons whose somas are in the selected area.
- **Analyze**: When selecting a brain area, users can click the "Analyze" button to view an overview of the selected area on the right side of the page.

## Data Management

This panel displays all the groups that have been saved as Custom Groups or Temporary Groups that users create during their exploration of the website. In order to save your custom group, please ensure that you have logged in.

- **Data Group Edit**: When hovering over the group, select the "More" operation icon to open the dropdown menu. This menu allows users to rename the group, manage the neurons in the group, copy the group, or delete the group.
- **Data Group Sharing**: In order to facilitate collaboration between users, we have implemented two methods for sharing data groups. The first is to lock the current status of the group and share it, which means that the group is locked and no updates can be applied to it. The second is to share the data group with future updates, which means that any future changes in the group, such as group name editing, will be applied in real-time. Once the user has selected a sharing option and clicked the share button, a link will be generated. This link can be copied and shared with partners, who will then be able to view the data group by opening the link. It is also possible for users to cancel sharing, which effectively disables the link.

## Citation

Wang, Quanxin, et al. "The Allen mouse brain common coordinate framework: a 3D reference atlas." Cell 181.4 (2020): 936-953.
