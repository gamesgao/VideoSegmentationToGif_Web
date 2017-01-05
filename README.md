# README #

The Web Server for the Video Segmentation To GIF Software 

## What is this repository for? ##

* this repository is designed to convert Video to GIF, with interactive user input, we can easily cutout the main part of the video and combine it with the background image, to generate the GIF.
* Ver1.0.0

## How do I get set up? ##

### Summary of set up ###
1. download this repository

```
    git clone https://github.com/gamesgao/VideoSegmentationToGif_Web.git
```

2. install the Dependencies

```
    npm install
```

3. run the project

```
    npm start
```

### Configuration ###

    .\routes\controllers\data.controller.js
change the value of isG to change the python way or C way

### Dependencies ###

#### python way ###

* NodeJS 6.9.2
* Python 2.7
* OpenCV 2.4.9 with FFmpeg
* Imageio

#### C way ####

* Boost
* FFMPEG
* Google protobuffer
* Google logging
* Google gflags
* Jsoncpp 

## Details ##

*please read the User Guidance*

## Who do I talk to? ##

* [Contact us](gamesgao@gmail.com)