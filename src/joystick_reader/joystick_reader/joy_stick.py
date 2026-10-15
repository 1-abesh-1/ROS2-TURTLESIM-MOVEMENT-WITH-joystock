import rclpy
from sensor_msgs.msg import Joy
from turtlesim.srv import Spawn, Kill
from geometry_msgs.msg import Twist
import time
axes_values = []
button_values = [0, 0, 0, 0, 0, 0]
count = 1
c = 1
spawn_client = None
kill_client = None
cmd_pub = None
node = None

def joy_callback(msg):
    global axes_values, button_values, count, c, spawn_client, kill_client, cmd_pub, node
    axes_values = list(msg.axes)
    button_values = list(msg.buttons)
    
    # Spawn a new turtle (Button 5)
    if button_values[5] == 1:
        req = Spawn.Request()
        req.x = 5.0
        req.y = 5.0
        req.theta = 0.0
        req.name = 'turtle' + str(count + 1)
        spawn_client.call_async(req)
        count += 1
        time.sleep(2.0)

    # Kill the currently selected turtle (Button 2)
    if button_values[2] == 1:
        req = Kill.Request()
        req.name = 'turtle' + str(c)
        kill_client.call_async(req)
        
        # Fall back safely (never drop below turtle1)
        if c > 1:
            c -= 1
            
        cmd_pub = node.create_publisher(Twist, '/turtle' + str(c) + '/cmd_vel', 10)

    # Switch active turtle up (Button 4)
    if button_values[4] == 1 and c < count:
        c += 1
        cmd_pub = node.create_publisher(Twist, '/turtle' + str(c) + '/cmd_vel', 10)
        
    # Switch active turtle down (Button 3)
    if button_values[3] == 1 and c > 1:
        c -= 1
        cmd_pub = node.create_publisher(Twist, '/turtle' + str(c) + '/cmd_vel', 10)

    # Drive the currently active turtle
    twist = Twist()
    twist.linear.x = (-1 * axes_values[3] * 2.0)
    twist.angular.z = (axes_values[0] * 2.0)
    cmd_pub.publish(twist)

def main():
    global spawn_client, kill_client, cmd_pub, node
    rclpy.init()
    node = rclpy.create_node('joy_reader')
    node.create_subscription(Joy, '/joy', joy_callback, 10)
    
    spawn_client = node.create_client(Spawn, '/spawn')
    kill_client = node.create_client(Kill, '/kill')
    
    cmd_pub = node.create_publisher(Twist, '/turtle1/cmd_vel', 10)

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()