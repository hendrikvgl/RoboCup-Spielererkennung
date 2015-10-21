package de.bitbots.tagger.gui.box;

import java.awt.Component;
import java.awt.GridBagConstraints;

public class HBox extends Box {
	private static final long serialVersionUID = 1L;

	@Override
	public void add(Component comp, boolean expand, boolean fill) {
		GridBagConstraints gc = new GridBagConstraints();
		gc.anchor = GridBagConstraints.CENTER;
		gc.gridx = index;
		gc.gridy = 0;
		gc.weighty = 1;

		gc.fill = GridBagConstraints.VERTICAL;
		if(fill) {
			gc.fill = GridBagConstraints.BOTH;
		}

		if(expand) {
			gc.weightx = 1;
		}

		if(index > 0 && spacing > 0) {
			gc.insets.left = spacing;
		}

		add(comp, gc);
		index++;
	}
}
