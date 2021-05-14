# MLB-Player-Tracking - Analysis of MLB game footage with Python and OpenCV
## Initial video:
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/gifs/initial_gif.gif?raw=true" width="840" height="500" />

To begin, I averaged all frames of the video to get a clearer view of the blank field. While most of the field is clear in the averaged image, locations where players/umpires stand still during the video still appear.

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/avgImage.jpg?raw=true" width="840" height="500" />

## Locating field elements:

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

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/firstAndThirdBaseLocated.jpg?raw=true" width="840" height="500" />


Player Tracking:

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/avgImageFieldMask.jpg?raw=true" width="840" height="500" />
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/avgImageGrassMask.jpg?raw=true" width="840" height="500" />
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/firstFrame.jpg?raw=true" width="840" height="500" />

frame - avg image
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/detectDefensivePlayers.jpg?raw=true" width="840" height="500" />
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/detectCatcher.jpg?raw=true" width="840" height="500" />
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/detectOpposingPlayers.jpg?raw=true" width="840" height="500" />
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/detectUmpires.jpg?raw=true" width="840" height="500" />
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/combinedMasks.jpg?raw=true" width="840" height="500" />
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/detectedPoints.jpg?raw=true" width="840" height="500" />
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/detectedPoints2.jpg?raw=true" width="840" height="500" />


Using this averaged image, a white color mask, and Canny/ HoughLinesP, I gathered points along both foul lines. Using the intersection of the two these lines as the location of home plate, I rotated the image about home plate so that both foul lines were at an equal angle from the horizonal. Then, to get the location of second base, I used a white color mask on a vertical slice from home plate. To get the location of first and third base, I rotated the image about home plate twice so that each foul line was horizontal. Then, I placed a horizontal slice of each image (one flipped) onto each other, creating a bright white spot where first/third base was located. This ensured consistency of first/third base location. Finally, using the distance between the spot and home plate, I placed each base along it’s respective foul line. Once I had these locations, I was able to setup a transposition onto the playing field. To do this, I calculated the intersection point between each foul line and the line from first/third base to second base. Then, to transpose any observed point, I drew lines from each ‘origin’ point through the observed point. Using the angle difference between these lines and the foul lines, along with a foot to degree ratio calculated with the 90ft distance between bases, I was able to get the x, y location of any observed point in the video (first base line = x-axis). The transposition was less accurate in the outfield, so I left the non-transposed points in my csv file. As far as image processing, I used a combination of masks to track figures on the field. First, I created a mask for just the playing field to eliminate the crowd, stands, and dugouts. My player detection method revolved around utilizing OpenCV and SimpleBlobDetector. I used a combination of white/dark masks and image subtraction (using the average image from before) on each frame. This resulted in 15-30 points for each frame, which I connected between frames using proximity calculations and gap restrictions. Finally, I filtered out duplicate and choppy tracking paths. This resulted in a location dataset for every offensive and defensive player, umpire, and base.



Results:
Tracked locations:
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/gifs/tracked_gif.gif?raw=true" width="840" height="500" />


Transpositions
<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/images/transformationGrid.jpg?raw=true" width="840" height="500" />

<img src="https://github.com/jacksonlewis87/MLB-Player-Tracking/blob/inital_upload/media/gifs/transposed_gif.gif?raw=true" width="840" height="500" />


