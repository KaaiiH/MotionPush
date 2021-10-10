# Organize Imports
import cv2
import imutils
import numpy as np
from sklearn import metrics
import subprocess

# Global Variables
BackGround = None

def video_average(frame_image, Average_Framing):
    global BackGround

    # initialize the background
    if BackGround is None:
        BackGround = frame_image.copy().astype("float")
        return


    # computes averaged frame, this then updates the background
    cv2.accumulateWeighted(frame_image, BackGround, Average_Framing)


def segment(frame_image, threshold_amount=25):
    global BackGround

    # This finds the absolute difference between the background frame and the current frame
    difference = cv2.absdiff(BackGround.astype("uint8"), frame_image)

    # This is the threshold of the differnce imaging to get foreground imaging
    Amount_Thresholded = cv2.threshold(difference, threshold_amount, 255, cv2.THRESH_BINARY)[1]

    # This gets the contours in the thresholded imaging
    (count,_) = cv2.findContours(Amount_Thresholded.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    # returns None if no countours are detected
    if len(count) == 0:
        return
    else:
        # This is segemented based on countour area, tries to get the max countour (the hand)
        segemented = max (count, key=cv2.contourArea)
        return  (Amount_Thresholded, segemented)

def CountFingers(Amount_Thresholded, Amount_Segmented):

    Chull =  cv2.convexHull(Amount_Segmented)

    # This Finds the most Extreme points in the Convex Hull
    Extreme_Top_Section = tuple(Chull[Chull[:, :, 1].argmin()][0])
    Extreme_Bottom_Section = tuple(Chull[Chull[:, :, 1].argmax()][0])
    Extreme_Left_Section = tuple(Chull[Chull[:, :, 1].argmin()][0])
    Extreme_Right_Section = tuple(Chull[Chull[:, :, 1].argmax()][0])

    # This Finds the center of the palm
    Center_X = int((Extreme_Left_Section[0] + Extreme_Right_Section[0]) / 2)
    Center_Y = int((Extreme_Top_Section[1] + Extreme_Bottom_Section[1]) / 2)

    # This finds the maximumeuclidean distance between the center of the palm
    # and also the most extreme points of the Convex Hull
    Distance = metrics.pairwise.euclidean_distances([(Center_X, Center_Y)], Y=[Extreme_Left_Section, Extreme_Right_Section, Extreme_Top_Section, Extreme_Bottom_Section])[0]
    Max_Distance = Distance[Distance.argmax()]

    # This calculates the radius of the circle with 80% of the max euclidean distance kept
    radius = int(0.8 * Max_Distance)

    # This calculates the circumference of the circle
    Circumference = (2 * np.pi * radius)

    # This erases the parts the circle the fingers intersect with
    Circular_ROI = np.zeros(Amount_Thresholded.shape[:2], dtype="uint8")

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
        if (finger_count == 5):
            break

    return finger_count


if __name__ == "__main__":

    
    # This initializes what is the "weighted" average for the framing
    Weighted_Frames = 0.5

    # This gets the reference to the camera
    web_camera = cv2.VideoCapture(0)

    # These are the region of intersted coordinates (for edges of that part of frame)
    top_edge, right_edge, bottom_edge, left_edge = 10, 350, 440, 830

    # initializes the number of frames
    number_of_frames = 0

    # This is the initialization Variable for Finger Count
    Number_Of_Fingers = 0

    # This is a temporary variable to make updating print
    # less frequent. It too is initialized
    Temp_Var_Finger_Count = 0

    # Active Signal
    Active_Signal = 1000

    # Timer_Tracking_Var
    Timer_Track = 0

    # Internal Hand Signal "2" Tracker
    Commit_Var = 0

    # Internal Hand Signal "1" Tracker
    Push_Var = 0

    # Internal Hand Signal "0" Tracker
    Add_Var = 0

    # Internal Hand Signal "3" Tracker
    Pull_Var = 0

    # Internal Hand Signal "4" Tracker
    Check_Out_Var = 0

    # Ten Second Delay 
    Start_Up_Delay = 0 

    # This will kep looping till it is interrupted
    while(True):

        # The gets the current frame
        (grabbed, current_frame) = web_camera.read()

        # The frame is resized
        current_frame = imutils.resize(current_frame, width=700)

        # This flips the frame to make sure the current frame does not look relfected
        current_frame = cv2.flip(current_frame, 1)

        # This makes a copy of the frame
        copy_frame = current_frame.copy()

        # This gets the height and width of the frame
        (height, width) = current_frame.shape[:2]

        # This gets the ROI of the current frame
        ROI = current_frame[top_edge:bottom_edge, right_edge:left_edge]

        # This converts the ROI to grayscale and adds blur to the frame
        graying = cv2.cvtColor(ROI, cv2.COLOR_BGR2GRAY)
        graying = cv2.GaussianBlur(graying, (7, 7), 0)


        # For getting the background, api will look at image until the
        # the threshold
        if number_of_frames < 30:
            video_average(graying, Weighted_Frames)
        else:

            # This will segment the hand section of the frame
            hand_segment = segment(graying)

            # This checks to see if the hand region is segmented
            if hand_segment is not None:

                # if this is true, unpack the threshold image and segmented region
                (thresholded_hand, segmented_hand) = hand_segment

                # Counting Number of Fingers
                #Temp_Var_Finger_Count = CountFingers(thresholded_hand, segmented_hand)

                #if (Temp_Var_Finger_Count is not Number_Of_Fingers):
                #   Number_Of_Fingers = Temp_Var_Finger_Count
                Number_Of_Fingers = CountFingers(thresholded_hand, segmented_hand)

                # This draws the segmented region and then shows the frame
                cv2.drawContours(copy_frame, [segmented_hand + (right_edge, top_edge)], -1, (0, 0, 255))
                cv2.imshow("Thresholed", thresholded_hand)


        # This draws the segemented hand onto the frame
        cv2.rectangle(copy_frame, (left_edge, top_edge), (right_edge, bottom_edge), (0, 255, 0), 2)


        # The increments the number of frames
        number_of_frames += 1

        # Increments until 60 for "2" seconds of duration in Time
        Timer_Track +=1

        # Deals with incrementing amount of time for each handle signal
        if (Number_Of_Fingers == 2):
            Add_Var += 1
        elif (Number_Of_Fingers == 1):
            Commit_Var += 1
        elif (Number_Of_Fingers == 0):
            Push_Var += 1
        elif (Number_Of_Fingers == 3):
            Pull_Var += 1
        elif (Number_Of_Fingers == 4):
            Check_Out_Var += 1
        else:
            Active_Signal +=1

        # Handles Signal response within 2 second duration intervals
        if Timer_Track >= 30:
            if Add_Var >= 15:
                Active_Signal = 2
            elif Commit_Var >=15:
                Active_Signal = 1
            elif Push_Var >= 15:
                Active_Signal = 0
            elif Pull_Var >= 15:
                Active_Signal = 3
            elif Check_Out_Var >= 15:
                Active_Signal = 4
            else:
                Active_Signal = 1000

            print(Active_Signal)

        if Start_Up_Delay >= 300:
            # For getting the background, api will look at image until the
            # the threshold
            if(Active_Signal == 4):
                subprocess.call("gitcheckout.sh", shell=True)
                print("Checkout Signal")

            if(Active_Signal == 3):
                subprocess.call("gitpull.sh", shell=True)
                print("Pull Signal")

            if(Active_Signal == 2):
                subprocess.call("gitadd.sh", shell=True)
                print("Add Signal")

            if(Active_Signal == 1):
                subprocess.call("gitcommit.sh", shell=True)
                print("Commit Signal")

            if(Active_Signal == 0):
                subprocess.call("gitpush.sh", shell=True)
                print("Push Signal")

            Timer_Track = 0
            Commit_Var = 0
            Push_Var = 0
            Pull_Var = 0
            Add_Var = 0
            Check_Out_Var = 0
            Active_Signal = 1000
        else: 
            Start_Up_Delay += 1


        # This displays the frame with the segmented hnd in it
        key_press = cv2.waitKey(1) & 0xFF

        # if the user pressed the "q" key, then the loop will be interrupted
        if key_press == ord("q"):
            break

    # This helps free up memory
    web_camera.release()
    cv2.destroyAllWindows()
