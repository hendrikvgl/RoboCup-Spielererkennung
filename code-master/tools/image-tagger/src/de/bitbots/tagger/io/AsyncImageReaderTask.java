package de.bitbots.tagger.io;

import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.util.zip.GZIPInputStream;

import javax.swing.SwingWorker;

public class AsyncImageReaderTask extends SwingWorker<BufferedImage, Void> {
	private File file;
	private int width;
	private int height;

	private Exception exception;
	private BufferedImage image;

	/**
	 * Erzeugt einen AsyncImageReaderTask mit einer zu lesenden Datei. Es muss
	 * die Größe des Bildes angegeben werden, da die YUYV Datei keinen Header
	 * hat.
	 * 
	 * Die Datei kann nach dem laden mit get() abgefragt werden. Möchte man im
	 * EventDispatcherThread über das Ende des Vorgangs benachrichtigt werden,
	 * sollte man die done()-Methode überladen.
	 * 
	 * @param file
	 *            Datei, die ausgelesen werden soll
	 * @param width
	 *            Breite des Bildes
	 * @param height
	 *            Höhe des Bildes
	 */
	public AsyncImageReaderTask(File file, int width, int height) {
		this.file = file;
		this.width = width;
		this.height = height;
	}

	@Override
	protected BufferedImage doInBackground() {
		try {
			InputStream input = new FileInputStream(file);
			try {
				// Wenn nötig, GZIP dekomprimieren
				if(file.getName().endsWith(".gz")) {
					input = new GZIPInputStream(input);
				}

				image = YUYVImageReader.readColorImage(input, width, height);
				return image;
			} finally {
				input.close();
			}
		} catch (Exception ex) {
			exception = ex;
			return null;
		}
	}

	/**
	 * Gibt eine Exception zurück, falls ein Fehler aufgetreten ist.
	 * 
	 * @return
	 */
	public Exception getException() {
		return exception;
	}

	public BufferedImage getImage() {
		return image;
	}
}
