# README Pythia


<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->
<!-- code_chunk_output -->

* [README Pythia](#readme-pythia)
	* [Landing Words](#landing-words)
	* [Features](#features)
	* [Overview](#overview)
	* [Guideline](#guideline)
	* [Future Steps](#future-steps)
	* [Contributors](#contributors)

<!-- /code_chunk_output -->

## Landing Words
 **Pythia** is a web application primarily developed as an initiative for helping researchers to build _Labeled Dataset_ from crowd in a organized way, with minimal effort, and yet with reliability.

## Features
 - Text to text labeling
 - Allow multiple annotators for simultaneous Annotation
 - View project progress status
 - Pause and resume running project

## Overview
 **Pythia** is very simple to use. You just upload your sample data file of size up to 50 Mb and list of labels in the format specified, then assign up to 10 annotators and run the project.

 Annotators will find 5 unlabeled data from _Pythia Dispatcher_ each time they hit the project page ready for labeling. **Dispatcher** will receive those annotated data and assign new set of data to the Annotator. No Annotator will receive already annotated data.
<!-- ### What It Is? -->
<!-- ### How It Works? -->
<!-- ## Tutorial -->
## Guideline
 - **Running Server and Database Setup**
	 - `export FLASK_APP=pythia`
	 - `flask init-db`
	 - `flask run --host 0.0.0.0 --port 5000`
	 - Please refer to: [Flask Quickstart](http://flask.pocoo.org/docs/1.0/quickstart/)
 - **Deployment**
	 - The app currently uses the built-in flask server. You may dockerize the app as it is. Please refer to the given `Dockerfile`.
	 - Further: [Deployment Options](http://flask.pocoo.org/docs/1.0/deploying/)
 - **Client**
     - Sign Up as Client
     - Create New Project
         - File size has to be less than 50Mb
         - File format has to be .csv
         - File should contain one column named 'Sample' and a single sample data per row.
     - Start Project
 - **Annotator**
     - Sign Up as Annotator
     - View running project list in the home page
         - Click on the link
         - Label the samples
         - Submit, then the page will refresh with new data

## Future Steps
 - **Next Steps**:
     - Multi-label Annotation
     - View progress status in more details:
         - Annotator progress
         - Annotation speed curve.
     - Project management feature:
         - Add annotator in a running project
         - Extend project after time out
         - Message broadcast to annotators.
 - **Next Next Steps**:
     - Active learning
     - Administrative dashboard
     - Annotator ranking
     - Faster Dispatcher
## Contributors
Mehdi Rahman

Ragib Ahsan

Special Thanks: Md. Kawser Munshi
