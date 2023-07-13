
# import the necessary packages
import cv2
import argparse


class userCropTable:

    def __init__(self,image_path):
        self.ref_point = []
        self.image_path=image_path
        self.createAlerts()
        self.initiateMainLoop()

    def shape_selection(self,event, x, y, flags, param):

        # now let's initialize the list of reference point

        crop = False

        # grab references to the global variables
        #global ref_point, crop

        # if the left mouse button was clicked, record the starting
        # (x, y) coordinates and indicate that cropping is being performed
        if event == cv2.EVENT_LBUTTONDOWN:
            #print("lbuttondown")
            self.ref_point = [(x, y)]
            #print(self.ref_point)

        # check to see if the left mouse button was released
        elif event == cv2.EVENT_LBUTTONUP:
            # record the ending (x, y) coordinates and indicate that
            # the cropping operation is finished
            #print("lbuttonup")
            self.ref_point.append((x, y))
            #print(self.ref_point)

            # draw a rectangle around the region of interest
            cv2.rectangle(self.image, self.ref_point[0], self.ref_point[1], (0, 255, 0), 2)
            cv2.imshow("image", self.image)

    def initiateMainLoop(self):
        # load the image, clone it, and set up the mouse callback function
        self.image = cv2.imread(self.image_path)
        clone = self.image.copy()
        cv2.namedWindow("image", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("image", self.shape_selection)

        # keep looping until the 'q' key is pressed
        while True:
            cv2.resizeWindow('image', self.image.shape[1], self.image.shape[0])
            # display the image and wait for a keypress
            cv2.imshow("image", self.image)
            key = cv2.waitKey(1) & 0xFF

            # press 'r' to reset the window
            if key == ord("r"):
                print("triggered r")
                self.image = clone.copy()

            # if the 'c' key is pressed, break from the loop
            elif key == ord("c"):
                print("triggered c")
                break

        if len(self.ref_point) == 2:
            crop_img = clone[self.ref_point[0][1]:self.ref_point[1][1], self.ref_point[0][0]:
                                                                        self.ref_point[1][0]]
            cv2.imshow("crop_img", crop_img)
            cv2.waitKey(0)
            # write the image to a directory
            self.writeImageToDirectory(crop_img)

        # close all open windows
        cv2.destroyAllWindows()

    def writeImageToDirectory(self,image):
        import os
        directory_name = "temp_directory"
        # Create the directory
        try:
            os.mkdir(directory_name)
            print("Directory '{}' created successfully.".format(directory_name))
        except FileExistsError:
            print("Directory '{}' already exists.".format(directory_name))
            pass
        except Exception as e:
            print("An error occurred while creating the directory: ", str(e))

        # Check if the image was successfully loaded
        if image is not None:
            # Save the image to the new directory
            save_path = os.path.join(directory_name, self.image_path)
            cv2.imwrite(save_path, image)
            print("Image saved successfully.")
        else:
            print("Failed to load the image.")

    def createAlerts(self):
        import tkinter as tk
        from tkinter import messagebox

        # Create a Tkinter window
        root = tk.Tk()

        # Hide the main window
        root.withdraw()

        # Display the alert message box
        messagebox.showinfo("Alert", "Click on the top-left-most point on the window, drag the cursor to the "
                                     "bottom-right point. If you're ok with the selection, press c. else, press r ")

        # Destroy the Tkinter window
        root.destroy()

if __name__=="__main__":
    path="hdfc.jpg"

    classHandle=userCropTable(path)

