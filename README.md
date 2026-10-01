# mcap-rich

[![PyPI version](https://badge.fury.io/py/mcap-rich-cli.svg)](https://badge.fury.io/py/mcap-rich-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A clean, visual wrapper for the official Foxglove `mcap` CLI tool. It adds a real-time progress bar, transfer speed metrics, and ETA estimations to your terminal operations using the `rich` Python library.

## Why this exists

When working with heavy ROS 2 data—such as high-resolution point clouds, 4D imaging radar logs, or multi-camera setups from autonomous vehicle testing—merging and filtering `.mcap` bags can take a significant amount of time. 

The native `mcap` CLI tool is incredibly fast, but it runs silently. This wrapper solves the "blank terminal anxiety" by estimating the maximum theoretical output size and providing a beautiful UI to track the I/O progress, without altering the underlying tool's behavior.

<p align="center">
  <!-- TODO: Replace the link below with an actual screenshot or GIF of your terminal -->
  <img src="https://via.placeholder.com/800x150.png?text=Add+a+GIF+of+the+progress+bar+here!" alt="mcap-rich demo">
</p>

## Installation

Install the wrapper globally via PyPI:

```bash
pip install mcap-rich-cli
