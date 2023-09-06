import RPi.GPIO as GPIO
import subprocess
import cv2
from tensorflow.keras.models import load_model
import time
import numpy as np

TRIG_PIN = 18  # GPIO pin for trigger
ECHO_PIN = 24  # GPIO pin for echo
#PROXIMITY_PIN = 25  # GPIO pin for proximity sensor
SERVO_A_PIN = 27
SERVO_B_PIN = 13
SERVO_C_PIN = 17  # GPIO pin for servo C
SERVO_D_PIN = 4  # GPIO pin for servo C
#pin_webcam = 0

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SERVO_A_PIN, GPIO.OUT)
    GPIO.setup(SERVO_B_PIN, GPIO.OUT)
    GPIO.setup(SERVO_C_PIN, GPIO.OUT)
    GPIO.setup(SERVO_D_PIN, GPIO.OUT)
#    GPIO.setup(PROXIMITY_PIN, GPIO.IN)

def move_servo_c(angle):
    pwm_servo_c = GPIO.PWM(SERVO_C_PIN, 50)  # 50 Hz frequency
    pwm_servo_c.start(0) #1
    duty_cycle = angle / 18 + 2  # Convert angle to duty cycle
    pwm_servo_c.ChangeDutyCycle(duty_cycle)
    time.sleep(1)  # Adjust the delay as needed
    pwm_servo_c.stop()

def move_servo_a(angle):
    pwm_servo_a = GPIO.PWM(SERVO_A_PIN, 50)  # 50 Hz frequency
    pwm_servo_a.start(50)
    duty_cycle = angle / 18 + 2  # Convert angle to duty cycle
    pwm_servo_a.ChangeDutyCycle(duty_cycle)
    time.sleep(1)  # Adjust the delay as needed
    pwm_servo_a.stop()

def move_servo_b(angle):
    pwm_servo_b = GPIO.PWM(SERVO_B_PIN, 50)  # 50 Hz frequency
    pwm_servo_b.start(100)
    duty_cycle = angle / 18 + 2  # Convert angle to duty cycle
    pwm_servo_b.ChangeDutyCycle(duty_cycle)
    time.sleep(1)  # Adjust the delay as needed
    pwm_servo_b.stop()

def move_servo_d(angle):
    pwm_servo_d = GPIO.PWM(SERVO_D_PIN, 50)  # 50 Hz frequency
    pwm_servo_d.start(0)
    duty_cycle = angle / 18 + 2  # Convert angle to duty cycle
    pwm_servo_d.ChangeDutyCycle(duty_cycle)
    time.sleep(1)  # Adjust the delay as needed
    pwm_servo_d.stop()

def read_distance():
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    pulse_start = time.time()
    pulse_end = time.time()

    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

#def read_proximity():
 #   proximity_status = GPIO.input(PROXIMITY_PIN)
  #  return proximity_status

# ... (other functions)

def classify_image(image, model):
    resized_image = cv2.resize(image, (224, 224))
    normalized_frame = resized_image / 255.0
    input_frame = normalized_frame.reshape((1, 224, 224, 3))

    predictions = model.predict(input_frame)
    predicted_class_index = np.argmax(predictions)
    label_names = ["Recyclable", "Organic"]
    predicted_class = label_names[predicted_class_index]

    return predicted_class

def capture_and_classify_image(webcam, model):  # 0 adalah indeks kamera default
    file_gambar = "gambar.jpg"  # Nama file untuk gambar

    ret, frame = webcam.read()
    if ret:
        cv2.imwrite(file_gambar, frame)
        print(f"Gambar diambil dan disimpan sebagai {file_gambar}")
    else:
        print("Error saat mengambil gambar")

    webcam.release()
    cv2.destroyAllWindows()

    image = cv2.imread(file_gambar)
    predicted_class = classify_image(image, model)
    return predicted_class
# ... (fungsi lainnya)

def main():
    setup_gpio()
    loaded_model = load_model('/home/admin/trash/waste_classification_model (1).h5')

    try:
        while True:
            distance = read_distance()
            print(f"Distance: {distance} cm")

            if distance < 10:  # Sesuaikan ambang batas sesuai kebutuhan
                print("Object detected by ultrasonic. Moving servo C...")
                move_servo_c(90)  # Pindahkan servo C ke 90 derajat
                time.sleep(3)  # Tunda 3 detik
                move_servo_c(0)  # Pindahkan servo C ke 0 derajat
                print("Servo C closed.")
              #  proximity_status = read_proximity()
               # if proximity_status == 0:
                #    print(proximity_status)
                cam = cv2.VideoCapture(0)
                hasil = capture_and_classify_image(cam,loaded_model)
                    
                if hasil == "Recyclable":
                    move_servo_b(0)  #b0
                    move_servo_a(100)  # Pindahkan servo C ke 90 derajat
                    time.sleep(3)  # Tunda 3 detik
                    move_servo_a(50)
                    move_servo_b(100) #b100
                else:
                    move_servo_d(90)
                    move_servo_a(0)  # Pindahkan servo C ke 90 derajat
                    time.sleep(3)  # Tunda 3 detik
                    move_servo_a(50)
                    move_servo_d(0)
                print(hasil)
            time.sleep(0.1)
    except KeyboardInterrupt:
        GPIO.cleanup()
if __name__ == "__main__":
   main()
