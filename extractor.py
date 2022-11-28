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


# Convert dat to string
def data_to_string(data):
    if data is None:
        return ''
    if isinstance(data, list):
        return ' or '.join(data)
    return data


# Draw data on image with its rectangle
def draw_data_on_image(image, coordinates, data):
    text = data_to_string(data)

    color = (0, 255, 0) if text != '' else (0, 0, 255)
    font = cv2.FONT_HERSHEY_SIMPLEX
    x, y, w, h = coordinates.get('box')
    cv2.rectangle(image, (x, y), (x+w, y+h), color, 2)

    if text != '':
        cv2.putText(image, text, (x, y-10), font, 0.7, color, 2)

    return image


# Check if new data is the same as previous data
def is_data_different(previous_data, new_data):
    for key, value in new_data.items():
        if previous_data.get(key) != value:
            return True
    return False


# Return result of pattern matching
def get_pattern_match(cropped, pattern):
    template = cv2.imread(pattern, 0)
    res = cv2.matchTemplate(cropped, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8

    arr1, arr2 = np.where(res >= threshold)
    return len(arr1) + len(arr2)


# Return the most similar pattern if corresponding pattern found
def find_pattern(cropped, patterns):
    cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    best_pattern = None
    best_pattern_match = None
    for key, pattern in patterns.items():
        if not os.path.exists(pattern):
            print(f'File {pattern} does not exist')
            sys.exit()

        current_pattern_match = get_pattern_match(cropped, pattern)

        # if no similarity found, continue
        if current_pattern_match == 0:
            continue

        if best_pattern is None or current_pattern_match > best_pattern_match:
            best_pattern = key
            best_pattern_match = current_pattern_match

    return best_pattern


# Extract patterns or texts from the list of subimages composing the image
def extract_information_from_image(reader, image_array, subimages_coordinates):
    if image_array is None:
        return {}
    result = {}
    for coordinates in subimages_coordinates:
        x, y, w, h = coordinates.get('box')
        patterns = coordinates.get('match-pattern')
        cropped = image_array[y:y+h, x:x+w]

        # if patterns are defined, try to find the most similar pattern
        if patterns:
            result[coordinates.get('label')] = find_pattern(cropped, patterns)
        # else, use the reader to extract data
        else:
            result[coordinates.get('label')] = reader.readtext(
                cropped, detail=0)

    return result


# Extract data from image
def from_image(reader, ifile, subimages_coordinates, ofile):
    img = PIL.Image.open(ifile)
    image_array = np.array(img)

    data = extract_information_from_image(
        reader, image_array, subimages_coordinates)

    # save a copy of the image with data on it
    if ofile is not None:
        image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        for coordinates in subimages_coordinates:
            subdata = data.get(coordinates.get('label'))
            image_array = draw_data_on_image(image_array, coordinates, subdata)

        cv2.imwrite(ofile, image_array)

    return {
        "id": 1,
        "time": 0,
        "data": data
    }


# Print additional informations in terminal while processing video
def print_processing_infos_in_terminal(is_stream, data, current_frame, total_frames):
    if not sys.stdout.isatty():
        return

    # if streaming, print the current data
    if is_stream:
        # clear terminal
        os.system('cls' if os.name == 'nt' else 'clear')

        # print values
        for key, value in data.get('data').items():
            value = data_to_string(value)
            print(f'{key} : {value}')

    # if not streaming, print the processing progression
    else:
        print(
            f"Frame {current_frame}/{total_frames} ({current_frame/total_frames*100:.2f}%)", end="\r")


# Extract data from video or stream
def from_video_or_stream(reader, subimages_coordinates, vfile=None, ofile=None, callback=None):
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
        out = cv2.VideoWriter(ofile, fourcc,
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
                current_frame = int(video.get(cv2.CAP_PROP_POS_FRAMES))
                # fix video.isOpened() false positive
                if (current_frame == total_frames):
                    break

            # image processing
            if counter % 10 == 0:
                data = {
                    "id": id_image,
                    "time": time.time() - initial_time,
                    "data": extract_information_from_image(reader, frame, subimages_coordinates)
                }

                # if not stream, print processing infos every 10 frames
                if not is_stream:
                    print_processing_infos_in_terminal(
                        is_stream, data, current_frame, total_frames)

                # if data is different from previous data
                if current_data is None or is_data_different(current_data, data.get('data')):
                    result.append(data)

                    # if stream and callback is defined, call it, else print new data
                    if is_stream and callback is not None:
                        callback(data)
                    elif is_stream:
                        print_processing_infos_in_terminal(
                            is_stream, data, current_frame, total_frames)

                    current_data = data.get('data')
                    id_image += 1

                # if the data is different from the previous one

            counter += 1

            # save a copy of the image with data on it
            if out is not None:
                for coordinates in subimages_coordinates:
                    subdata = current_data.get(coordinates.get('label'))
                    text = data_to_string(subdata)
                    frame = draw_data_on_image(frame, coordinates, text)

                out.write(frame)

        except KeyboardInterrupt:
            break

    if out is not None:
        out.release()

    # close any open windows
    cv2.destroyAllWindows()

    return result


# Extract data from video
def from_video(reader, vfile, subimages_coordinates, ofile):
    return from_video_or_stream(reader, subimages_coordinates, vfile=vfile, ofile=ofile)


# Extract data from stream
def from_stream(reader, subimages_coordinates, ofile, callback):
    return from_video_or_stream(reader, subimages_coordinates, ofile=ofile, callback=callback)
