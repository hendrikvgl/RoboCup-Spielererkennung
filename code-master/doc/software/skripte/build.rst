Build
=====

mit dem Buildskript bauen wir unsere Software.
Das Buildskript stellt sicher, dass wir uns im Bitbots-Virtualenv befinden,
bevor gebaut wird. Danach werden mehrere Optionen abgehandelt, bevor
mit CMake die Makefiles für den Code automatisch generiert werden und danach
kompiliert werden. Das Buildskript legt automatisch ein Verzeichnis zum Bauen
an. Dieses ist spezifisch für den Compiler und den Buildtyp, wie z.B.
Release, ReleaseWithDebugInf oder Debug. Wenn kein Buildtyp angegeben wird,
dann wird automatisch Debug angenommen.
Nach einen erfolgreichen Build werden die Tests ausgeführt (siehe find_test_failures).
Mit der ConsolenVariable QUIET kann das Ausführen der Tests unterdrückt werden.

Aktionen des Buildskriptes:
---------------------------

    Update VirtualEnv:

        siehe update-env.sh

    Bestimmung des Compilers:

        Wir können unseren Code mit gcc und mit clang bauen. Je nachdem welcher
        installiert ist und welche Optionen gegeben wird wird einer der beiden
        Compiler zum bauen genutzt.

    Auswahl der Architektur:

        Unsere Darwins haben einen Atomprozessor. Für diesen muss speziell Optimiert werden.
        Seit dem wir die MiTeCom Teamkommunikation benutzen, ist der 32-Bit-Architektur-Code
        nicht mehr in jeden Fall mit den 64-Bit-Systemen kompatibel, auch denen
        wir entwickeln. Des weiteren haben wir mitlerweile einen Odroid.
        Dieser hat eine ARM-Architektur.

    Auswahl des Buildpfades:

        Zum bauen wird ein eigenes Verzeichnis angelegt, in dem gebaut wird.

    Virtual-env aktivieren:

        Zum bauen und installieren müssen wir uns im Virtual-env befinden.
        Wenn das Virtual-env aktiviert ist, dann wird es ggf unter .py-env verlinkt,
        damit beim nächsten Mal das Virtual-env auch automatisch aktiviert werden kann.

Optionen des Buildskriptes:
---------------------------

    Clean: -c, --clean, --clean-env, --clean-build-path

        Die Clean Option gibt es in verschiedenen Ausprägungen. Je nachdem
        welcher Parameter gegeben ist, werden verschiedene Sachen gemacht.
        Mit --clean-env werden im Virtual-env so viele Dateien wie möglich,
        die zu unserer Software gehören gelöscht. Da nicht alle unsere installierten
        Dateien in eindeutig zu uns gehörenden Ordnern liegen, ist das nicht zu
        100 Prozent möglich. Durch im Virtual-env verbliebende Dateien sind
        schon des öfteren Tests bei den Entwickelndes Personen nicht fehlgeschlagen,
        obwohl das zu importierende Modul nicht mehr vorhanden war. Diese Fehler
        blieben gerne mehrere Wochen unentdeckt, bis ein neues Mitglied die
        Software das erste Mal bauen wollte.
        --clean-build-path löscht das Verzeichnis, in dem gebaut wird. Normalerweise
        wollen wir inkrementelle Builds haben, um nicht jedes Mal die komplette
        Software zu bauen. In Ausgewählten Situationen kann es aber dazu kommen,
        das auf diese Art Fehler entstehen, oder vermieden werden, die andernfalls
        nicht auftreten würden. Besonders beim Löschen von C++ Dateien sollte ein
        Clean Build ausgeführt werden, da die gelöschten Header häufig noch importiert werden.
        --clean und -c sind Abkürzungen für CleanBuildPath und CleanVirtualEnv.

    Choose Compiler: -gcc -clang

        Wir wollen unseren Code mit dem LLVM Clang bauen, der aber nicht auf allen
        Rechnern installiert ist, und auch nicht auf jeden System Compilieren kann.
        Deswegen gibt es Optionen, mit denen die Auswahl des Compilers beeinflusst werden
        kann. Wenn der clang installiert ist, dann wird im Standardfall auch mit
        clang compiliert. Clang ist etwas schneller und poduziert besser verständliche
        Fehlermeldungen. Alternativ kann auch die Consolenvariable "NOCLANG" auf 1 gesetzt sein.
        Dann wird auch mit dem gcc gebaut.

    Build Typ: Release, ReleaseWithDebugInf, Debug

        Über den Buildtype werde verschiedene Optionen zum Compilieren ausgewählt.
        Ein ReleaseBuild ist hoch optimiert und z.B. schwer bis unmöglich zu debuggen.
        Besonders Speicherzugriffsfehler sollten nicht mit Releasebuilds gesucht werden.
        Die Debugbuilds sind deutlich weniger starkmoptimiert, so dass ein debuggen
        des Codes noch möglich ist. Allerdings kann die Ausführungszeit schnell eine bis
        2 Größenorndungen höher sein.

    Include Project: -i

        Momentan gibt es mehrere Unterprojekte, die zwar vorhanden sind, aber nicht
        ausgeführt werden. Sie werden momentan auch nicht gebaut. Um sie dennoch
        zu bauen können sie mit -i <PROJEKTNAME> dennoch gebaut werden.

    Nur Python: -p, --python-only

        Mit dieser Option werden nur die .py-Dateien unterhalb des lib-Ordners
        in das Virtual-env kopiert. Damit kann das zeitaufwendige Kompilieren
        des C-Cdes übersprungen werden.

    Exit: -e

        Eine Option zu sofortigen Beendes des Buildskripten, wenn man z.B. nur
        den update-env Teil oder nur ein clean ausführen möchte.

    -D Compiler Optionen: -D<ONE_WORD_CPP_COMPILER_OPTION>

        CMake und auch dem benutzten C-Compiler können via -D noch weitere Optionen
        gegeben werden. So kann z.B. für den C++-Teil ein zu kompilierendes Debug-
        Level gegeben werden. Auf diese Art gibt es keine Debug-Statements, die ein
        Höheres Level als das angegebene haben. Das kann mit -DDEBUG_LEVEL=X gesetzt werden.

    -j Number CPS's

        Mit -j kann für das Bauen angegeben werden, wie vieler parallele Prozesse
        verwendet werden.

    -v

        Verbose Build output

    -vv

        Verbose Build output und verbose Makefiles
