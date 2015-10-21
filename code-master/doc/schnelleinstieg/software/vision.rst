Vision
======

Image format and coordinate systems
-----------------------------------

Our image prozessing uses the YUYV format, which is usually used in
broadcasting because of its compression. Each pixel has its own luma value but
every pixel shares its chrominance with one of its neighbors.

::

    |<----- 4 byte ---->|
    +----+----+----+----+----+--
    | Y1 | Cb | Y2 | Cr | Y3 | 
    +----+----+----+----+----+--
    :                   :
    :                   :
    +----+----+ - -+----+
    | Y1 | Cb |    | Cr |   Pixel 1
    +----+----+- - +----+
    :                   :
     - - +----+----+----+
    |    | Cb | Y2 | Cr |   Pixel 2
     - - +----+----+----+

The image processing uses a discrete pixel representation internally.

Pixel system::

    (0,0)
    X-----------+-----------------------+   
    |           |                       |   +------> x
    |           | y                     |   |
    |           |                       |   |
    |           V                       |   |
    +---------->X                       |   V
    |      x     (x,y)                  |   y         
    |                                   |
    +-----------------------------------+

For the further calculations of the real (global) position of the objects found
in the image processing the coordinates are converted into another coordinate
system.

Relative system

::

    +-----------------------------------+   
    |   (x,y) X<-----+                  |           y
    |         ^      | y                |      (z)  ^
    |         |      |                  |        \  |
    |         +------X                  |         \ |
    |            x    (0,0)             |          \|
    |                                   |   x<------+
    |                                   |
    +-----------------------------------+

The position in the latter system is normalized over the width of the image. The
resulting maximum x value is 0.5 and the minimum value is -0.5. The boundary
values for y are dependent on the aspect ratio of the image. (The z axis points
implicitly into the image. This axis will be used to calculate the distance of
objects later in the process.)

Results of processing
---------------------

The vision provides the following information to the behaviour:

BallInfo
~~~~~~~~
The BallInfo consists of the position, radius and rating of the found ball 
candidate. The coordinates are floats which represent the position in the
relative system (see above).

The rating of the ball is the mean quadratic error provides information about
how perfekt the found ball can be fitted by the algorithms. Perfectly round
objects get a lower rating and therefore a lower rating indicates a better ball
candidate.

The rating of -2 is reserved for an alternative method to find the ball. These
ball candidates are always preferred.

GoalInfo
~~~~~~~~
The GoalInfo contains the color of the goal posts and an arbitrary number of
GoalPost objects.

Each GoalPost object holds the information about the relative and the absolute
position and dimensions (width and height) as well as a rating and whether the
foot point of the post is inside the field.

Obstacle
~~~~~~~~
::

    [TODO]

RobotData
~~~~~~~~~
::

    [TODO]

ImageData
~~~~~~~~~
::

    [TODO]

The processing
--------------

This section gives a short overview over our strategies to process the images.

The point cloud
~~~~~~~~~~~~~~~
::

    [TODO]


Strategie to find the ball
~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    [TODO]


Strategie to find the goal
~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    [TODO]


Strategie to find obstacles
~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    [TODO]

