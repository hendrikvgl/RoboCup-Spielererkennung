package de.bitbots.tagger.gui;

import javax.swing.JCheckBox;
import javax.swing.SwingUtilities;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;

public class DeactivateOnlyCheckBox extends JCheckBox {
	private static final long serialVersionUID = 1L;

	public DeactivateOnlyCheckBox(String text) {
		super(text);
		getModel().addChangeListener(new ChangeListener() {
			@Override
			public void stateChanged(ChangeEvent event) {
				SwingUtilities.invokeLater(new Runnable() {
					@Override
					public void run() {
						setEnabled(isSelected());
					}
				});
			}
		});

		setEnabled(isSelected());
	}
}
