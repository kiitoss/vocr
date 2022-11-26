import argparse
import os
import sys
import json
import easyocr
import text_extractor


def error(error):
    print(f'Error - {error}')
    sys.exit()


def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ifile", type=str,
                    help="path to image file")
    ap.add_argument("-v", "--vfile", type=str,
                    help="path to video file")
    ap.add_argument("-d", "--dfile", required=True, type=str,
                    help="path to input data")
    ap.add_argument("-o", "--ofile", type=str,
                    help="path to optionaly output image/video file")
    return vars(ap.parse_args())


def get_reader():
    # needs to run only once to load the model into memory
    return easyocr.Reader(['en'])


def check_file(filepath, endswith=[]):
    if not os.path.exists(filepath):
        error(f'File {filepath} does not exist')

    end_valid = False
    for end in endswith:
        if filepath.endswith(end):
            end_valid = True
            break

    if not end_valid:
        error(f'File {filepath} does not end with {endswith}')


def get_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)


def main():
    args = get_args()

    ifile = args.get("ifile")
    vfile = args.get("vfile")
    dfile = args.get("dfile")
    ofile = args.get("ofile")

    if ifile is not None and vfile is not None:
        error("Only one file can be specified")

    if ifile is not None:
        check_file(ifile, ['.jpg', '.jpeg', '.png'])
    if vfile is not None:
        check_file(vfile, ['.mp4', '.mkv'])

    check_file(dfile, ['.json'])

    subimages_coordinates = get_data(dfile)

    reader = get_reader()

    result = {}
    if ifile is not None:
        result = text_extractor.from_image(
            reader, ifile, subimages_coordinates, ofile)
    elif vfile is not None:
        result = text_extractor.from_video(
            reader, vfile, subimages_coordinates, ofile)
    else:
        result = text_extractor.from_stream(
            reader, subimages_coordinates, ofile)

    print(json.dumps(result, indent=4))


if __name__ == '__main__':
    main()
