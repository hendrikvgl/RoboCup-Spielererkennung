3D Druck Teile
**************

Teil erstellen
==============

Im gegensatz zu den Metallplatten benutzen wir jetzt nicht das Metal Sheet Template sondern das Standart(DIN) Template.
Das Vorgehen ist dann etwas anders. Wir machen genauso Sketche wie vorher auch, erzeugen dann aber keine Faces sondern machen Extrudes. Dabei können wir jetzt im Prinzip beliebige Formen machen. Das Teil kann dann auch noch weiterverarbeitet werden, indem man Teile wieder weg oder rausschneidet. Hierzu benutzt man auch das Extrude-Tool, welches man im Tool-Menü auf "Cut" stellen kann.

Grenzen des 3D Drucks
=====================

Es ist immer schwer zu sagen welche Objekte der 3D Drucker gut drucken kann und welche nicht, im Zweifelsfall hilft dabei nur ausprobieren. Aber es gibt schon einige Grundregeln an die man sich halten sollte:

Überhänge
'''''''''

Grundsätzlich kann der 3D Drucker nichts in die Luft drucken, da das Material das er auftägt schließlich irgendwo drauf landen muss. Deshalb sollte man das Objekt möglichst so aufbauen, dass es zumindest von einer Seite aus immer bis zum Boden geht. Falls das nicht möglich ist muss der Drucker Stützmaterial drucken. Dabei druckt er zusätzliche Strukturen um dort drauf dann die "richtigen" Features zu drucken. Dies ist natürlich zu vermeiden, weil das Zeit und Material kostet und weil man per hand nacher das Stützmaterial entfernen muss.

Steigungen
''''''''''

Wenn der Drucker eine Steigung die so /\ gelegen ist druckt spielt der Winkel keine wirkliche Rolle. Wird aber eine Steigung in V gedruckt muss auf den Winkel geachtet werden. Auch hier ist es schwer zu sagen bei welchem Winkel es noch geht, weil dieses vom Drucker und vom Material abhängig ist, aber man kann grundsätzlich sagen, dass es unter 30° eigentlich immer geht und über 45° eigentlich nicht.

Lücken
''''''

Wie schon gesagt kann der Drucker nicht in der Luft drucken, aber es gibt einen Trick um das in bestimmten Fällen doch zu erreichen, das sogenannte "Bridging". Dabei zieht der Drucker den Plastikfaden über eine Lücke hinweg, wie eine Brücke. Dieses funktioniert nur für gewisse Entfernungen. Auch hier ist kein genauer Wert möglich, aber normalerweise ist der Bereich in dem es noch geht ca. 1cm

Kurven / Rundungen
''''''''''''''''''

Bei Kurven und Rundungen muss bedacht werden, dass diese aus einzelnen Linien aufgebaut werden und deshalb keine perfekten Kurven entstehen können. Der Grad der Genauigkeit ist dann abhängig von der Schichtendicke und anderen erweiterten Einstellungen des Druckers und Slicers.

Ecken
'''''

Bei Ecken muss bedacht werden, dass diese unter Umständen nicht perfekt 90° werden können, falls das Plastik sich leicht verzieht. Dies kann vorallem an auf dem Druckbett aufliegenden Ecken der Fall sein. Sollte mit unserem Drucker aber durch das beheizte Druckbett nicht so ein Problem darstellen.

Details
'''''''

Details können auch nur bis zu einem gewissen Grad abgebildet werden. Auch dies ist hauptsächlich von der Schichtdicke abhängig. Außerdem noch davon in welcher Orientierung das Detail liegt, da es in Z Achse (nach oben) anders ist als in X und Y.