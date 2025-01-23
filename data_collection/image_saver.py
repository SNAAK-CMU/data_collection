import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge
import os
import time
import sys
import termios
import tty
import select
import threading

class ImageSaverNode(Node):
    def __init__(self):
        super().__init__('image_saver_node')

        # Declare parameters
        self.declare_parameter('save_directory', '/home/cliche/data_collection_images')

        # Get the values of the parameters
        self.save_directory = self.get_parameter('save_directory').get_parameter_value().string_value
        
        # Create subscribers
        self.subscription = self.create_subscription(
            Image,
            '/camera/camera/color/image_rect_raw',  # Adjust topic name based on your setup
            self.image_callback,
            10
        )
        
        self.bridge = CvBridge()
        self.image_count = 0
        
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

        self.save_dir_jpg = self.save_directory + "/jpg_images"
        self.save_dir_png = self.save_directory + "/png_images"
        if not os.path.exists(self.save_dir_jpg):
            os.makedirs(self.save_dir_jpg)
        if not os.path.exists(self.save_dir_png):
            os.makedirs(self.save_dir_png)

        
        self.get_logger().info('ImageSaverNode initialized. Press any key to save an image.')
        
        # Start a thread to listen for user input
        self.input_thread = threading.Thread(target=self.wait_for_keypress)
        self.input_thread.daemon = True
        self.input_thread.start()

    def image_callback(self, msg: Image):
        # Convert the ROS Image message to an OpenCV image
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"Error converting image: {e}")
            return
        
        self.cv_image = cv_image
    
    def wait_for_keypress(self):
        while rclpy.ok():
            if self.kbhit():
                key = self.getch()
                if key:
                    self.save_image()

    def kbhit(self):
        """
        Check if a key has been pressed.
        Returns: True if a key has been pressed, False otherwise.
        """
        return select.select([sys.stdin], [], [], 0.0)[0]

    def getch(self):
        """
        Get a single character from the keyboard.
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def save_image(self):
        if hasattr(self, 'cv_image'):
            # Save jpg image
            filename = os.path.join(self.save_dir_jpg, f"image_{self.image_count:04d}.jpg")
            cv2.imwrite(filename, self.cv_image)

            # Save png image
            filename = os.path.join(self.save_dir_png, f"image_{self.image_count:04d}.png")
            cv2.imwrite(filename, self.cv_image)

            self.get_logger().info(f"Saved image {filename}")
            self.image_count += 1
        else:
            self.get_logger().warn("No image received yet, please wait.")
    
def main(args=None):
    rclpy.init(args=args)
    
    node = ImageSaverNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
