
package de.bitbots.tagger.io;


import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.OutputStream;
import java.util.Collection;
import java.util.HashMap;
import java.util.Map;

import de.bitbots.tagger.gui.ImageInfoModel;


public class DataStore {

	private final File file;
	private Map<String, ImageInfoModel> infos;


	public DataStore(File file) {
		this.file = file;
		infos = new HashMap<String, ImageInfoModel>();
	}

	@SuppressWarnings("unchecked")
	private void load() throws Exception {
		InputStream input = new FileInputStream(file);
		try {
			ObjectInputStream oin = new ObjectInputStream(input);
			infos = (Map<String, ImageInfoModel>)oin.readObject();
		} finally {
			try {
				input.close();
			} catch (IOException io) {}
		}
	}

	public void save() throws Exception {
		OutputStream output = new FileOutputStream(file);
		try {
			for (ImageInfoModel info : infos.values()) {
				info.setDataSaved(true);
			}
			new ObjectOutputStream(output).writeObject(infos);
		} finally {
			try {
				output.close();
			} catch (IOException io) {
				for (ImageInfoModel info : infos.values()) {
					info.setDataSaved(false);
				}
			}
		}
	}

	public ImageInfoModel getImageInfoModel(File file) {
		String name = file.getName();
		if (!infos.containsKey(name)) {
			infos.put(name, new ImageInfoModel(file));
		}

		return infos.get(name);
	}

	public Collection<ImageInfoModel> getImageInfoModels() {
		return infos.values();
	}

	static public DataStore load(File file) throws Exception {
		DataStore store = new DataStore(file);
		store.load();
		return store;
	}

	public void export() throws Exception {
		new Exporter(this).export(new File(file.getParentFile(), "export.json"));
	}
}
