import pyrealsense2 as rs
import numpy as np
import cv2
import os
import time

# Constants
EXPOSURE_VALUE = 15000  # Set desired exposure value

# Create a folder to store images   
save_folder = "/home/parth/snaak/snaak_data/data_collection"
os.makedirs(save_folder, exist_ok=True)

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Set RGB camera resolution
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)

# Get the color sensor for setting exposure
color_sensor = pipeline.get_active_profile().get_device().query_sensors()[0]

# Set exposure
color_sensor.set_option(rs.option.exposure, EXPOSURE_VALUE)

print("Press 's' to save an image. Press 'q' to exit.")

try:
    while True:
        # Wait for a frame
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()

        if not color_frame:
            continue

        # Convert to NumPy array
        color_image = np.asanyarray(color_frame.get_data())

        # Display the image
        cv2.imshow("RealSense RGB", color_image)

        # Wait for key press
        key = cv2.waitKey(1) & 0xFF
        if key == ord("s"):  # Press 's' to save image
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            image_path = os.path.join(save_folder, f"image_{timestamp}.png")
            cv2.imwrite(image_path, color_image)
            print(f"Saved: {image_path}")
        elif key == ord("q"):  # Press 'q' to quit
            break

finally:
    # Stop streaming
    pipeline.stop()
    cv2.destroyAllWindows()
