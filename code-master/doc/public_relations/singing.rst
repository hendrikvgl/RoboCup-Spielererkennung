Singen mit dem Darwin 
=====================

Vorbedingungen
--------------

* Es muss das sprachsyntheseprogramm festival installiert werden

Musikdatei programmieren
------------------------
Nun muss man eine .xml-Datei erstellen welche folgende Syntax hat:

.. code-block :: xml

  <?xml version="1.0"?>
  <!DOCTYPE SINGING PUBLIC "-//SINGING//DTD SINGING mark up//EN" 
        "Singing.v0_1.dtd"
        []>
        <SINGING BPM="50">
          <PITCH NOTE="G4,G4"><DURATION BEATS="0.25,0.25">happy</DURATION></PITCH>
          <PITCH NOTE="A4,G4"><DURATION BEATS="0.25,0.25">birthday</DURATION></PITCH>
          <PITCH NOTE="C4"><DURATION BEATS="0.25">to</DURATION></PITCH>
          <PITCH NOTE="H4"><DURATION BEATS="0.5">you</DURATION></PITCH>
          <PITCH NOTE="G4,G4"><DURATION BEATS="0.25,0.25">happy</DURATION></PITCH>
          <PITCH NOTE="A4,G4"><DURATION BEATS="0.25,0.25">birthday</DURATION></PITCH>
          <PITCH NOTE="D4"><DURATION BEATS="0.25">to</DURATION></PITCH>
          <PITCH NOTE="C4"><DURATION BEATS="0.5">you</DURATION></PITCH>
          <PITCH NOTE="G4,G4"><DURATION BEATS="0.25,0.25">happy</DURATION></PITCH>
          <PITCH NOTE="G5,E4"><DURATION BEATS="0.25,0.25">birthday</DURATION></PITCH>
          <PITCH NOTE="C4,C4"><DURATION BEATS="0.25,0.25">dear</DURATION></PITCH>
          <PITCH NOTE="H4,A4"><DURATION BEATS="0.25,0.25">Ollie</DURATION></PITCH>
          <PITCH NOTE="F4,F4"><DURATION BEATS="0.25,0.25">happy</DURATION></PITCH>
          <PITCH NOTE="E4,C4"><DURATION BEATS="0.25,0.25">birthday</DURATION></PITCH>
          <PITCH NOTE="D4"><DURATION BEATS="0.25">to</DURATION></PITCH>
          <PITCH NOTE="C4"><DURATION BEATS="0.5">you</DURATION></PITCH>
        </SINGING>

Musikdatei abspielen
--------------------

mit ::

 festival

festival starten und dann mit ::

 (tts "dateiname.xml" 'singing)

Die gesungene wiedergabe starten.

