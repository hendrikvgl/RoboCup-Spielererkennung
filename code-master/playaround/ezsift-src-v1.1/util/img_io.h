/*	Copyright (c) 2013, Robert Wang, email: robertwgh (at) gmail.com
	All rights reserved. https://sourceforge.net/p/ezsift

	Revision history:
		September, 15, 2013: initial version.
*/

#ifndef _IMG_IO_H_
#define _IMG_IO_H_

typedef struct {
  int w;
  int h;
  unsigned char * img_r;
  unsigned char * img_g;
  unsigned char * img_b;
} PPM_IMG;

int read_pgm(const char* filename, unsigned char * & data, int & w, int & h);
void write_pgm(const char* filename, unsigned char * data, int w, int h);

int read_ppm(const char * filename, unsigned char * & data, int & w, int & h);
void write_ppm(const char * filename, unsigned char * data, int w, int h);
void write_rgb2ppm(const char * filename, unsigned char* r, unsigned char* g, 
					unsigned char* b, int w, int h) ;

void write_float_pgm(const char* filename, float* data, int w, int h,  int mode);

void rasterCircle(PPM_IMG* imgPPM, int r, int c, int radius);
void draw_red_circle(PPM_IMG* imgPPM, int r, int c, int cR);
void draw_circle(PPM_IMG* imgPPM, int r, int c, int cR, float thickness);
void draw_red_orientation(PPM_IMG* imgPPM, int x, int y, float ori, int cR);

#endif//_IMG_IO_H_
