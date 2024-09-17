import cv2
import time
import os

# Folder
folder = "frames"

# Create the frames folder if it doesn't exist
frames_dir = os.path.join(os.getcwd(), folder)
os.makedirs(frames_dir, exist_ok=True)

# Initialize the video capture
cap = cv2.VideoCapture(0)  # Use 0 for webcam, or specify a video file path

# Wait for the camera to initialize and adjust light levels
time.sleep(2)

while True:
    ret, frame = cap.read()
    if ret:
        # Display the frame
        cv2.imshow("Video Preview", frame)

        # Save the frame as an image file
        path = f"{folder}/frame.jpg"
        cv2.imwrite(path, frame)
        print("Saved current frame")
    else:
        print("Failed to capture image")
        break

    # Check if the user pressed the 'q' key
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()