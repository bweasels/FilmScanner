# **Software For The Pi Film Scanner**

##Required external Packages and software versions
**Python 3.7.3**
1) Kivy v1.11.1
2) RPi.GPIO
3) pyDNG v3.4.4 [(Schoolpost's github)](https://github.com/schoolpost/PyDNG)
4) Numpy v1.18.5
5) OpenCV v4.0.1
6) PiCamera v1.7



##Installation
1) Copy these files over
2) Python FilmScanner.py
3) Enjoy!

#Notes!
- I've included several benchmarking scripts under TestScripts/ to help test different algorithms to improve white balance
 performance (Currently the white balance calculations slow everything down to ~7-9fps from 20fps)
- I've also included a set of dummy scripts to debug the UI when not on the Raspberry pi! These should have the same
class calls as the proper py versions, but will only output a blue frames.
- The guide to construct the film scanner and parts list ~~is here~~ _will be uploaded when I finally get around to making
a portfolio website._