import Motion_Detection
import subprocess
import os

# Checkout 4
# Push 3
# Add 2
# Commit 1
# Push 0

class ObjectHoldingTheValue:
    def __init__(self, initial_value=1000):
        self._value = initial_value
        self._callbacks = []

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        old_value = self._value
        self._value = new_value
        self._notify_observers(old_value, new_value)

    def _notify_observers(self, old_value, new_value):
        for callback in self._callbacks:
            callback(old_value, new_value)

    def register_callback(self, callback):
        self._callbacks.append(callback)

    if(Motion_Detection.Active_Signal == 4):
        subprocess.call("./gitcheckout.sh", shell=True)
        print("Checkout Signal")

    if(Motion_Detection.Active_Signal == 3):
        subprocess.call("./gitpull.sh", shell=True)
        print("Pull Signal")

    if(Motion_Detection.Active_Signal == 2):
        subprocess.call("./gitadd.sh", shell=True)
        print("Add Signal")

    if(Motion_Detection.Active_Signal == 1):
        subprocess.call("./gitcommit.sh", shell=True)
        print("Commit Signal")

    if(Motion_Detection.Active_Signal == 0):
        subprocess.call("./gitpush.sh", shell=True)
        print("Push Signal")


# class Person():
#     def __init__(self):
#         self.wealth = 0
#         global Motion_Detection.Active_Signal
#         # here is where attribute should be
#         # bound to changes in 'global_wealth'
#         self.happiness = bind_to(Motion_Detection.Active_Signal, trigger)

#     def trigger(self, Motion_Detection.Active_Signal):
#         if(Motion_Detection.Active_Signal == 2):
#             subprocess.call("./gitadd.sh", shell=True)

#         if(Motion_Detection.Active_Signal == 1):
#             subprocess.call("./gitcommit.sh", shell=True)

#         if(Motion_Detection.Active_Signal == 0):
#             subprocess.call("./gitpush.sh", shell=True)

#         return
