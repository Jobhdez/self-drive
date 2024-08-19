import carla
import csv
import time
import os

# Global Variables
image_save_path = 'carla_data'
csv_file_path = os.path.join(image_save_path, 'steering_angles.csv')
image_counter = 0

# Initialize Carla client and world
client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.load_world('Town03')  # Load a town with curves
spawn_points = world.get_map().get_spawn_points()

blueprint_library = world.get_blueprint_library()
vehicle_bp = blueprint_library.filter('model3')[0]
start_point = spawn_points[0]

# Spawn the vehicle in a specific location with more curves
vehicle = world.spawn_actor(vehicle_bp, start_point)

# Setting autopilot for the vehicle
vehicle.set_autopilot(True)

# Open the CSV file outside the callback
if not os.path.exists(image_save_path):
    os.makedirs(image_save_path)

csv_file = open(csv_file_path, mode='w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['image_filename', 'steering_angle'])

# Callback for image saving and steering angle collection
def image_callback(image):
    global image_counter
    # Save image
    image_filename = f'image_{image_counter:06d}.png'
    image.save_to_disk(os.path.join(image_save_path, image_filename))
    
    # Get the vehicle's control for steering angle
    control = vehicle.get_control()
    steering_angle = control.steer
    
    # Save the data to CSV
    csv_writer.writerow([image_filename, steering_angle])
    
    image_counter += 1
    print(f'Saved {image_filename} with steering angle {steering_angle}')

# Add a camera sensor to the vehicle
camera_bp = blueprint_library.find('sensor.camera.rgb')
camera_transform = carla.Transform(carla.Location(x=0.30, y=0, z=1.30), carla.Rotation(pitch=0, yaw=0, roll=0))
camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

# Listen to the camera sensor
camera.listen(image_callback)

# Add a spectator camera to follow the vehicle
spectator = world.get_spectator()
def update_spectator():
    transform = vehicle.get_transform()
    spectator.set_transform(carla.Transform(transform.location + carla.Location(z=50, x=-5), carla.Rotation(pitch=-90)))

try:
    start_time = time.time()
    while time.time() - start_time < 120:  # Collect data for 120 seconds
        world.wait_for_tick()
        update_spectator()

finally:
    # Cleanup
    camera.stop()
    csv_file.close()
    vehicle.destroy()

    print(f'Data collection completed and saved to {image_save_path}')
