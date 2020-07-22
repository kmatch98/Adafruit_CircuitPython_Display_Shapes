# class of sparklines in CircuitPython
# created by Kevin Matocha - Copyright 2020 (C)

# See the bottom for a code example using the `sparkline` Class.

# # File: display_shapes_sparkline.py
# A sparkline is a scrolling line graph, where any values added to sparkline using `add_value` are plotted.
#
# The `sparkline` class creates an element suitable for adding to the display using `display.show(mySparkline)`
# or adding to a `displayio.Group` to be displayed.
#
# When creating the sparkline, identify the number of `max_items` that will be included in the graph.
# When additional elements are added to the sparkline and the number of items has exceeded max_items,
# any excess values are removed from the left of the graph, and new values are added to the right.


# The following is an example that shows the

# setup display
# instance sparklines
# add to the display
# Loop the following steps:
# 	add new values to sparkline `add_value`
# 	update the sparklines `update`

import board
import displayio
import terminalio
import random
import time
from adafruit_display_shapes.sparkline import Sparkline
from adafruit_ili9341 import ILI9341
from adafruit_display_text import label

import gc

if "DISPLAY" not in dir(board):
    # Setup the LCD display with driver
    # You may need to change this to match the display driver for the chipset
    # used on your display
    from adafruit_ili9341 import ILI9341

    displayio.release_displays()

    # setup the SPI bus
    spi = board.SPI()
    tft_cs = board.D9  # arbitrary, pin not used
    tft_dc = board.D10
    tft_backlight = board.D12
    tft_reset = board.D11

    while not spi.try_lock():
        spi.configure(baudrate=32000000)
        pass
    spi.unlock()

    display_bus = displayio.FourWire(
        spi,
        command=tft_dc,
        chip_select=tft_cs,
        reset=tft_reset,
        baudrate=32000000,
        polarity=1,
        phase=1,
    )

    print("spi.frequency: {}".format(spi.frequency))

    # Number of pixels in the display
    DISPLAY_WIDTH = 320
    DISPLAY_HEIGHT = 240

    # create the display
    display = ILI9341(
        display_bus,
        width=DISPLAY_WIDTH,
        height=DISPLAY_HEIGHT,
        rotation=180, # The rotation can be adjusted to match your configuration.
        auto_refresh=True,
        native_frames_per_second=90,
    )

    # reset the display to show nothing.
    display.show(None)
else:
    # built-in display
    display = board.DISPLAY

##########################################
# Create background bitmaps and sparklines
##########################################

# Baseline size of the sparkline chart, in pixels.
chartWidth = 50
chartHeight = 50

font = terminalio.FONT

# Setup the first bitmap and sparkline
# This sparkline has no background bitmap
# mySparkline1 uses a vertical y range between -1 to +1.25 and will contain a maximum of 40 items
mySparkline1 = Sparkline(
    width=chartWidth, height=chartHeight, max_items=40, yMin=-1, yMax=1.25, x=10, y=10
)

# Label the y-axis range
textLabel1a = label.Label(
    font=font, text=str(mySparkline1.yTop), color=0xFFFFFF
)  # yTop label
textLabel1a.anchor_point = (0, 0.5)  # set the anchorpoint
textLabel1a.anchored_position = (
    10 + chartWidth,
    10,
)  # set the text anchored position to the upper right of the graph

textLabel1b = label.Label(
    font=font, text=str(mySparkline1.yBottom), color=0xFFFFFF
)  # yTop label
textLabel1b.anchor_point = (0, 0.5)  # set the anchorpoint
textLabel1b.anchored_position = (
    10 + chartWidth,
    10 + chartHeight,
)  # set the text anchored position to the upper right of the graph


# Setup the second bitmap and sparkline
# mySparkline2 uses a vertical y range between 0 to 1, and will contain a maximum of 10 items
#
palette2 = displayio.Palette(1)  # color palette used for bitmap2 (one color)
palette2[0] = 0x0000FF

bitmap2 = displayio.Bitmap(chartWidth * 2, chartHeight * 2, 1)  # create bitmap2
tileGrid2 = displayio.TileGrid(
    bitmap2, pixel_shader=palette2, x=150, y=10
)  # Add bitmap2 to tilegrid2
mySparkline2 = Sparkline(
    width=chartWidth * 2,
    height=chartHeight * 2,
    max_items=10,
    yMin=0,
    yMax=1,
    x=150,
    y=10,
    color=0xFF00FF,
)


# Setup the third bitmap and third sparkline
# mySparkline3 contains a maximum of 10 items
# since yMin and yMax are not specified, mySparkline3 uses autoranging for both the top and bottom of the y-axis.
# Note1: Any unspecified edge limit (yMin or yMax) will autorange that edge based on the data in the list.
# Note2: You can read back the value of the y-axis limits by using mySparkline3.yBottom or mySparkline3.yTop


palette3 = displayio.Palette(1)  # color palette used for bitmap (one color)
palette3[0] = 0x11FF44
bitmap3 = displayio.Bitmap(DISPLAY_WIDTH - 30, chartHeight * 2, 1)  # create bitmap3
tileGrid3 = displayio.TileGrid(
    bitmap3, pixel_shader=palette3, x=0, y=120
)  # Add bitmap3 to tilegrid3

mySparkline3 = Sparkline(
    width=DISPLAY_WIDTH - 30,
    height=chartHeight * 2,
    max_items=10,
    x=0,
    y=120,
    color=0xFFFFFF,
)

# Initialize the y-axis labels for mySparkline3 with no text
textLabel3a = label.Label(
    font=font, text="", color=0x11FF44, max_glyphs=20
)  # yTop label
textLabel3a.anchor_point = (0, 0.5)  # set the anchorpoint
textLabel3a.anchored_position = (
    mySparkline3.width,
    120,
)  # set the text anchored position to the upper right of the graph

textLabel3b = label.Label(
    font=font, text="", color=0x11FF44, max_glyphs=20
)  # yTop label
textLabel3b.anchor_point = (0, 0.5)  # set the anchorpoint
textLabel3b.anchored_position = (
    mySparkline3.width,
    120 + mySparkline3.height,
)  # set the text anchored position to the upper right of the graph


# Create a group to hold the three bitmap TileGrids and the three sparklines and
# append them into the group (myGroup)
#
# Note: In cases where display elements will overlap, then the order the elements are added to the
# group will set which is on top.  Latter elements are displayed on top of former elemtns.
myGroup = displayio.Group(max_size=20)

myGroup.append(mySparkline1)
myGroup.append(textLabel1a)
myGroup.append(textLabel1b)

myGroup.append(tileGrid2)
myGroup.append(mySparkline2)

myGroup.append(tileGrid3)
myGroup.append(mySparkline3)
myGroup.append(textLabel3a)
myGroup.append(textLabel3b)

# Set the display to show myGroup that contains all the bitmap TileGrids and sparklines
display.show(myGroup)

i = 0  # This is a counter for changing the random values for mySparkline3

# Start the main loop
while True:

    # Turn off auto_refresh to prevent partial updates of the screen during updates
    # of the sparklines
    display.auto_refresh = False

    # add_value: add a new value to a sparkline
    # Note: The y-range for mySparkline1 is set to -1 to 1.25, so all these random
    # values (between 0 and 1) will fit within the visible range of this sparkline
    mySparkline1.add_value(random.uniform(0, 1))

    # Note: For mySparkline2, the y-axis range is set from 0 to 1.
    # With the random values set between -1 and +2, the values will sometimes
    # be out of the y-range.  This example shows how the fixed y-range (0 to 1)
    # will "clip" values (it will not display them) that are above or below the y-range.
    mySparkline2.add_value(random.uniform(-1, 2))

    # mySparkline3 is set autoranging for the top and bottom of the Y-axis

    # In this example, for 15 values, this adds points in the range from 0 to 1.
    # Then, for the next 15 values, it adds points in the range of 0 to 10.
    # This is to highlight the autoranging of the y-axis.
    # Notice how the y-axis labels show that the y-scale is changing.
    #
    # An exercise for the reader: You can set only one or the other sparkline axis
    # to autoranging by setting its value to None.
    if i < 15:
        mySparkline3.add_value(random.uniform(0, 1))
    else:
        mySparkline3.add_value(random.uniform(0, 10))
    textLabel3a.text = str(mySparkline3.yTop)
    textLabel3b.text = str(mySparkline3.yBottom)
    i += 1  # increment the counter
    if i > 30:  # After 30 times through the loop, reset the counter
        i = 0

    # Turn on auto_refresh for the display
    display.auto_refresh = True

    # The display seems to be less jittery if a small sleep time is provided
    # You can adjust this to see if it has any effect
    time.sleep(0.01)

    # Uncomment the next line to print the amount of available memory
    # print('memory free: {}'.format(gc.mem_free()))
