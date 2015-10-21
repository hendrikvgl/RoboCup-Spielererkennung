package de.bitbots.tagger.gui.shapes;

import java.awt.Graphics2D;

public class RectangleShapeComponent extends ShapeComponent {
	private static final long serialVersionUID = 1L;

	public RectangleShapeComponent() {
		setAntialiasing(false);
	}

	@Override
	protected void paintShape(Graphics2D gra) {
		gra.drawRect(0, 0, getWidth() - 1, getHeight() - 1);
	}
}
