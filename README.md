# home-recorder

Detect, record and notifiy events in your home for your security.

## Feature

* event detection  
  * with cameras  
  * with gpio switch  
  * Event detection is automatically enabled when you go out of home with your smartphone, and is disabled when you come back home. This feature is offered by [the Android client app](https://github.com/nknytk/home-recorder-client).  
* notification about the event  
  * with email  
* record the event  
  * with cameras  
  * with mikes
  * send images and sound files via email  

## Requirements

* Raspbian or Ubuntu
* Python3
* webcam by Gerd Knorr for image capturing
* [raspberry-gipo-python](http://sourceforge.net/p/raspberry-gpio-python/wiki/Home/) for window/door switch using GPIO in Raspberry Pi

## Usage

typical usage

1. Setup Raspbian on a raspberry pi or Ubuntu on a PC.  
2. Connect web cameras with the device.  
3. Download home-recorder.
  * Click "Download ZIP" button on the github page, and unzip the donloaded file.  
  * `git clone https://github.com/nknytk/home-recorder.git`  
4. Run `./setup.sh` to install dependencies.  
5. Adjust direction of the cameras. Run `./camera_direction_config.sh`, and you will see a URL to view images from the cameras with your browser. This process is unneccesary if you have the Android client because you can watch camera with the client. 
6. Install the [client](https://github.com/nknytk/home-recorder-client) into your Android device.  
7. Write config files.
  * Set eventcheck interval, pairing information with the client to "conf/home-recorder.json."  
  * Set your mail settings to "conf/home-recorder.json." Web mails (i.e. gmail) are deprecated because they often block mails from unofficial clients. Use the account provided by your internet service porvider.
  * Set plugin-specific config to "conf/eventchecker.json", "conf/notifier.json" or "conf/recorder.json." If you want to config camera eventchecker, edit "conf/eventchecker.json." 
8. Run test with `./start.sh test`. Fix configs until you see "All components are OK." at last.
9. Start home-recorder with `./start.sh`.

## Config

Under construction

## ToDo list

* Write README  
How to use  
How to add feature
* ~~eventchecker~~  
~~Event detection with camera~~ done  
Circuit diagram for gpio switch
* notifier  
Notification with Google Cloud Messaging for Android  
Notification receiver for Andoird
* recorder  
Upload to online stroage
* Error handling
* Log handling

## Comment

Check out [Android client application](https://github.com/nknytk/home-recorder-client) if you're Android user!

## License

Copyright 2014 Yutaka Nakano

This software is released under the Apache License v2.
