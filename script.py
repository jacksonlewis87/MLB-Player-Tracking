import csv
import cv2
import numpy as np
import imutils


def angleBetweenVectors(x1, y1, x2, y2, originX, originY):
    xa = x1 - originX
    ya = y1 - originY
    xb = x2 - originX
    yb = y2 - originY
    return (np.arccos((xa * xb + ya * yb) / (pow(pow(xa, 2) + pow(ya, 2), .5) * pow(pow(xb, 2) + pow(yb, 2), .5))) / np.pi) * 180


def toRadians(rad):
    return (rad / 180) * np.pi


def disBetweenPoints(a, b):
    tot = 0
    for i in range(len(a) - 1):
        tot += pow(a[i] - b[i], 2)
    return pow(tot, .5)


def findStreakSection(maxPointFrame, pointSection, maxPointDis):
    streaks = []
    for p in maxPointFrame:
        streaks += [[p, [p], 0]]
    for newPoints in pointSection:
        oldToNew = {}
        for i in range(len(streaks)):
            oldToNew[i] = []
            for j in range(len(newPoints)):
                dis = disBetweenPoints(streaks[i][0], newPoints[j])
                if dis < maxPointDis:
                    oldToNew[i] += [[j, dis]]
            oldToNew[i].sort(key=lambda p: p[1])

        newToOld = {}
        for i in range(len(newPoints)):
            newToOld[i] = []
            for j in range(len(streaks)):
                dis = disBetweenPoints(newPoints[i], streaks[j][0])
                if dis < maxPointDis:
                    newToOld[i] += [[j, dis]]
            newToOld[i].sort(key=lambda p: p[1])

        toMatchOld = [i for i in range(len(streaks))]
        toMatchNew = [i for i in range(len(newPoints))]

        while len(toMatchOld) > 0 and len(toMatchNew) > 0:
            oldMatchPot = toMatchOld[0]
            while len(oldToNew[oldMatchPot]) > 0 and oldToNew[oldMatchPot][0][0] not in toMatchNew:
                oldToNew[oldMatchPot].pop(0)
                oldMatchPot = toMatchOld[0]
            if len(oldToNew[oldMatchPot]) > 0 and len(newToOld[oldToNew[oldMatchPot][0][0]]) > 0 and \
                    newToOld[oldToNew[oldMatchPot][0][0]][0][0] == oldMatchPot:
                # append new to existing streak
                streaks[oldMatchPot] = [newPoints[oldToNew[oldMatchPot][0][0]],
                                        streaks[oldMatchPot][1] + [newPoints[oldToNew[oldMatchPot][0][0]]], 0]
                toMatchNew.remove(oldToNew[oldMatchPot][0][0])
                toMatchOld.remove(oldMatchPot)
            else:
                # no points close enough to streak
                streaks[oldMatchPot][1] += [None]
                streaks[oldMatchPot][2] += 1
                toMatchOld.remove(oldMatchPot)

        if len(toMatchOld) > 0:
            for i in toMatchOld:
                streaks[i][1] += [None]
                streaks[i][2] += 1
    return streaks


def findCompleteStreaks(points, maxBreak):
    lengths = [len(p) for p in points]
    maxIndex = lengths.index(max(lengths))
    secondStreaks = findStreakSection(points[maxIndex], points[maxIndex + 1:], 20)
    firstPoints = points[:maxIndex]
    firstPoints.reverse()
    streaks = findStreakSection(points[maxIndex], firstPoints, 20)

    for i in range(len(streaks)):
        streaks[i][1].reverse()
        streaks[i][1] += secondStreaks[i][1][1:]

    completeStreaks = [i for i in range(len(streaks))]
    biggestBreak = maxBreak

    for j in range(len(streaks)):
        noneCount = 0
        for i in range(len(streaks[j][1]) - biggestBreak):
            if streaks[j][1][i] is None:
                noneCount += 1
                if noneCount == biggestBreak:
                    completeStreaks.remove(j)
                    break
            else:
                noneCount = 0

    streakPoints = [streaks[c][1] for c in completeStreaks]
    return streakPoints


def removeStreaksFromPoints(points, streakPoints):
    for fIndex in range(len(points)):
        for sIndex in range(len(streakPoints)):
            if streakPoints[sIndex][fIndex] is not None:
                points[fIndex].remove(streakPoints[sIndex][fIndex])


def mergePoints(points, newPoints):
    for i in range(len(points)):
        points[i] += newPoints[i]


def fillNones(streak):
    if streak[0] is None:
        notNoneIndex = 1
        while streak[notNoneIndex] is None:
            notNoneIndex += 1
        while notNoneIndex > 0:
            streak[notNoneIndex - 1] = streak[notNoneIndex]
            notNoneIndex -= 1

    noneStart = None
    for i in range(len(streak)):
        if streak[i] is None:
            if noneStart is None:
                noneStart = i
        else:
            if noneStart is not None:
                xInc = (streak[i][0] - streak[noneStart - 1][0]) / (i - noneStart + 1)
                yInc = (streak[i][1] - streak[noneStart - 1][1]) / (i - noneStart + 1)
                for j in range(i - noneStart):
                    streak[noneStart + j] = [streak[noneStart + j - 1][0] + xInc, streak[noneStart + j - 1][1] + yInc, 0]
                noneStart = None
    # Trailing Nones
    if noneStart is not None:
        for i in range(len(streak) - noneStart):
            streak[noneStart + i] = streak[noneStart - 1]


def getIntersectionOfLines(line1, line2):
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2
    x = ((x3 - x4) * ((y2 - y1) * x1 + (x1 - x2) * y1) - (x1 - x2) * ((y4 - y3) * x3 + (x3 - x4) * y3)) / ((y2 - y1) * (x3 - x4) - (y4 - y3) * (x1 - x2))
    y = ((y2 - y1) * ((y4 - y3) * x3 + (x3 - x4) * y3) - (y4 - y3) * ((y2 - y1) * x1 + (x1 - x2) * y1)) / ((y2 - y1) * (x3 - x4) - (y4 - y3) * (x1 - x2))
    return (x, y)


def transformCameraPoint(x, y):
    point = getIntersectionOfLines([homePlateX, homePlateY, firstBaseLoc[0], firstBaseLoc[1]], [lOrigin[0], lOrigin[1], x, y])
    firstBaseFoulLinePoint = lDegreeLength * angleBetweenVectors(point[0], point[1], homePlateX, homePlateY, lOrigin[0], lOrigin[1])
    if angleBetweenVectors(point[0], point[1], lOrigin[0], lOrigin[1] + 100, lOrigin[0], lOrigin[1]) < angleBetweenVectors(homePlateX, homePlateY, lOrigin[0], lOrigin[1] + 100, lOrigin[0], lOrigin[1]):
        firstBaseFoulLinePoint = firstBaseFoulLinePoint * -1
    point = getIntersectionOfLines([homePlateX, homePlateY, thirdBaseLoc[0], thirdBaseLoc[1]], [rOrigin[0], rOrigin[1], x, y])
    thirdBaseFoulLinePoint = rDegreeLength * angleBetweenVectors(point[0], point[1], homePlateX, homePlateY, rOrigin[0], rOrigin[1])
    if angleBetweenVectors(point[0], point[1], rOrigin[0], rOrigin[1] + 100, rOrigin[0], rOrigin[1]) < angleBetweenVectors(homePlateX, homePlateY, rOrigin[0], rOrigin[1] + 100, rOrigin[0], rOrigin[1]):
        thirdBaseFoulLinePoint = thirdBaseFoulLinePoint * -1
    return (firstBaseFoulLinePoint, thirdBaseFoulLinePoint)


videoFileName = 'video.mp4'

# Create average image
video = cv2.VideoCapture(videoFileName)
frames = np.empty((int(video.get(cv2.CAP_PROP_FRAME_COUNT)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), 3), np.dtype('uint8'))
count = 0
while video.isOpened():
    valid, frame = video.read()

    if valid:
        frames[count] = frame
        count += 1
    else:
        break
video.release()
avgImage = frames.mean(axis=0).astype("uint8")
avgHLS = cv2.cvtColor(avgImage, cv2.COLOR_BGR2HLS)

# Find foul lines
foulLineMask = cv2.inRange(avgHLS, np.array([0, 250, 0]), np.array([255, 255, 255]))
foulLineBlur = cv2.GaussianBlur(foulLineMask, (5, 5), 0)
foulLineEdges = cv2.Canny(foulLineBlur, 50, 150, 3)
foulLines = cv2.HoughLinesP(foulLineEdges, 1, np.pi / 180, 15, np.array([]), 50, 20)
lineLengths = [[i, pow(pow(p[0][0] - p[0][2], 2) + pow(p[0][1] - p[0][3], 2), .5)] for i, p in enumerate(foulLines)]
lineLengths.sort(key=lambda l: l[1], reverse=True)
longestLines = [foulLines[l[0]] for l in lineLengths[0:2]]

# Calc location of home plate (use intersection of foul lines)
x1, y1, x2, y2 = longestLines[0][0]
x3, y3, x4, y4 = longestLines[1][0]
homePlateX = ((x3-x4) * ((y2-y1)*x1 + (x1-x2)*y1) - (x1-x2) * ((y4-y3)*x3 + (x3-x4)*y3)) / ((y2-y1) * (x3-x4) - (y4-y3) * (x1-x2))
homePlateY = ((y2-y1) * ((y4-y3)*x3 + (x3-x4)*y3) - (y4-y3) * ((y2-y1)*x1 + (x1-x2)*y1)) / ((y2-y1) * (x3-x4) - (y4-y3) * (x1-x2))
homePlateLoc = (homePlateX, homePlateY)

# Determine first/third foul lines
linePoints = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
linePoints.sort(key=lambda p: p[0])
lPoint = linePoints[0]
rPoint = linePoints[3]

# Find difference in angles to straighten video
lAngle = angleBetweenVectors(lPoint[0], lPoint[1], homePlateX - 100, homePlateY, homePlateX, homePlateY)
rAngle = angleBetweenVectors(rPoint[0], rPoint[1], homePlateX + 100, homePlateY, homePlateX, homePlateY)
rotDiff = (lAngle - rAngle) / 2

# Find Second Base by rotating frame, drawing a vertical line, and filtering white color
rotationMatrix = cv2.getRotationMatrix2D((homePlateX, homePlateY), rotDiff, 1.0)
straightenedImage = cv2.warpAffine(avgImage, rotationMatrix, avgImage.shape[1::-1], flags=cv2.INTER_LINEAR)
secondBaseRect = straightenedImage[0: int(homePlateY), int(homePlateX) - 5: int(homePlateX) + 5]
hsvRect = cv2.cvtColor(secondBaseRect, cv2.COLOR_BGR2HLS)
maskRect = cv2.inRange(hsvRect, np.array([0, 250, 0]), np.array([255, 255, 255]))
blurRect = cv2.GaussianBlur(maskRect, (5, 5), 0)
rotSecondBaseLoc = (homePlateX, cv2.minMaxLoc(blurRect)[3][1])

# Rotate Second Base point back to camera aspect
homeToSecondDis = pow(pow(homePlateX - rotSecondBaseLoc[0], 2) + pow(homePlateY - rotSecondBaseLoc[1], 2), .5)
secondBaseLoc = (homePlateX + (np.sin(toRadians(rotDiff)) * homeToSecondDis), homePlateY - homeToSecondDis)

# Find First/Third Base by rotating average image so first/third foul line are horizontal and merging the two
rotationMatrix = cv2.getRotationMatrix2D((homePlateX, homePlateY), lAngle, 1.0)
thirdRotation = cv2.warpAffine(avgImage, rotationMatrix, avgImage.shape[1::-1], flags=cv2.INTER_LINEAR)
thirdRect = thirdRotation[int(homePlateY) - 5: int(homePlateY) + 5, 0: int(homePlateX)]
hsvRect = cv2.cvtColor(thirdRect, cv2.COLOR_BGR2HLS)
maskRect = cv2.inRange(hsvRect, np.array([0, 250, 0]), np.array([255, 255, 255]))
thirdBlurRect = cv2.GaussianBlur(maskRect, (5, 5), 0)

# Flip and rotate the first base image
rotationMatrix = cv2.getRotationMatrix2D((homePlateX, homePlateY), rAngle, 1.0)
flippedAvgImage = cv2.flip(avgImage, 1)
firstRotation = cv2.warpAffine(flippedAvgImage, rotationMatrix, avgImage.shape[1::-1], flags=cv2.INTER_LINEAR)
firstRect = thirdRotation[int(homePlateY) - 5: int(homePlateY) + 5, 0: int(homePlateX)]
hsvRect = cv2.cvtColor(firstRect, cv2.COLOR_BGR2HLS)
maskRect = cv2.inRange(hsvRect, np.array([0, 250, 0]), np.array([255, 255, 255]))
firstBlurRect = cv2.GaussianBlur(maskRect, (5, 5), 0)

# Place first base (flipped image) and third base horizonal images on top of eachother and average the image.
# This creates a very bright white spot to determine the correct location of the bases.
combined = cv2.addWeighted(thirdBlurRect, 1, firstBlurRect, 0, 0.0)
firstThirdOffset = homePlateX - cv2.minMaxLoc(combined)[3][0]
firstBaseLoc = (homePlateX + (firstThirdOffset * np.cos(toRadians(rAngle))), homePlateY - (firstThirdOffset * np.sin(toRadians(rAngle))))
thirdBaseLoc = (homePlateX - (firstThirdOffset * np.cos(toRadians(lAngle))), homePlateY - (firstThirdOffset * np.sin(toRadians(lAngle))))

# Transformation constants
lOrigin = getIntersectionOfLines([homePlateX, homePlateY, thirdBaseLoc[0], thirdBaseLoc[1]], [firstBaseLoc[0], firstBaseLoc[1], secondBaseLoc[0], secondBaseLoc[1]])
rOrigin = getIntersectionOfLines([homePlateX, homePlateY, firstBaseLoc[0], firstBaseLoc[1]], [thirdBaseLoc[0], thirdBaseLoc[1], secondBaseLoc[0], secondBaseLoc[1]])
lDegreeLength = 90 / angleBetweenVectors(firstBaseLoc[0], firstBaseLoc[1], homePlateX, homePlateY, lOrigin[0], lOrigin[1])
rDegreeLength = 90 / angleBetweenVectors(thirdBaseLoc[0], thirdBaseLoc[1], homePlateX, homePlateY, rOrigin[0], rOrigin[1])

# Mask for field (all dirt/grass)
fieldMask = cv2.inRange(avgHLS, np.array([0, 0, 0]), np.array([15, 255, 255])) + \
            cv2.inRange(avgHLS, np.array([172, 0, 0]), np.array([180, 255, 255])) + \
            cv2.inRange(avgHLS, np.array([36, 0, 0]), np.array([86, 255, 255]))
fieldMask = cv2.erode(fieldMask, None, iterations=2)
fieldMask = cv2.dilate(fieldMask, None, iterations=2)
fieldContours = cv2.findContours(fieldMask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
fieldContours = imutils.grab_contours(fieldContours)
maxFieldContour = max(fieldContours, key=cv2.contourArea)
fieldContourMask = np.ones(avgImage.shape[:2], dtype="uint8") * 255
cv2.drawContours(fieldContourMask, [maxFieldContour], -1, 0, -1)
inverseFieldContourMask = 255 - fieldContourMask

# No outside dirt/warning track
grassMask = cv2.inRange(avgHLS, np.array([36, 0, 0]), np.array([86, 255, 255]))
grassMask = cv2.erode(grassMask, None, iterations=2)
grassMask = cv2.dilate(grassMask, None, iterations=2)
grassContours = cv2.findContours(grassMask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
grassContours = imutils.grab_contours(grassContours)
maxGrassContour = max(grassContours, key=cv2.contourArea)
grassContourMask = np.ones(avgImage.shape[:2], dtype="uint8") * 255
cv2.drawContours(grassContourMask, [maxGrassContour], -1, 0, -1)
inverseGrassContourMask = 255 - grassContourMask

# Regular mask detector
params = cv2.SimpleBlobDetector_Params()
params.filterByArea = True
params.minArea = 20
params.filterByColor = True
params.blobColor = 255
params.filterByCircularity = True
params.minCircularity = 0.1
params.filterByConvexity = True
params.minConvexity = 0.1
params.filterByInertia = True
params.minInertiaRatio = 0.01
regularDetector = cv2.SimpleBlobDetector_create(params)

# Dark color mask detector
params = cv2.SimpleBlobDetector_Params()
params.filterByArea = True
params.minArea = 10
params.filterByColor = True
params.blobColor = 255
params.filterByCircularity = False
params.filterByConvexity = False
params.filterByInertia = False
darkDetector = cv2.SimpleBlobDetector_create(params)

playerPoints = []
offensePoints = []
catcherPoints = []
umpirePoints = []

for frame in frames:
    # Find defensive players
    diff = cv2.subtract(frame, avgImage)
    diffMasked = cv2.bitwise_and(diff, diff, mask=inverseFieldContourMask)
    diffFiltered = cv2.inRange(diffMasked, np.array([22, 0, 0]), np.array([255, 255, 255]))
    diffBlurred = cv2.GaussianBlur(diffFiltered, (5, 5), 0)
    keyPoints = regularDetector.detect(diffBlurred)
    playerPoints += [[[keyPoint.pt[0], keyPoint.pt[1], keyPoint.size] for keyPoint in keyPoints]]

    # Find opposing players (dressed in white)
    whiteMask = cv2.inRange(frame, np.array([250, 250, 250]), np.array([255, 255, 255]))
    diffWhiteFiltered = cv2.bitwise_and(diffFiltered, diffFiltered, mask=whiteMask)
    diffWhiteBlurred = cv2.GaussianBlur(diffWhiteFiltered, (5, 5), 0)
    keyPoints = regularDetector.detect(diffWhiteBlurred)
    offensePoints += [[[keyPoint.pt[0], keyPoint.pt[1], keyPoint.size] for keyPoint in keyPoints]]

    # Find catcher
    frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    frameThresholdMask = cv2.inRange(frameHSV, (74, 0, 0), (134, 142, 103))
    frameMasked = cv2.bitwise_and(frameHSV, frameHSV, mask=frameThresholdMask)
    frameDiffCropped = cv2.bitwise_and(frameMasked, frameMasked, mask=inverseGrassContourMask)
    frameDiffCroppedColor = cv2.cvtColor(frameDiffCropped, cv2.COLOR_BGR2GRAY)
    nonBlackMask = cv2.inRange(frameDiffCroppedColor, 20, 255)
    frameDiffCroppedColor[nonBlackMask > 0] = 255
    frameDiffCroppedColor = cv2.GaussianBlur(frameDiffCroppedColor, (5, 5), 0)
    keyPoints = darkDetector.detect(frameDiffCroppedColor)
    catcherPoints += [[[keyPoint.pt[0], keyPoint.pt[1], keyPoint.size] for keyPoint in keyPoints]]

    # Find umpires
    frameThresholdMask = cv2.inRange(frameHSV, (74, 0, 0), (180, 255, 81))
    frameMasked = cv2.bitwise_and(frameHSV, frameHSV, mask=frameThresholdMask)
    frameDiffCropped = cv2.bitwise_and(frameMasked, frameMasked, mask=inverseGrassContourMask)
    frameDiffCroppedColor = cv2.cvtColor(frameDiffCropped, cv2.COLOR_BGR2GRAY)
    nonBlackMask = cv2.inRange(frameDiffCroppedColor, 20, 255)
    frameDiffCroppedColor[nonBlackMask > 0] = 255
    frameDiffCroppedColor = cv2.GaussianBlur(frameDiffCroppedColor, (5, 5), 0)
    keyPoints = darkDetector.detect(frameDiffCroppedColor)
    umpirePoints += [[[keyPoint.pt[0], keyPoint.pt[1], keyPoint.size] for keyPoint in keyPoints]]

streakPoints = []
points = umpirePoints
umpireStreaks = findCompleteStreaks(points, 150)
removeStreaksFromPoints(points, umpireStreaks)
mergePoints(points, catcherPoints)
newStreaks = findCompleteStreaks(points, 130)
streakPoints += newStreaks
removeStreaksFromPoints(points, newStreaks)
opposingStreaks = findCompleteStreaks(offensePoints, 200)
newStreaks = findCompleteStreaks(playerPoints, 40)
streakPoints += newStreaks
removeStreaksFromPoints(playerPoints, newStreaks)
mergePoints(points, playerPoints)
newStreaks = findCompleteStreaks(points, 10)
streakPoints += newStreaks

# Format streaks
streaks = []
for streakP in streakPoints:
    streak = []
    for i in range(len(streakP)):
        if streakP[i] is None:
            streak += [None]
        else:
            streak += [streakP[i][0:2]]
    streaks += [streak]

# Fill holes in streaks
for streak in streaks:
    fillNones(streak)

for streak in opposingStreaks:
    fillNones(streak)

for streak in umpireStreaks:
    fillNones(streak)

# Remove players not on field at start of play (on deck player)
numOfStreaks = len(streaks)
for streakI in range(len(streaks)):
    if cv2.pointPolygonTest(maxGrassContour, (streaks[numOfStreaks - streakI - 1][0][0], streaks[numOfStreaks - streakI - 1][0][1]), False) != 1.0:
        streaks.pop(numOfStreaks - streakI - 1)

# Remove duplicate opposing team players (white)
numOfStreaks = len(streaks)
for i in range(len(streaks)):
    for whiteStreak in opposingStreaks:
        totDiff = 0
        for f in range(len(streaks[0])):
            totDiff += disBetweenPoints(streaks[numOfStreaks - i - 1][f], whiteStreak[f])
        if (totDiff / len(streaks[0])) < 2:
            streaks.pop(numOfStreaks - i - 1)

# Remove non-smooth streaks
numOfBigJumps = []
numOfStreaks = len(streaks)
for streak in streaks:
    bigJumps = 0
    for i in range(len(streak) - 1):
        if disBetweenPoints(streak[i], streak[i + 1]) > 2:
            bigJumps += 1
    numOfBigJumps += [bigJumps]

for i in range(len(numOfBigJumps)):
    # if 5% or more points 'jump', remove streak
    if (numOfBigJumps[numOfStreaks - i - 1] / len(streaks[0])) > .05:
        streaks.pop(numOfStreaks - i - 1)
        numOfBigJumps.pop(numOfStreaks - i - 1)

entities = []

# Determine third base coach
thirdBaseCoachIndex = None
minDis = 1000
for streakI in range(len(opposingStreaks)):
    if (((((homePlateLoc[1] - thirdBaseLoc[1]) / (homePlateLoc[0] - thirdBaseLoc[0])) * (opposingStreaks[streakI][0][0] - thirdBaseLoc[0])) + thirdBaseLoc[1]) < opposingStreaks[streakI][0][1]) and disBetweenPoints(opposingStreaks[streakI][0], [thirdBaseLoc[0], thirdBaseLoc[1]]) < minDis:
        minDis = disBetweenPoints(opposingStreaks[streakI][0], [thirdBaseLoc[0], thirdBaseLoc[1]])
        thirdBaseCoachIndex = streakI

if thirdBaseCoachIndex is not None:
    entities += [['thirdBaseCoach', opposingStreaks[thirdBaseCoachIndex]]]
    opposingStreaks.pop(thirdBaseCoachIndex)

# Determine first base coach
firstBaseCoachIndex = None
minDis = 1000
for streakI in range(len(opposingStreaks)):
    if (((((homePlateLoc[1] - firstBaseLoc[1]) / (homePlateLoc[0] - firstBaseLoc[0])) * (opposingStreaks[streakI][0][0] - firstBaseLoc[0])) + firstBaseLoc[1]) < opposingStreaks[streakI][0][1]) and disBetweenPoints(opposingStreaks[streakI][0], [firstBaseLoc[0], firstBaseLoc[1]]) < minDis:
        minDis = disBetweenPoints(opposingStreaks[streakI][0], [firstBaseLoc[0], firstBaseLoc[1]])
        firstBaseCoachIndex = streakI

if firstBaseCoachIndex is not None:
    entities += [['firstBaseCoach', opposingStreaks[firstBaseCoachIndex]]]
    opposingStreaks.pop(firstBaseCoachIndex)

# Determine batter
batterIndex = None
minDis = 1000
for streakI in range(len(opposingStreaks)):
    if disBetweenPoints(opposingStreaks[streakI][0], [homePlateLoc[0], homePlateLoc[1]]) < minDis:
        minDis = disBetweenPoints(opposingStreaks[streakI][0], [homePlateLoc[0], homePlateLoc[1]])
        batterIndex = streakI

if batterIndex is not None:
    entities += [['batter', opposingStreaks[batterIndex]]]
    opposingStreaks.pop(batterIndex)

for streak in opposingStreaks:
    entities += [['baseRunner', streak]]

for streak in umpireStreaks:
    entities += [['umpire', streak]]

for streak in streaks:
    entities += [['defender', streak]]

with open('entities.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['frameNumber', 'entity', 'x', 'y', 'transformedX', 'transformedY'])
    bases = [['firstBase', firstBaseLoc], ['secondBase', secondBaseLoc], ['thirdBase', thirdBaseLoc], ['homePlate', homePlateLoc]]
    for base in bases:
        for fIndex in range(len(entities[0][1])):
            # Transformation occurs here
            transformedPoint = transformCameraPoint(base[1][0], base[1][1])
            writer.writerow([fIndex + 1, base[0], base[1][0], base[1][1], transformedPoint[0], transformedPoint[1]])
    for entity in entities:
        for fIndex in range(len(entity[1])):
            # Transformation occurs here
            transformedPoint = transformCameraPoint(entity[1][fIndex][0], entity[1][fIndex][1])
            writer.writerow([fIndex + 1, entity[0], entity[1][fIndex][0], entity[1][fIndex][1], transformedPoint[0], transformedPoint[1]])
