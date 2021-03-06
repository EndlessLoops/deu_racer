<<<<<<< .mine
#-*-coding:utf-8-*-
||||||| .r42
=======
#!/usr/bin/env python
#-*-coding:utf-8-*-

>>>>>>> .r54
import numpy as np
import cv2
import matplotlib.pyplot as plt
import logging
from elapsed_time import ElapsedTime
from distance_calculator import DistanceCalculator
from rgb_color import RGBColor


logger = logging.getLogger('cv_test17')
logging.basicConfig(level=logging.INFO)
timer = ElapsedTime()
dist_calc = DistanceCalculator('parking')

MIN_MATCH_COUNT = 10
show_matched_points = True

# 최적화 사용
cv2.useOptimized()
cv2.setUseOptimized(True)

cap = cv2.VideoCapture()
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 10)

img1 = cv2.imread('parking_marker.png', cv2.IMREAD_COLOR)
<<<<<<< .mine
# img1 = cv2.imread('blocking_bar_marker.png', cv2.IMREAD_COLOR)
# img1 = cv2.imread('small_athletica2.jpg', cv2.IMREAD_COLOR)
#logger.debug(f'marker shape = {img1.shape}')
||||||| .r42
# img1 = cv2.imread('blocking_bar_marker.png', cv2.IMREAD_COLOR)
# img1 = cv2.imread('small_athletica2.jpg', cv2.IMREAD_COLOR)
logger.debug(f'marker shape = {img1.shape}')
=======
#logger.debug(f'marker shape = {img1.shape}')
>>>>>>> .r54

# Initiate SIFT detector
sift = cv2.xfeatures2d.SIFT_create()

while True:
    start_t = timer.start()

    ret, frame = cap.read()

    img2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # find the keypoints and descriptors with ORB
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)

    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    # store all the good matches as per Lowe's ratio test.
    good = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good.append(m)

    outer_dst_pts = np.float32([])
    if len(good) > MIN_MATCH_COUNT:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        outer_dst_pts = dst_pts
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()
        h, w, d = img1.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)

        frame = cv2.polylines(frame, [np.int32(dst)], True, (0,255,255), 3, cv2.LINE_AA)

        # 물체와의 거리 계산 및 표시
        dist = dist_calc.get_distance(dst[0], dst[3]) 
        logger.info('distance = %.2f' % dist)
        text = "%.2f cm" % dist
        h, w, d = frame.shape
        cv2.putText(frame, text, (10, h-20), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1,
                    color=RGBColor.BLUE, thickness=2, lineType=cv2.LINE_AA)
        if(int(dist) < 6):
          logger.info('parking is true')
    else:
        logging.debug("Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT))
        matchesMask = None

    # draw_params = dict(matchColor=(0, 255, 0),  # draw matches in green color
    #                    singlePointColor=None,
    #                    matchesMask=matchesMask,  # draw only inliers
    #                    flags=2)
    # img3 = cv2.drawMatches(img1, kp1, frame, kp2, good, None, **draw_params)
    #
    # cv2.imshow('match', img3)

    # dst_pts를 img2에 원으로 그리기
    if show_matched_points:
        for pt in outer_dst_pts:
            # print(pt)
            x,y = pt[0]
            # print(x,y)
            cv2.circle(frame, (x, y),3, (0,0,255), -1)

    cv2.imshow('frame', frame)
    end_t = timer.end()
    logger.debug('소요 시간: %.3f' % (timer.getTime(),))

    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()
