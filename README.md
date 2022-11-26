# VOCR

VOCR for **V**ideo **O**ptical **C**haracter **R**ecognition.

This module allows you to extract data from an image, a video, or your screen directly.

The module is mainly based on [OpenCV](https://github.com/opencv/opencv-python) and [EasyOCR](https://github.com/JaidedAI/EasyOCR) technologies.

```sh
python3 vocr.py -h
```

```
usage: vocr.py [-h] [-i IFILE] [-v VFILE] -d DFILE [-o OFILE] [-r RFILE]

options:
  -h, --help            show this help message and exit
  -i IFILE, --ifile IFILE
                        path to image file
  -v VFILE, --vfile VFILE
                        path to video file
  -d DFILE, --dfile DFILE
                        path to input data
  -o OFILE, --ofile OFILE
                        path to optionaly output image/video file
  -r RFILE, --rfile RFILE
                        path to optionaly result file
```

---

---

## Before running the script

- Use the `-i` option to scan an image
- Use the `-v` option to scan a video

If none of the options are selected, then the main screen will be used as the video stream.

---

You can specify the `-r` option to define a result file.

If the data comes from the screen as a video stream, then you will **need** to specify this option.

The terminal will be used to display the data in real time.

---

You can specify the `-o` option to define an output file.

If you process an image, the output file will be the same image annotated with the extracted information.

If it is a video or the video stream from a screen, then the output file will be a video including the extracted information.

---

---

## What does the data files look like?

### Input data file

The input data file is a JSON which contains a list of objects with a label, a box and potentially a 'match-pattern' attribute.

```json
[
  {
    "label": "simple-text-recognition",
    "box": [0, 0, 100, 15]
  },
  {
    "label": "bigger-text-recognition",
    "box": [100, 100, 200, 100]
  },
  {
    "label": "try-to-match-patterns",
    "box": [100, 100, 200, 100],
    "match-pattern": {
      "square": "path-to-square-image.png",
      "circle": "path-to-circle-image.png"
    }
  }
]
```

### Output data file

The output data file is another JSON that could look like this:

```json
[
  {
    "id": 1,
    "time": 0.05372333526611328,
    "data": {
      "simple-text-recognition": [],
      "bigger-text-recognition": [
          "Hello World",
          "This is earth"
      ],
      "try-to-match-patterns": [
        "square"
      ]
  },
  {
    "id": 2,
    "time": 0.25372333526611328,
    "data": {
      "simple-text-recognition": [
        "Hi"
      ],
      "bigger-text-recognition": [
          "The sentence changed"
      ],
      "try-to-match-patterns": [
        "circle"
      ]
  }
]
```

---

---

## Questions

### How to extract from an image?

#### To show informations directly in the terminal :

```sh
python3 vocr.py -i <path-to-image> -d data.json
```

#### To save informations in a file :

```sh
python3 vocr.py -i <path-to-image> -d data.json -r result.json
```

#### To save a picture of the annoted image :

```sh
python3 vocr.py -i <path-to-image> -d data.json -o output.png
```

#### To do everything :

```sh
python3 vocr.py -i <path-to-image> -d data.json -o output.png -r result.json
```

---

### How to extract from a video?

#### Without output annoted video :

```sh
python3 vocr.py -v <path-to-video> -d data.json -r result.json
```

Here, the frame progression will be shown in the terminal :

```
Frame 100/200 (50%)
```

#### With output annoted video :

```sh
python3 vocr.py -v <path-to-video> -d data.json -r result.json -o output.avi
```

---

### How to extract from my screen?

#### Without output annoted video :

```sh
python3 vocr.py -d data.json -r result.json
```

Here the data will be shown on the terminal, depending on what you have included in the data file.

#### With output annoted video :

```sh
python3 vocr.py -v <path-to-video> -d data.json -r result.json -o output.avi
```
