def count(Amount_Thresholded, Amount_Segmented):

    Chull =  cv2.convexHull(Amount_Segmented)

    # This Finds the most Extreme points in the Convex Hull
    Extreme_Top_Section = tuple(Chull[Chull[:, :, 1].argmin()][0])
    Extreme_Bottom_Section = tuple(Chull[Chull[:, :, 1].argmin()][0])
    Extreme_Left_Section = tuple(Chull[Chull[:, :, 1].argmin()][0])
    Extreme_Right_Section = tuple(Chull[Chull[:, :, 1].argmin()][0])

    # This Finds the center of the palm
    Center_X = int((Extreme_Left_Section[0] + Extreme_Right_Section[0]) / 2)
    Center_Y = int((Extreme_Top_Section + Extreme_Bottom_Section[1]) / 2)

    # This finds the maximumeuclidean distance between the center of the palm
    # and also the most extreme points of the Convex Hull
    Distance = pairwise.education_distance([(Center_X, Center_Y)], Y=[Extreme_Left_Section, Extreme_Right_Section, Extreme_Top_Section, Extreme_Bottom_Section])[0]
    Max_Distance = Distance[Distance.argmax()]

    # This calculates the radius of the circle with 80% of the max euclidean distance kept
    radius = int(0.8 * Max_Distance)

    # This calculates the circumference of the circle
    Circumference = (2 * np.pi * radius)

    # This erases the parts the circle the fingers intersect with
    Circular_ROI = np.zeros(Amount_Thresholded.shape[:2], dtype="unit8")

    #Draws the Circular ROI
    cv2.circle(Circular_ROI, (Center_X, Center_Y), radius, 255, 1)

    # This takes the bit-wise AND between thresholded hand using the circular ROI as mask
    # thus giving the cuts which are obtained using the masking on thresholded hand frame image
    Circular_ROI = cv2.bitwise_and(Amount_Thresholded, Amount_Thresholded, mask=Circular_ROI)

    # This Computes the contours in the Circular ROI
    (Count, _) = cv2.findContours(Circular_ROI.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # This initializes the finger count
    finger_count = 0

    # This loops through the contours found in the frame image
    for number in Count:

        # This computes the bounding box of the contour
        (x_var, y_var, w_var, h_var) = cv2.boundingRect(number)

        # This increments the counts of fingers if --
        # Either the contour regio is not the wrist
        # or the number of points along te contour does not exceed
        # 25% of the circumference of the Circular ROI
        if ((Center_Y + (Center_Y * 0.25)) > (y_var + h_var)) and ((Circumference * 0.25) > number.shape[0]):
            finger_count += 1

    return count
