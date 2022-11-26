import sys
import PIL
import numpy as np
import cv2
import time
from mss import mss
from screeninfo import get_monitors
import os


def convert_frame_mss_to_cv2(frame):
    # https://stackoverflow.com/a/51528497/18342998
    frame = np.flip(frame[:, :, :3], 2)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return frame


def draw_text_on_image(image, coordinates, text):
    color = (0, 255, 0) if text != '' else (0, 0, 255)
    font = cv2.FONT_HERSHEY_SIMPLEX

    x, y, w, h = coordinates.get('box')

    cv2.rectangle(image, (x, y), (x+w, y+h), color, 2)

    if text != '':
        cv2.putText(image, text, (x, y-10), font, 0.7, color, 2)

    return image


def is_different(previous_data, new_data):
    for key, value in new_data.items():
        if previous_data.get(key) != value:
            return True
    return False


def get_text(reader, image_array, subimages_coordinates):
    result = {}
    for coordinates in subimages_coordinates:
        x, y, w, h = coordinates.get('box')
        patterns = coordinates.get('match-pattern')
        cropped = image_array[y:y+h, x:x+w]
        if patterns:
            cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
            best_pattern = None
            best_match = None
            for key, pattern in patterns.items():
                template = cv2.imread(pattern, 0)
                res = cv2.matchTemplate(
                    cropped, template, cv2.TM_CCOEFF_NORMED)
                threshold = 0.8

                arr1, arr2 = np.where(res >= threshold)
                current_match = len(arr1) + len(arr2)
                if best_pattern is None or current_match > best_match:
                    best_pattern = key
                    best_match = current_match
            result[coordinates.get('label')] = [best_pattern]
        else:
            result[coordinates.get('label')] = reader.readtext(
                cropped, detail=0)
    return result


def from_image(reader, ifile, subimages_coordinates, ofile):
    img = PIL.Image.open(ifile)
    image_array = np.array(img)

    data = get_text(reader, image_array, subimages_coordinates)

    if ofile is not None:
        image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        for coordinates in subimages_coordinates:
            texts = data.get(coordinates.get('label'))
            image_array = draw_text_on_image(
                image_array, coordinates, ' or '.join(texts))

        cv2.imwrite(ofile, image_array)

    return {
        "id": 1,
        "time": 0,
        "data": data
    }


def from_video_or_stream(reader, subimages_coordinates, vfile=None, ofile=None):
    is_stream = vfile is None

    result = []
    id_image = 1
    counter = 0
    initial_time = time.time()

    current_data = None

    # instantiate video capture object
    if is_stream:
        screen = get_monitors()[0]
        width = screen.width
        height = screen.height
        sct = mss()
    else:
        video = cv2.VideoCapture(vfile)
        width = int(video.get(3))
        height = int(video.get(4))
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    # instantiate video writer
    out = None
    if ofile is not None:
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter(ofile + '.avi', fourcc,
                              20.0, (width, height), True)

    while is_stream or video.isOpened():
        try:
            # get the frame
            if is_stream:
                box = {'top': 0, 'left': 0, 'width': width, 'height': height}
                frame = np.array(sct.grab(box))
                frame = convert_frame_mss_to_cv2(frame)
            else:
                _, frame = video.read()

            # image processing
            if counter % 10 == 0:
                data = {
                    "id": id_image,
                    "time": time.time() - initial_time,
                    "data": get_text(reader, frame, subimages_coordinates)
                }

                if current_data is None or is_different(current_data, data.get('data')):
                    result.append(data)

                    if sys.stdout.isatty():
                        if is_stream:
                            os.system('cls' if os.name == 'nt' else 'clear')
                            for key, value in data.get('data').items():
                                value = ' or '.join(value)
                                print(f'{key} : {value}')
                        else:
                            current_frame = int(
                                video.get(cv2.CAP_PROP_POS_FRAMES))
                            print(
                                f"Frame {current_frame}/{total_frames} ({current_frame/total_frames*100:.2f}%)", end="\r")

                    current_data = data.get('data')

                    id_image += 1

            counter += 1

            # save image
            if out is not None:
                for coordinates in subimages_coordinates:
                    texts = current_data.get(coordinates.get('label'))
                    frame = draw_text_on_image(
                        frame, coordinates, ' or '.join(texts))

                out.write(frame)

        except KeyboardInterrupt:
            break

    if out is not None:
        out.release()

    # close any open windows
    cv2.destroyAllWindows()

    return result


def from_video(reader, vfile, subimages_coordinates, ofile):
    return from_video_or_stream(reader, subimages_coordinates, vfile=vfile, ofile=ofile)


def from_stream(reader, subimages_coordinates, ofile):
    return from_video_or_stream(reader, subimages_coordinates, ofile=ofile)
