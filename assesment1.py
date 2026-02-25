from machine import Pin, PWM
import time, random
import neopixel

# setup stuff
pb = Pin(23, Pin.IN, Pin.PULL_UP)
l1 = Pin(18, Pin.OUT)
l2 = Pin(19, Pin.OUT)
buzzer = Pin(25, Pin.OUT)
sensor = Pin(22, Pin.IN, Pin.PULL_UP)
np = neopixel.NeoPixel(Pin(13), 16)
servo = PWM(Pin(5))
servo.freq(50)

# morse 
MORSE_CODE = {
    ".-":"a","-...":"b","-.-.":"c","-..":"d",".":"e",
    "..-.":"f","--.":"g","....":"h","..":"i",".---":"j",
    "-.-":"k",".-..":"l","--":"m","-.":"n","---":"o",
    ".--.":"p","--.-":"q",".-.":"r","...":"s","-":"t",
    "..-":"u","...-":"v",".--":"w","-..-":"x",
    "-.--":"y","--..":"z"
}

# game variables

wordlist = ["cat","dog","rat","fog","fat","fly","try"]
secret = random.choice(wordlist)
progress = ["_"] * len(secret)
mistakes = 0
current_letter_number = 0
game_over = False

# morse timing rules

DOT_DASH_THRESHOLD = 1
LETTER_GAP_TIME = 1.5

# button memory

is_pressed = False
press_start = 0
last_release = time.time()
current_morse = ""

# Game settings
for i in range(0,16):
    np[i] = (0,0,0)
    
print("Aborted 🔥 -- By Shantanu and Avyukt")
print("Who wants to save the child, not me 😈? 3 tries is all you got, better get it right... HAHAHAHA")
print("Here's your word 😏 ", secret)
print("Word:", "".join(progress))

while True:
    
    #Default settings
    
    now = time.time()
    button = pb.value()
    l1.off()
    l2.off()
    servo.duty(110)

    # reset
    
    if sensor.value() == 0:
        secret = random.choice(wordlist)
        progress = ["_"] * len(secret)
        mistakes = 0
        current_letter_number = 0
        current_morse = ""
        game_over = False
        for i in range(16):
            np[i] = (0,0,0)
        np.write()
        print("RESET")
        print("The word is ", secret)
        print("Word:", "".join(progress))
        time.sleep(0.5)
        continue

    # freeze
    
    if game_over:
        continue

    # button press
    if button == 0 and not is_pressed:
        is_pressed = True
        press_start = now
        buzzer.on()

    # dot dash logic
    elif button == 1 and is_pressed:
        is_pressed = False
        buzzer.off()
        press_time = now - press_start
        last_release = now

        if press_time < DOT_DASH_THRESHOLD:
            current_morse += "."
            print(".", end="")
            l1.on()
            l2.off()
        else:
            current_morse += "-"
            print("-", end="")
            l1.on()
            l2.on()

    # long pause for letter done
    if not is_pressed and current_morse != "":
        if now - last_release > LETTER_GAP_TIME:
            letter = MORSE_CODE.get(current_morse, None)
            print(" ->", letter)

            led_start = current_letter_number * 4
            led_end = led_start + 4

            if letter and letter in secret:
                for i in range(len(secret)):
                    if secret[i] == letter:
                        progress[i] = letter
                for i in range(led_start, led_end):
                    np[i] = (0, 50, 0)
            else:
                mistakes += 1
                for i in range(led_start, led_end):
                    np[i] = (50, 0, 0)

            np.write()
            current_letter_number += 1
            current_morse = ""

            print("Word:", "".join(progress))
            print("Mistakes:", mistakes)

            # winning animation
            if "_" not in progress:
                for _ in range(2):
                    for i in range(16):
                        np[i] = (0,50,0)
                    np.write()
                    time.sleep(0.3)
                    for i in range(16):
                        np[i] = (0,0,0)
                    np.write()
                    time.sleep(0.3)

                for i in range(16):
                    np[i] = (0,50,0)
                np.write()
                print("Congrats you successfully saved the child, but can you save another one?")
                print("Try again in 5")
                game_over = True
                time.sleep(4)

            # losing animation
            if mistakes >= 3:
                for _ in range(2):
                    for i in range(16):
                        np[i] = (50,0,0)
                    np.write()
                    time.sleep(0.3)
                    for i in range(16):
                        np[i] = (0,0,0)
                    np.write()
                    servo.duty(35)
                    print("You can reset IN 5 seconds")
                    time.sleep(4)

                print("GAME OVER")
                game_over = True
        