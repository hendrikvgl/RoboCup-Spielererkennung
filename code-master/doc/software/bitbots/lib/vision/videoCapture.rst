.. _videoCapture:

Video Erfassung
===============

video_capture bietet mehrere Methoden zur Erfassung der Bilder und zum Ändern von Kontrast und ähnlichem. 

Methoden:
---------

.. cpp:class:: Vision::VideoCapture

	.. cpp:function:: void open(const std::string& device)

		Öffnet ein Device.
		
	.. cpp:function:: void start()

		Startet den Aufnamevorgang.

	.. cpp:function:: void set_pixel_format(const std::string& fmt, int width, int height)

		Setzt das Pixelformat. Wirft bei ungültigem Format eine Exception.
		fmt ist ein FOURCC wie YUYV.

	.. cpp:function:: bool ioctl(int request, T& data, bool quiet=false)

		Führt einen ioctl mit Fehlerüberprüfung aus.

	.. cpp:function:: const std::string& get_pixel_format()

		Gibt das PixelFormat als String zurück.

	.. cpp:function:: int get_width()

		Gibt die Breite des Bildes zurück.

	.. cpp:function:: int get_height()

		Gibt die Höhe des Bildes zurück.

	.. cpp:function:: void set_image_decoder()

		Setzt eine ImageDecoder Klasse.

	.. cpp:function:: PixelFormatList enumerate_pixel_formats()

		Gibt eine Liste mit allen Unterstützen Pixelformaten zurück.
		Ein Pixelformat ist dabei ein Paar, dessen erster Wert ein.

	.. cpp:function:: Controller& get_brightness() 

		Stellt einen Controller bereit, mit dem die Helligkeit des Bildes
		reguliert werden kann.

	.. cpp:function:: Controller& get_contrast()

		Stellt einen Controller bereit, mit dem die Helligkeit des Bildes
		reguliert werden kann.
		
	.. cpp:function:: Controller& get_saturation()

		Stellt einen Controller bereit, mit dem die Sättigung des Bildes
		reguliert werden kann.
		
	.. cpp:function:: Controller& get_hue()

		Stellt einen Controller bereit, mit dem der Farbton des Bildes
		reguliert werden kann.
		
	.. cpp:function:: Controller& get_sharpness()

		Stellt einen Controller bereit, mit dem die Schärfe des Bildes
		reguliert werden kann.
		
	.. cpp:function:: cv::Mat grab(cv::Mat mat)

		Ließt ein Bild von der Kamera aus und gibt es in dem korrekten
		Format zurück.
		
.. cpp:class:: Vision::VideoCapture::Controller

	.. cpp:function:: float get_default()
	
		TODO beschreibung
		
	.. cpp:function:: std::string get_name()
	
		TODO beschreibung
	
	.. cpp:function:: float get_value()
	
		TODO beschreibung
		
	.. cpp:function:: void set_value(float v)
	
		TODO beschreibung
