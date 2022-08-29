import keyboard
import time


tests = """
/p
/c
/p eth
/price eth
/p Btc
/p btc
/c eth
/chart
/c btc
/help
/start
/""".split(
    "\n"
)

print("press enter to start")
keyboard.wait("enter")

for test in tests:
    print(test)
    keyboard.write(test)
    time.sleep(1)
    keyboard.press_and_release("enter")
