# HRI-Project

Project repository for the course "Human-Robot Interactions" helded in the master degree course of "Artifial Intelligence & Robotics" @ Sapienza University of Rome.

## Abstract
Nowadays, with the rapid growth of the traditional industries, intelligent robots and automated systems are widely used in the hospitality industry. In particular the application developed in this project is meant to be used in the catering sector, for example inside a restaurant. The idea behind this project is to automate and personalize the experience of the user inside a restaurant with the help of a robot; in particular the robot used for the development of the application is a simulated version of the known robot ”Pepper”. Here are briefly defined the main developed functionalities: Pepper, under the will of the user, can register in its database a picture of him and his personal information; if the user is correctly registered, Pepper can perform a recognition through a facerecognition model, in order to provide to him a personalized service based on the registered data; regardless of the fact that the user is registered or not, Pepper has an interface to show the menu' and collect the order of the customer, but in this case for registered users there is an additional functionality that allows to speed up the order; the last interface of the application offers a funny way to interact with Pepper through an imitation game performed by the robot. This project wants to show how some operations inside a restaurant can be integrated and personalized through a robotic system, with the advantage of a much more fast and personalized service.

## Project
The project was developed using a Docker image containing all the necessary libraries to interact with the simulated robot, in particular the *NAOQi* and *ROS* modules. The Pepper simulator used is the one offered by AndroidStudio, while a browser is used to simulate Pepper's tablet. 
The application was developed using:
- Python 2.7
- HTML/CSS
- Javascript

The libraries used to implement the face recognition features are:
- OpenCV
- dlib
- face_recognition

A simulation of the possible interactions developed with Peppers is showed in the video linked below.

## [Report](https://github.com/kevinmunda/HRI-Project/blob/06623daf6af4fb0cd5df0fc51b802bd5d6c552f0/HRI%20-%20Report.pdf)
## [Video](https://github.com/kevinmunda/HRI-Project/blob/8cb570d8e31e5b37d4479d1d53469f8ef54d43ab/HRI%20-%20Video.mp4)
