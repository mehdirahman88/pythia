**Pythia** is a web application developed as an initiative for helping researchers to build labeled dataset
with minimal effort by assigning annotators.


#### Supports
 - Text to text labeling.
 - Multiple annotators for simultaneous annotation.
 - Tracking project progress.
 - Pause and resume ongoing project.


#### Overview
 **Pythia** is easy to use. You have to:
  - Upload your sample data file of size up to 50 Mb and list of labels in a specified format.
  - Assign up to 10 annotators and run the project.

 When the project is ready for labeling:
  - Annotators will receive 5 unlabeled data from _Pythia Dispatcher_ each time they request through the project page.
	- Annotators will not receive data already annotated by them.


#### Setup
 - **Running Server and Database Setup**
	 - `export FLASK_APP=pythia`
	 - `flask init-db`
	 - `flask run --host 0.0.0.0 --port 5000`
	 - [Flask Quickstart](http://flask.pocoo.org/docs/1.0/quickstart/)
 - **Deployment**
	 - The app currently uses the built-in flask server.
	 - You may refer to the given `Dockerfile` if you want to dockerize.
	 - [Deployment Options](http://flask.pocoo.org/docs/1.0/deploying/)


#### Usage
 - **Client**
     - Sign up as Client
     - Create new project
         - File size has to be less than 50Mb.
         - File format has to be .csv.
         - File should contain one column named 'Sample', and a single sample data per row.
     - Start Project
 - **Annotator**
     - Sign up as Annotator
     - View running project list in the home page
         - Click on the link.
         - Label the samples.
         - Submit, then the page will refresh with new data.


#### Further Steps
 Possible next steps might be:
  - Multi-label Annotation
  - View progress status in more details
  	- Annotation speed curve.
    - Annotator's progress.
  - Project management features
	  - Add annotator in a running project
	  - Extend project after time out
	  - Message broadcast to annotators.
  - Active learning
  - Administrative dashboard
  - Annotator ranking
  - Faster Dispatcher
