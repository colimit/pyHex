pyHex
=====

Yet another hex project, this time a python pygame program with a very simple monte carlo ai.

This project repo contains a pygame program for playing a simple AI (depends on pygame & pygraph).

hex.c is c ai which currently outputs its opinion best starting square for red and the best response for blue.
The highlight of this code is a fast algorithm for evaluating the outcome of a random game continuation from a 
given position, capable of generating and evaluating a million positions in about a minute, using bit operations on
an array of integers representing the rows of the board.

Note that this c code is not currently integrated with the python program.
