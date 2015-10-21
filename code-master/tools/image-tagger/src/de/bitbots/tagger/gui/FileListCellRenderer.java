
package de.bitbots.tagger.gui;


import java.awt.Component;
import java.io.File;

import javax.swing.DefaultListCellRenderer;
import javax.swing.JList;

import de.bitbots.tagger.io.DataStore;


public class FileListCellRenderer extends DefaultListCellRenderer {

	private static final long serialVersionUID = 1L;
	private DataStore dataStore;


	@Override
	public Component getListCellRendererComponent(JList list,
	                                              Object value,
	                                              int index,
	                                              boolean isSelected,
	                                              boolean cellHasFocus) {
		File f = (File)value;
		String str = f.getName();
		if (dataStore != null) {
			ImageInfoModel info = dataStore.getImageInfoModel(f);
			if (!info.isDataSaved()) {
				str = "*" + str;
			}
			boolean needsHTML = false;
			if (info.hasData()) {
				needsHTML = true;
				str = "<b>" + str + "</b>";
			}
			if (info.hasInvalidCoordinates()) {
				needsHTML = true;
				str = "<font color=\"#ff0000\">" + str + "</font>";
			}
			if (needsHTML) {
				str = "<html>" + str + "</html>";

			}
		}
		return super.getListCellRendererComponent(list, str, index, isSelected, cellHasFocus);
	}

	public void setDataStore(DataStore dataStore) {
		this.dataStore = dataStore;
	}
}
