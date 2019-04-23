# README Pythia


<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->
<!-- code_chunk_output -->

* [README Pythia](#readme-pythia)
	* [Landing Words](#landing-words)
	* [Features](#features)
	* [Overview](#overview)
	* [Guideline](#guideline)
	* [Future Plans](#future-plans)
	* [Contributors](#contributors)

<!-- /code_chunk_output -->

## Landing Words
 **Pythia** is a web application primarily developed as an initiative for helping research students to build _Labeled Dataset_ by bare minimum effort, and yet with reliability.
## Features
 - Text To Text Labeling
 - Assign Multiple Annotators for Parallel Annotation
 - View Project Progress Status
 - Pause A Running Project
## Overview
 **Pythia** is very simple to use. You just upload your sample data file of size up to 50 Mb and list of label in the format specified, assign up to 10 annotators and run the project.

 Annotators will find 5 unlabeled data from _Pythia Dispatcher_ each time they hit the project page ready for labeling. **Dispatcher** will receive those annotated data and assign new set of data to the Annotator. No Annotator will receive the same data twice.
<!-- ### What It Is? -->
<!-- ### How It Works? -->
<!-- ## Tutorial -->
## Guideline
 - **Client**
     - Sign Up as Client
     - Create New Project
         - File size has to be less than 50Mb
         - File format has to be .csv
         - File should contain one column named 'Sample' and a single sample data per row.
     - Start Project
 - **Annotator**
     - Sign Up as Annotator
     - In the home page there will be running project list
         - Click on the link
         - Label the samples
         - Submit, and the page will refresh with new data
## Future Plans
 - **Next Steps**:
     - Multi Label Annotation
     - View progress status in more details:
         - Annotator progress
         - Annotation speed curve.
     - Project management feature:
         - Add annotator in a running project
         - Extend project after time out
         - Message broadcast to annotators.
 - **Next Next Steps**:
     - Active Learning
     - Administrative Dashboard
     - Annotator Ranking
     - Faster Dispatcher
## Contributors
Mehdi Rahman
Ragib Ahsan
