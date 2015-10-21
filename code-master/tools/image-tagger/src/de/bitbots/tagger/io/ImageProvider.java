package de.bitbots.tagger.io;

import java.io.File;
import java.io.FilenameFilter;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import javax.swing.SwingWorker;

public class ImageProvider extends SwingWorker<Boolean, Void> {
	private File directory;
	private List<File> fileList;

	public ImageProvider(File directory) {
		this.directory = directory;
	}

	@Override
	protected Boolean doInBackground() {
		File[] files = directory.listFiles(new FilenameFilter() {
			@Override
			public boolean accept(File dir, String name) {
				return name.endsWith(".yuv") || name.endsWith(".yuv.gz");
			}
		});

		if(files == null) {
			return false;
		}

		fileList = Arrays.asList(files);
		Collections.sort(fileList);
		return true;
	}

	public List<File> getFileList() {
		return fileList;
	}
}
