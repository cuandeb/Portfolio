# Modelling & Numerical 

Modelling and Numerical Simulation comprises of a number of projects related to the modelling of 
physical systems either through solving differential equations or generating some random or 
iterative process. Two of these projects were college assignments and two were independent projects done
out of interest and to practice my coding. 

## Diffusion Limited Aggregation 

This was a project as part of my "Physics and Astronomy Advanced Lab" module which I took as
part of my undergraduate degree. The code attempts to replicate the physical process known
as Diffusion Limited Aggregation, a process seen in nature in which particles moving under 
random motion clump together around a central seed creating snowflake like patterns. This can
be seen in electrodeposition, mineral deposits and many other natural settings. 

The idea behind the code is to generate a set of random walkers that are "born" around a circular
radius defined by the program. These walkers then move inward toward the central seed particle
and if they meet another particle will stick to it and the next walker is generated and begins 
the walk. When the total particle count exceeds a certain number the loop breaks and the plotted
image is returned. 

There are additions that can be made to the code. For example a probability of sticking could 
be introduced that would vastly change the output images.

## GPS Trilateration 

This was an assignment as part of the "Applications of Space Science" course taken during my 
MSc. The section was related to satellite navigation and GPS systems. The aim of the project 
was to demonstrate how GPS satellites can calculate the position of a GPS receiver through 
the process of trilateration. This process is the solving of a system of 4 non-linear equations
using the Newton-Raphson method for finding roots. 

The input given was the coordinates and times of 4 GPS satellites (Given in the file "gps_data.txt")
and using the above method the process demonstrated that the GPS receiver was located at a
position in South Dublin. However the process would work for any GPS satellite readings. 


## Julia Set 

This was a small independent project that I undertook after observing that it is a relatively 
straightforward process to plot intricate fractal images using only a few basic functions. 

The mathematics are straightfoward and explained in the notebook and in my opinion this is a 
good example of compact functional code that outputs beautiful images. There is also great wallpaper 
potential!


## Lorenz Attractor 

This was another independent project that was intially going to be part of an application for a
summer internship a few years ago. However it grew a little over time and was something I was 
ticking away at every now and again. The project was actually inspired by the book *Chaos* by 
James Glieck which is one of the best science books I have read and deals with the history of 
chaos theory and dynamical systems. 

The project is based around the Lorenz attractor, a set of non-linear differential equations with 
3 time dependent variables that represent the flow of liquid in a heated box over time. In the 
notebook these 3 equations are solved using the Runge-Kutta method for numerically solving 
differential equations. The phase spaces are plotted which result in the iconic periodic
looping plots associated with chaos theory.

A brief investigation is then made into how the system is affected by subtle changes in initial
condition, one of the most prominent features of dynamical systems. 

Finally as a brief aside, I managed to create a gif of the attractor developing over time by 
saving an image of the plot at each iteration and then stitching them together using the 
*imagio* package in Python. 
