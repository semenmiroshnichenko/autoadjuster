# autoadjuster
This is autoadjuster, a small tool supposed to allow you test and adjust your astrotracker indoor.

# Usage
First, you have to know the pixel scale (AKA image scale) for you camera + objective lens. You can calculate it based on known focal length of your lens and size of a single pixel on your camera's sensor. Pixel scale is in this case just ps=atan(pixel size / focal lenth). Please be sure you are using same dimensions (like mm). You can use online calculator too, I just asked google for "image scale calculator" and found http://celestialwonders.com/tools/imageScaleCalc.html

You can get your image scale more precisely by using astrometry.net. You do upload one of your astro fotos made with camera and lens you supposed to use with this script. Then go to caliblation results and search for a pixel scale value.

With known pixel scale open this script in text editor and change the value of variable pixelScaleInArcsecPerPixel to your value.

Then you put a camera on your astrotracker, start it and do shots every let say 10 seconds. Delay between shots should not be exact as script will read the time from EXIF-information in pictures.

Your camera should be positioned perpendicular to the axis of rotation.

After some minutes of shots, copy pictures from camera to the PC and run a script with a full path to the directory with pictures as a first command line argument, like "python autoadjuster.py /home/test/astrostacker_pictures/"