import threading
import time


class SubtitleManager:

    def __init__(self):
        self.label = None
        self.thinking = False


    def connect(self, label):
        self.label = label


    def set_text(self, text):

        self.thinking = False

        if self.label:
            self.label.after(
                0,
                lambda: self.label.configure(
                    text=text
                )
            )


    def start_thinking(self):

        if self.thinking:
            return

        self.thinking = True

        threading.Thread(
            target=self._thinking_loop,
            daemon=True
        ).start()


    def _thinking_loop(self):

        dots = 1

        while self.thinking:

            text = "Pensando" + "." * dots

            if self.label:
                self.label.after(
                    0,
                    lambda t=text:
                    self.label.configure(
                        text=t
                    )
                )

            dots += 1

            if dots > 3:
                dots = 1

            time.sleep(0.5)


    def stop_thinking(self):

        self.thinking = False


subtitle = SubtitleManager()