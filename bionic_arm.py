from components import Report, Servo, Hand
import time

class Robot:
    def __init__(self):
        report = Report()
        self.servo = Servo(report)

        config = {
            'report': report,
            'servo': self.servo,
        }

        self.hand = Hand(config)


    def sleep(self):
        # self.hand.close()
        self.servo.move_servo_to_percent(self.hand.channels['thumb'], 50)
        self.servo.move_servo_to_percent(self.hand.channels['index'], 50)
        self.servo.move_servo_to_percent(self.hand.channels['middle'], 50)
        self.servo.move_servo_to_percent(self.hand.channels['ring'], 50)
        self.servo.move_servo_to_percent(self.hand.channels['little'], 0)
        for i in range(5):
            self.servo.sleep(i)
            time.sleep(1)


# invoke a new robot
robot = Robot()

# open the hand
#robot.hand.close()

robot.sleep()

# close the hand
#robot.hand.open()
