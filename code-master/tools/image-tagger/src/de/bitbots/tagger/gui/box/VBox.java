package de.bitbots.tagger.gui.box;

import java.awt.Component;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;

public class VBox extends Box {
	private static final long serialVersionUID = 1L;

	public VBox() {
		setLayout(new GridBagLayout());
		index = 0;
	}

	@Override
	public void add(Component comp, boolean expand, boolean fill) {
		GridBagConstraints gc = new GridBagConstraints();
		gc.anchor = GridBagConstraints.CENTER;
		gc.gridx = 0;
		gc.gridy = index;
		gc.weightx = 1;

		gc.fill = GridBagConstraints.HORIZONTAL;
		if(fill) {
			gc.fill = GridBagConstraints.BOTH;
		}

		if(expand) {
			gc.weighty = 1;
		}

		if(index > 0 && spacing > 0) {
			gc.insets.top = spacing;
		}

		add(comp, gc);
		index++;
	}
}
