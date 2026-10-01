# mcap-rich

[![PyPI version](https://badge.fury.io/py/mcap-rich-cli.svg)](https://badge.fury.io/py/mcap-rich-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A clean, visual wrapper for the official Foxglove `mcap` CLI tool. It adds a real-time progress bar, transfer speed metrics, and ETA estimations to your terminal operations using the `rich` Python library.

**New in v0.2.0:** You don't even need to install the base `mcap` CLI beforehand. `mcap-rich` will detect your OS and architecture and automatically download the official binary on its first run!

## Why this exists

When working with heavy ROS 2 data—such as high-resolution point clouds, 4D imaging radar logs, or multi-camera setups from autonomous vehicle testing—merging and filtering `.mcap` bags can take a significant amount of time. 

The native `mcap` CLI tool is incredibly fast, but it runs silently. This wrapper solves the "blank terminal anxiety" by estimating the maximum theoretical output size and providing a beautiful UI to track the I/O progress, without altering the underlying tool's behavior.

<p align="center">
  <!-- TODO: Replace the link below with an actual screenshot or GIF of your terminal -->
  <img src="https://via.placeholder.com/800x150.png?text=Add+a+GIF+of+the+progress+bar+here!" alt="mcap-rich demo">
</p>

## Installation

Install the wrapper globally via PyPI:

`pip install mcap-rich-cli`

That's it. If you don't have the official Foxglove `mcap` CLI installed on your system, `mcap-rich` will prompt you to automatically download and configure it the first time you run a command.

## Usage

Simply replace the `mcap` command with `mcap-rich` in your terminal. All native flags and arguments are fully supported and passed through to the underlying tool.

### Merging bags
`mcap-rich merge bag1.mcap bag2.mcap -o merged.mcap`

*Note for ROS 2 users: If you are merging ROS 2 bags, remember to pass the native flag to handle duplicate metadata:*
`mcap-rich merge bag1.mcap bag2.mcap -o merged.mcap --allow-duplicate-metadata`

### Filtering bags
`mcap-rich filter input.mcap -o filtered.mcap --exclude-topic-regex "/tf"`

## Features
* **Zero Configuration & Auto-Install:** Drop-in replacement for the standard CLI. Automatically fetches the Foxglove binary if missing.
* **Smart ETA & Speed:** Real-time calculation of disk write speed and time remaining.
* **Auto-Cleanup:** If the underlying `mcap` process crashes or fails (e.g., due to duplicate metadata errors), `mcap-rich` intercepts the failure and automatically removes the corrupted output file, keeping your workspace clean.

## License

Distributed under the MIT License.
