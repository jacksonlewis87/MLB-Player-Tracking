import csv
import cv2

videoFileName = 'video.mp4'

points = {}
with open('entities.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if row[0] != 'frameNumber':
            [frameNumber, entity, x, y, transformedX, transformedY] = row
            if int(frameNumber) not in points:
                points[int(frameNumber)] = []
            color = (0, 80, 0)
            if 'Coach' in entity:
                color = (60, 60, 200)
            elif 'Base' in entity or 'Plate' in entity:
                color = (0, 0, 0)
            elif 'batter' in entity or 'Runner' in entity:
                color = (0, 0, 89)
            elif 'umpire' in entity:
                color = (60, 0, 4)
            points[int(frameNumber)] += [[int(float(x)), int(float(y)), color]]

# Loop 20 times
for y in range(20):
    vid = cv2.VideoCapture(videoFileName)

    fCount = 0
    while vid.isOpened():  # play the video by reading frame by frame
        ret, frame = vid.read()

        if ret:
            for entity in points[fCount + 1]:
                cv2.circle(frame, (int(entity[0]), int(entity[1])), radius=5, color=entity[2], thickness=-1)
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            fCount += 1
        else:
            break

    vid.release()
