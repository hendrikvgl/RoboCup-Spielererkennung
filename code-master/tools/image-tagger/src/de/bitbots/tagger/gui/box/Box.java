package de.bitbots.tagger.gui.box;

import java.awt.Component;
import java.awt.GridBagLayout;

import javax.swing.JPanel;

abstract public class Box extends JPanel {
	private static final long serialVersionUID = 1L;
	protected int index;
	protected int spacing;

	public Box() {
		setLayout(new GridBagLayout());
		spacing = 5;
	}

	abstract public void add(Component component, boolean expand, boolean fill);

	@Override
	public Component add(Component component) {
		add(component, false, true);
		return component;
	}

	public void add(Component component, boolean expand) {
		add(component, expand, true);
	}

	public void addFiller() {
		add(new JPanel(), true, true);
	}

	public void setSpacing(int spacing) {
		this.spacing = spacing;
	}
}