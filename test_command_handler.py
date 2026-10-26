
from src.command_handler import CommandHandler


class FakeController:
    def __init__(self):
        self.actions = []

    def play(self):
        self.actions.append("play")
        return "Playing"

    def resume(self):
        self.actions.append("resume")
        return "Resuming"

    def pause(self):
        self.actions.append("pause")
        return "Paused"


class FakeFeedback:
    def __init__(self):
        self.messages = []

    def say(self, message):
        self.messages.append(message)
        print(message)


controller = FakeController()
feedback = FakeFeedback()
handler = CommandHandler(controller, feedback)

handler.handle("play the music")
assert controller.actions == ["play"]

handler.handle("hello")
assert controller.actions == ["play"]
assert "Unsupported command" in feedback.messages[-1]

handler.handle("")
assert controller.actions == ["play"]
assert "Unclear command" in feedback.messages[-1]

print("All command-handler tests passed.")
