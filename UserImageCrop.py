# import the necessary packages
import cv2
#import argparse
import os


class userCropTable:

    def __init__(self, image_path):
        self.ref_point = []
        self.image_path = image_path
        self.createAlerts()
        self.output_path = None
        self.column_counter=None
        self.initiateMainLoop()

    def shape_selection(self, event, x, y, flags, param):

        # now let's initialize the list of reference point

        crop = False

        # grab references to the global variables
        # global ref_point, crop

        # if the left mouse button was clicked, record the starting
        # (x, y) coordinates and indicate that cropping is being performed
        if event == cv2.EVENT_LBUTTONDOWN:
            # print("lbuttondown")
            self.ref_point = [(x, y)]
            # print(self.ref_point)

        # check to see if the left mouse button was released
        elif event == cv2.EVENT_LBUTTONUP:
            # record the ending (x, y) coordinates and indicate that
            # the cropping operation is finished
            # print("lbuttonup")
            self.ref_point.append((x, y))
            # print(self.ref_point)

            # draw a rectangle around the region of interest
            cv2.rectangle(self.image, self.ref_point[0], self.ref_point[1], (0, 255, 0), 2)
            cv2.imshow("image", self.image)

    def shape_selection_columns(self, event, x, y, flags, param):

        # now let's initialize the list of reference point

        image = cv2.imread(self.output_path)
        image=self.add_10_percent_padding(image)

        crop = False

        # grab references to the global variables
        # global ref_point, crop

        # if the left mouse button was clicked, record the starting
        # (x, y) coordinates and indicate that cropping is being performed
        if event == cv2.EVENT_LBUTTONDOWN:
            # print("lbuttondown")
            self.ref_point = [(x, y)]
            # print(self.ref_point)

        # check to see if the left mouse button was released
        elif event == cv2.EVENT_LBUTTONUP:
            # record the ending (x, y) coordinates and indicate that
            # the cropping operation is finished
            # print("lbuttonup")
            self.ref_point.append((x, y))
            # print(self.ref_point)

            # draw a rectangle around the region of interest
            cv2.rectangle(image, self.ref_point[0], self.ref_point[1], (0, 255, 0), 2)
            cv2.imshow("column", image)

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

        if len(self.ref_point) == 2:
            self.createAlerts(message=1)
            column_flag=self.getColumns()


    def getColumns(self):

        # The user should have already identified a cropped image. This is a failsafe against that not occurring.
        if self.output_path is None:
            return [False]

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

        full_table_image=cv2.imread(self.output_path)
        full_table_image=self.add_10_percent_padding(full_table_image)

        cv2.namedWindow("selected table", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("selected table", self.shape_selection_columns)

        # int var to keep track of number of columns
        self.column_counter=0

        # keep looping until the 'q' key is pressed
        while True:
            try:
                cv2.resizeWindow("selected table", full_table_image.shape[1], full_table_image.shape[0])
            except cv2.error:
                # A cv2 error will have been caused by the user manually closing the window, leading to the program
                # being unable to detect any window called selected table, and causing a cv2 error. Since the window
                # is non-existent, the loop is broken here
                break
            # display the image and wait for a keypress
            cv2.imshow("selected table", full_table_image)
            key = cv2.waitKey(1) & 0xFF

            # press 'r' to reset the window
            if key == ord("r"):
                print("triggered r")
                self.image = full_table_image.copy()

            # Todo add padding -
            # todo add a way to track closure of cropped image and close the image with rectangles shown
            if key == ord("c"):
                print("triggered c")
                if len(self.ref_point) == 2:
                    self.column_counter+=1
                    crop_img = full_table_image[self.ref_point[0][1]:self.ref_point[1][1], self.ref_point[0][0]:
                                                                                self.ref_point[1][0]]
                    cv2.imshow("crop_img", self.add_10_percent_padding(crop_img))
                    cv2.waitKey(0)
                    # write the image to a directory
                    self.writeImageToDirectory(crop_img,str(self.column_counter))
                #continue

            # if the 'x' key is pressed, break from the loop
            elif key == ord("x"):
                print("triggered x")
                break

        if self.column_counter>0:
            # close all open windows
            cv2.destroyAllWindows()
            return True
        else:
            return False


    def writeImageToDirectory(self, image, col_name=None):

        # todo add checks for backslashes in path name
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

            if col_name is None:

                if "\\" in self.image_path:
                    import re
                    image_name=re.split(r'\\',self.image_path)
                    image_name=image_name[-1]
                else:
                    image_name=self.image_path

                save_path = os.path.join(directory_name, image_name)
                self.output_path = save_path
            else:
                save_path=os.path.join(directory_name, col_name+".jpg")

            # Save the image to the new directory
            cv2.imwrite(save_path, image)

            print("Image saved successfully.")
        else:
            print("Failed to load the image.")

    def add_10_percent_padding(self,image:cv2.Mat):
        image_height = image.shape[0]
        padding = int(image_height * 0.01)
        perspective_corrected_image_with_padding = cv2.copyMakeBorder(image, padding, padding*5, padding, padding, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        return perspective_corrected_image_with_padding


    def createAlerts(self, message=0):
        import tkinter as tk
        from tkinter import messagebox

        # Create a Tkinter window
        root = tk.Tk()

        # Hide the main window
        root.withdraw()

        if message==0:
            # Display the alert message box
            messagebox.showinfo("Alert", "Click on the top-left-most point on the table, drag the cursor to the "
                                         "bottom-right point. If you're ok with the selection, press c. else, press r ")
        elif message==1:
            messagebox.showinfo("Alert", "Click on the top-left-most point on each of the column of the table("
                                         "including the heading), drag the cursor to the"
                                         "bottom-right point. If you're ok with the selection, press c. else, "
                                         "press r.Once all columns have been selected, press r")
        # Destroy the Tkinter window
        root.destroy()


if __name__ == "__main__":
    path = "hdfc.jpg"

    classHandle = userCropTable(path)


