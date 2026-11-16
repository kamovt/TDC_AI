import os
import tempfile

from mss import mss

from brain_tools import describe_screen


def analyze_screen():

    with tempfile.NamedTemporaryFile(
        suffix=".png",
        delete=False
    ) as temp:

        image_path = temp.name

    try:

        with mss() as sct:
            try:
                sct.shot(
                    mon=2,
                    output=image_path
                )

            except Exception:
                sct.shot(
                    mon=1,
                    output=image_path
                )

        return describe_screen(image_path)

    finally:

        if os.path.exists(image_path):
            os.remove(image_path)


if __name__ == "__main__":

    print(analyze_screen())