package de.bitbots.tagger.gui.shapes;

import java.awt.Graphics2D;

public class CircleShapeComponent extends ShapeComponent {
	private static final long serialVersionUID = 1L;

	@Override
	protected void paintShape(Graphics2D gra) {
		gra.drawOval(0, 0, getWidth() - 1, getHeight() - 1);
	}
}
