#-*- coding:utf-8 -*-__author__ = 'Benjamin Scholz'"""Entwickelt im Robo-Cup Praktikum SoSe 2014Dieses Skript spiegelt Animationen und speichert sie dann in einer neuen Datei ab.Dies ist zum Beispiel nützlich um eine Schussanimation für den anderen Fuß zu erstellen."""#Dateien öffnenfile = raw_input("Datei: ") + ".json"f = open(str(file), "r")new_file = raw_input("Neue Datei: ") + ".json"g = open(str(new_file), "w")#Dokument Zeile für Zeile durchgehenfor line in f:    #Wenn in der Zeile ein Wert für einen rechten oder linken Motor angegeben ist,     #dann wird L mit R getauscht und der jeweilige Wert negiert.    if line[17:18]=='R' or line[17:18] == 'L':        line = line[:17] + line[17:19].replace('R', '&') + line[19:]        line = line[:17] + line[17:19].replace('L', 'R') + line[19:]        line = line[:17] + line[17:19].replace('&', 'L') + line[19:]        line = line.replace(': -', 'minus')        line = line.replace(': ', ': -')        line = line.replace('minus', ': ')        line = line.replace('-0', '0')    #Die geänderten Zeilen werden in eine neue Datei geschrieben.    g.write(line)