VisionSkript
============

Mit dem Visionskript kann die Vision lokal und auf dem Roboter getestet werden.
Es können Optionen und auch Testbilder oder Ordner, die solche enthalten als
Kommandozeilenparemeter übergeben werden. Dann werden die gegebenen Testbilder
abgearbeitet. Alternativ wird auf die Camera zugegriffen.
Dabei werde die verarbeiteten Bilder in eine Fenster auch immer angezeit.
Die Vision unterstützt dabei die folgenden Optionen:

    NoGui: -n, --no-gui

        Auf die Anzeige der Bilder wird verzichtet

    Record: -r

        Mit der Record Option können Testbilder aufgenommen und auf der Festplatte
        gespeicher werden. Record ist implizit ohner Anzeige der Bilder

    Benchmark: -b

        Es wird ein Benchmark gestartet. Wenn lokale Bilder angegeben sind, dann
        wird über diese der Benchmark ausgeführt, ansonsten werden 100 oder 1000
        Camerabilder genommen. Zum Abschluss wird die Laufzeitstatistik ausgegeben.
        Ein Benchmark unterstützt keine Anzeige der Bilder.

    Preload: -p, --preload

        Mit der Preload Option werden, die zu verarbeitenden Bilder zuerst
        alle in den Ram geladen, bevor die Verarbeitung mit der Vision beginnt.

    Recalibrate: -c, --recalibrate

        Unsere Vision ist in der Lage, eine neue Ballmaske aufzunehmen. Das kann
        mit dieser Option veranlasst werden

    CameraResolution: -R --resolution

        Es kann eine andere Kameraauflösung als in der Config angegeben erzwungen
        werden.
