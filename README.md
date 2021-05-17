# MLB-Player-Tracking - Analysis of MLB game footage with Python and OpenCV
## Initial video
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/gifs/initial_gif.gif?raw=true" width="840" height="500" />

To begin, I averaged all frames of the video to get a clearer view of the blank field. While most of the field is clear in the averaged image, locations where players/umpires stand still during the video still appear.

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/avgImage.jpg?raw=true" width="840" height="500" />

## Locating field elements

### Foul lines

First, I focused on finding both foul lines, as they are essential to accurately locating all 4 bases. To do this, I used a combination of a white color mask and OpenCV's Canny/HoughLinesP functions, which detects lines in a photo.

#### Masked
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/foulLineMask.jpg?raw=true" width="840" height="500" />

#### Detected lines
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/foulLineEdgesCanny.jpg?raw=true" width="840" height="500" />

Keeping only the two longest detected lines results in a segment of each foul line.

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/detectedFoulLines.jpg?raw=true" width="840" height="500" />

### Home Plate

Now that I've located both foul lines, finding home plate is as simple as extending each line across the image and determining their intersection point.

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/foulLinesAndHomePlate.jpg?raw=true" width="840" height="500" />

### Second Base

Knowing the location of the foul lines and home plate greatly limits the possible locations of second base. Because of the symmetries of the baseball diamond, a vertical line from home plate should cross through second base.

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/secondBaseUnrotated.jpg?raw=true" width="840" height="500" />

Unfortunately, the camera feed isn't perfectly level. However, because the foul lines are located, the image can be rotated to correct this.
Angle to rotate image by = (1st base line angle - 3rd base line angle) / 2

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/secondBaseStraightened.jpg?raw=true" width="840" height="500" />

Now that the image is straightened, second base must be located directly vertical of home plate. To find it's exact location, I took a 10 pixel-wide vertical splice of the image starting at home plate. I then applied a white color mask to the splice and located the biggest/brightest spot on the splice.

<table><tr><td vlign="center"><img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/secondBaseSplice.jpg?raw=true" width="20" height="500" /></td><td vlign="center"> RGB to HLS, white color mask, gaussian blur -> </td><td vlign="center"><img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/secondBaseSpliceMasked.jpg?raw=true" width="20" height="500" /></td></tr></table>

After applying a horizontal and reverse-rotational translation to the point, second base is located.

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/secondBaseLocated.jpg?raw=true" width="840" height="500" />

### First and Third Base

To get the location of first and third base, I decided to use two splices, one along each foul line, and average them. To get each splice, I rotated the image so that each foul line was horizontal. Then, after flipping the first base splice along the vertical axis and applying color filters/blurs, I averaged both images to create a bright white spot where first/third base was located. Using this method this ensured consistency of first/third base location.

<table>
<tr><td align="center">First base splice</td></tr>
<tr><td vlign="center"><img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/firstBaseSplice.jpg?raw=true" width="840" height="20" /></td></tr>
<tr><td align="center">First base splice flipped</td></tr>
<tr><td vlign="center"><img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/firstBaseSpliceFlipped.jpg?raw=true" width="840" height="20" /></td></tr>
<tr><td align="center">Third base splice</td></tr>
<tr><td vlign="center"><img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/thirdBaseSplice.jpg?raw=true" width="840" height="20" /></td></tr>
<tr><td align="center">Combined splice</td></tr>
<tr><td vlign="center"><img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/firstAndThirdAveraged.jpg?raw=true" width="840" height="20" /></td></tr>
</table>

First and third base located.

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/firstAndThirdBaseLocated.jpg?raw=true" width="840" height="500" />


## Player Tracking

To begin my player tracking, I created a mask for just the playing field to eliminate the crowd, stands, and dugouts.

INCLUDE METHOD/PHOTOS TO DO THIS (CONTOURS)

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/avgImageFieldMask.jpg?raw=true" width="840" height="500" />

I created an additional mask to filter out the oustide dirt/warning track to be used later.

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/avgImageGrassMask.jpg?raw=true" width="840" height="500" />

### Collecting Points

Next, I split the video into a list of frames and applied filters to each. Below is the first frame of the video.

Frame 1
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/firstFrame.jpg?raw=true" width="840" height="500" />

The first technique I used was to 'subtract' the averaged image from the frame which should highlight the moving parts of the frame (players/ball/umpires).

Subtracted image
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/frameSubtracted.jpg?raw=true" width="840" height="500" />

I then applied color filters to the subtracted image, revealing the figures in the frame.

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/detectDefensivePlayers.jpg?raw=true" width="840" height="500" />

Because the catcher, base coaches, and umpires move less during the play, subtracting the average image from the frame is less usefull. As a result, I decided to just use a series of color filters on the frame without subtraction to detect the other figures on the field.

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/detectCatcher.jpg?raw=true" width="840" height="500" />
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/detectOpposingPlayers.jpg?raw=true" width="840" height="500" />
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/detectUmpires.jpg?raw=true" width="840" height="500" />

Combining these filters and results in this figure mask.

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/combinedMasks.jpg?raw=true" width="840" height="500" />

I then used OpenCV's SimpleBlobDetector (with varying parameters) to detect figures in each of the filtered frames. Combining the detected blobs results in 15-30 points per frame.

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/detectedPoints.jpg?raw=true" width="840" height="500" />

As seen here, the first base umpire isn't detected and there are a few duplicate points. This will be accounted for when linking and filtering the points from each frame. For example, another frame from the video results in these detected points.

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/detectedPoints2.jpg?raw=true" width="840" height="500" />

The first base umpire is detected in this frame.

### Linking Points

Once points are gathered from each frame, they need to be linked together. To do this, I matched points from each frame by the minimum proximity value (difference between x, y, and blob size), creating chains of coordinates in the set of frames. If a chain wasn't close enough to a detected point a blank value was appended to the chain. Any points from a frame that weren't attached to a chain were discarded. After the chains were created, I filtered out any chains that had a long streak of null values, resulting in a set of the most complete chains. I then filtered out any duplicate chains, keeping the 'smoothest' in each case. This resulted in a location dataset for every offensive and defensive player, umpire, and base.

## Tracking Results
Tracked locations
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/gifs/tracked_gif.gif?raw=true" width="840" height="500" />

## Transposing locations onto the plane of the field

Using the locations of all 4 bases and knowing that the distance between each is 90 ft, I was able to create locate 2 'origin' points at the intersections of foul lines and base lines. These points help to account for the perspective distortion from the camera.

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/originPoints.jpg?raw=true" width="840" height="345" />

Next, I formed polynomial equations to calculate the distance from home plate along each foul line. I used three points for each equation: home plate, first/third base, and the outfield wall, all of which are known distances (at Yankee Stadium, the right and left field wall distances are 314 ft and 318 ft, respectively).

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/firstBaseLineGraph.JPG?raw=true" width="840" height="500" />
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/thirdBaseLineGraph.JPG?raw=true" width="840" height="500" />

Having both the origin points and the distance equations for each side of the field, I can now place any point from the video onto the plane of the field. For example, lets look at the second baseman from the first frame of the video.

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/transformationExample1.jpg?raw=true" width="840" height="500" />

To begin, I drew a line from each origin through the tracked point and onto the opposite foul line.

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/transformationExample2.JPG?raw=true" width="840" height="345" />

I then inputed the horizontal pixel index of foul line intersection points into their respective polynomial equations to determine the players location in relation to home plate.

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/transformationExample3.png?raw=true" width="840" height="500" />
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/transformationExample4.png?raw=true" width="840" height="500" />

This results in the x, y coordinate (first base line = x-axis) of the player on the plane of the field.

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/transformationExample5.jpg?raw=true" width="840" height="500" />

## Transposed Results
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/gifs/transposed_gif.gif?raw=true" width="840" height="500" />


