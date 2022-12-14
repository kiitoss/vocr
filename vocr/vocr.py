import argparse
import os
import sys
import json
import easyocr

try:
    from . import extractor
except:
    import extractor


# Error function
def error(error):
    print(f'Error - {error}')
    sys.exit()


# Get arguments passed to the script
def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--dfile", required=True, type=str,
                    help="path to input data")
    ap.add_argument("-i", "--ifile", type=str,
                    help="path to image file")
    ap.add_argument("-v", "--vfile", type=str,
                    help="path to video file")
    ap.add_argument("-o", "--ofile", type=str,
                    help="path to optionaly output image/video file")
    ap.add_argument("-r", "--rfile", type=str,
                    help="path to optionaly result file")
    return vars(ap.parse_args())


# Check if the file exists
def check_file_exists(filepath):
    if not os.path.exists(filepath):
        error(f'File {filepath} does not exist')


# Check if the file has a valid extension
def check_file_extension(filepath, extensions):
    is_valid = False
    for extension in extensions:
        if filepath.endswith(extension):
            is_valid = True
            break

    if not is_valid:
        error(f'File {filepath} does not end with {extensions}')


# Check if arguments are valid
def check_args(dfile, ifile, vfile, ofile, rfile, from_main):
    if ifile is not None and vfile is not None:
        error("Only one file can be specified")

    if from_main and ifile is None and rfile is None:
        error("You must specify a result file when using a video or a stream")

    check_file_exists(dfile)
    check_file_extension(dfile, ['.json'])

    if ifile is not None:
        check_file_exists(ifile)
        check_file_extension(ifile, ['.jpg', '.jpeg', '.png'])
    if vfile is not None:
        check_file_exists(vfile)
        check_file_extension(vfile, ['.mp4', '.mkv'])
    if ofile is not None:
        if ifile is not None:
            check_file_extension(ofile, ['.jpg', '.jpeg', '.png'])
        elif vfile is not None:
            check_file_extension(ofile, ['.avi'])
    if rfile is not None:
        check_file_extension(rfile, ['.json'])


# Extract the data from the image, the video or the stream
def extract_data(dfile, ifile=None, vfile=None, ofile=None, rfile=None, callback=None, from_main=False):
    check_args(dfile, ifile, vfile, ofile, rfile, from_main)

    with open(dfile, 'r') as f:
        subimages_coordinates = json.load(f)

    # needs to run only once to load the model into memory
    reader = easyocr.Reader(['en'])

    if ifile is not None:
        data = extractor.from_image(
            reader, ifile, subimages_coordinates, ofile)
    elif vfile is not None:
        data = extractor.from_video(
            reader, vfile, subimages_coordinates, ofile, callback)
    else:
        data = extractor.from_stream(
            reader, subimages_coordinates, ofile, callback)

    return data


def main():
    args = get_args()

    dfile = args.get("dfile")
    ifile = args.get("ifile")
    vfile = args.get("vfile")
    ofile = args.get("ofile")
    rfile = args.get("rfile")

    data = extract_data(dfile, ifile, vfile, ofile, rfile, None, True)

    if rfile is not None:
        with open(rfile, 'w') as f:
            json.dump(data, f, indent=4)
    else:
        print(json.dumps(data, indent=4))


if __name__ == '__main__':
    main()
