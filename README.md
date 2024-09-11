# Macroblock Matching Motion Visualization

This repository contains a Python script that processes video files to detect and visualize motion vectors using block-matching algorithms. The script analyzes each frame of a video, compares blocks between consecutive frames, and draws arrows to represent motion. The processed frames are then compiled into a new video.

## Features

- Extracts frames from a video.
- Compares blocks of pixels between consecutive frames.
- Draws arrows to indicate motion between blocks.
- Saves processed frames and compiles them into a new video.

## Dependencies

The script requires the following Python packages:

- `numpy`
- `opencv-python`

You can install the required packages using `pip`:

```bash
pip install numpy opencv-python
```

## Usages

### File Setup
- Place your video file in the `SourceVideo` folder.
- Ensure the `VideoFrames` and `OutputFrames` directories exist or create them.

### Script Setup
- Change the variables `video_name` and `output_video_name` to match the input video name [**WITH EXTENSION**] and desired output name

## Parameters
- `block_radius = 2`
- `pixel_search_radius = 35`
- `Tmin = 400`
- `Tmax = 1000`

The above parameters can be tweaked to provide more optimal results based on your input video resolution and noise levels.

## Demonstration
<p align="center">
  <img src="/DemoMedia/MacroblockMatch.gif" alt="Demo" />
</p>
