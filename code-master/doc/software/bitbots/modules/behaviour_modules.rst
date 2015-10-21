.. _sec_behaviour:

Standard Verhalten
******************

Zur Saison 2014 haben wir angefangen unser Verhalten umzubauen.  Statt einer Statemachine dient nun ein Stack mit einem Entscheidungsbaum als Vorbild.

Benutzung
#########

Normales starten
----------------
Das neue Verhalten wird mit dem Befehl "start-behaviour" gestartet. Auf diese Weise entscheidet er selbstständig welche Position er im  Spiel einnimmt. Man kann die Spielposition auch mit "start-behaviour {Fieldie,Goalie}" erzwingen.
Auf diese Weise können auch Spezielle Verhalten wie der ThrowIn gestartet werden.

Starten eines einzelnen Elementes
---------------------------------
Mit "start-element <element>" kann direkt in einen bestimmten Punkt des Verhaltens gesprungen werden.  <element> ist Beispielsweise "actions.KickBall". In dem Fall würde er direkt versuchen den Ball zu Kicken.
Hier muss beachtet werden, dass gegeben falls bestimmte Vorbedingungen nicht erfüllt sind, oder Defaultwerte benutzt werden.

Aufbau
######
Das Verhalten ist in verschiedene
Elemente Auf dem Stack
Folgende Elemente können auf den Stack geladen werden, diese Erben alle von AbstractStackElement und werden vom Framework aufgerufen. Sie bilden die Knoten im Entscheidungsbaum. Jedes mal wenn das Verhalten im system drann ist wird das jeweils oberste Element auf dem Stack aufgerufen.

Actions
-------
Actions sind im allgemeinen die Blätter im Entscheidungsbaum.
Actions definieren die Handlungen eines Roboters, zum Beispiel wie er sich fortbewegen soll oder, dass er einen Animation abspielen soll. Es sollten hier keine Komplexen Entscheidungen gefällt werden, besonders keine, die nicht direkt zu der auszuführenden Handlung gehören.

Decisions
---------
Decisions sind die internen Knoten im Entscheidungsbaum und definieren die Kanten. Sie bilden die Logik nach der entschieden wird was der Roboter gerade tut. Sie bekommen Ihre Daten aus der Schnittstelle zum Weltmodel und entscheiden welche Decision oder Action als nächstes aufgerufen wird. Außderdem können Decisions entscheiden ob sie bei jedem Verhaltensaufruf geprüft werden wollen, oder nur einmalig beim Abstieg im Baum.

Connector
---------
Der Connector bildet die Verbindung zwischen data dictionary aus den BasicModules und dem Verhalten. Dabei werden die Daten, welche im data dictionary stehen durch methoden
oder sogenannten Capsules gekapselt. Generelle Zugriffsmethoden finden sich im Connector direkt. Für andere Zugriffsbereiche gibt es im Conenctor verschiedene Capsules.
Als Einstieg sind hier vorallem die RawVisionInfoCapsule und die BehaviourBlackBoardCapsule zu nennen. In der RawVisionInfoCapsule finden sich Zugriffsmethoden für alle daten,
die direkt aus der Vision fallen. Die BehaviourBlackboardCapsule hingegen besitzt neben dem data dictionary welches global durchgereicht wird ein eigenes dictionary, welches
daten kapselt, welche nur vom Verhalten gesetzt bzw. gelesen werden. Es ist somit relativ eigenständig. Dort können sachen abgelegt werden, die sich das verhalten merken soll, was aber nicht gleich
im globalen Kontext publiziert werden muss. Es dient also Haupsächlich dem Seperation of Concerns.

Config
------
Die Config sollte immer benutzt werden, wenn man dem Code irgendwelche Konstanten gibt, z.B. die Entfernung zum Ball, bei der der Fieldie schießen soll. So können diese Werte wesentlich leichter angepasst werden und es können auch sehr leicht an verschiedenen Stellen im Code der gleiche Wert verwendet werden. Dies ist z.B. sehr hilfreich, wenn man eine andere Camera einbaut und sich damit der Kameraöffnungswinkel ändert. Dieser wird in ca. 12 verschiedenen Klassen benutzt und muss so nur einmal in der Config geändert werden.
Ein Configobject kann man einfach durch get_config() erhalten. Dann kann man z.B. mit config["Behaviour"]["Common"]["Camera"]["cameraAngle"] auf einen Wert zugreifen. Wenn man oft auf Configwerte aus dem selben Teil zugreifen will kann man auch ein zweites Configobjekt machen: behaviour_common_config = config["Behaviour"]["Common"] und dann behaviour_common_config["Camera"]["cameraAngle"] benutzen.
Configwerte werden _immer_ im Construktor als self. variable geladen und in den Methoden werden dann nur noch die Variablen benutzt. Dies hat den Vorteil, dass so sehr leicht Tippfehler oder fehlende Configwerte abgetestet werden können, indem einfach im Test der Konstruktor aufgerufen wird (dies sollte man auch für jede Klasse testen). Außerdem werden so die langen Configaufrufe im Code vermieden.
Die Namen für die Werte in der Config verfolgen die camelCaseConvention mit kleinem Anfangsbuchstaben. Die Unterteile der Config (z.B. ["Behaviour"]) sind auch im CamelCase aber mit großem Anfangsbuchstaben.

Entwicklung im neuen Verhalten
##############################
Programmieren
-------------
Aufbau
^^^^^^
Eine Element besteht aus einer Klasse die direkt oder Indirekt von AbstractActionModule oder AbstractDecisionModule erbt. Wird die Klasse auf den Stack geladen wird sie erzeugt und bleibt solange bestehen bis sie wieder Entfernt wird. Die __init__ Methode kann also als Konstruktor verwendet werden, hier werden zum Beispiel Werte aus der Config geladen, oder einmalige Berechnungen durchgeführt. Der Connector ist noch nicht verfügbar, allerdings können beim laden eines Elements auf den Stack Informationen mitgegeben werden, die hier empfangen werden.
Liegt das Element oben auf dem Strack wird perform() aufgerufen,  bis ein anderes Element über ihm auf dem Stack liegt. Hier landet also die Eigentliche Logik.
Zugriff auf  Informationen und Variablen
Im Verhalten kann auf die daten aus anderen Modulen bequem über den connector zugegriffen werden, dieser wird vom Framework in perform() übergeben und ist dementsprechned erst dort verfügbar.

Bewegen auf dem Stack
^^^^^^^^^^^^^^^^^^^^^
Es gibt 3 wesentliche Befehle um sich auf dem Stack zu bewegen:

* return self.push(NaechstesElement)
    Packt ein neues Element auf den Strack und führt dieses Sofort aus. Die Klasse muss vorher importiert werden.
* self.pop()
    Löscht sich selbst und alle tiefer liegenden Elemente vom Stack. (z.B. Beendigung einer Aufgabe)
* self.interrupt()
    Löscht den gesamten Stack, sodass er neu aufgebaut wird.

Reevaluieren
^^^^^^^^^^^^
Normalerweise wird nur das oberste Element des Stacks aufgerufen. Durch das überschreiben der Methode get_reevaluate() kann aber dafür gesorgt werden, dass  auch Elemente im Stack erneut betrachtet werden. So können vorbedingungen geprüft werden. Kommt das Element im Stack zur selben Entscheidung wie zuvor, wird anschließend ganz normal das oberste Element mit perform aufgerufen. Anderenfalls wird der stack bis zu der reevaluierenden Stelle abgeräumt.
Beim Aufruf des performs wird ein Flag übergeben, ob es sich hierbei um einen richtigen Aufruf handelt oder um einen Reevalutionsaufruf, so können ggf. nur einzelne Teile der Decision überprüft werden.
Arbeiten für verschiedene Verhalten
Wird eine Klasse für verschiedene Verhalten benutzt kann man sich entweder (bei Kleinen unterschieden) die Informationen als was gerade gespielt wird aus dem Connector geholt, oder man kann verschiedene Klassen von einen Basisimplementation erben lassen und einzelne Funktionen überschreiben

Sonsiges:
^^^^^^^^^
* Animationen abspielen; connector.play_animation("Name der Animation) Solange eine Animation noch läuft gibt connector.is_animation_busy() True zurück.


Tools
-----
Darstellung des Verhaltensbaums
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Es gibt ein Script unter tools/behaviour-graph/MakeGraph.py das aus den Code eine Grafische Darstellung des aktuellen Verhaltes erzeugt. Dafür wird das Modul "graphviz" benötigt, das aus den repositorys heruntergeladen werden kann.
"python MakeGraph.py" erzeugt die Datei "Verhalten.png"

.. todo::
    jetzt hier auf die Doku zu den verhaltensmodulen verweisen, die dann in den ordner behaviour kommt