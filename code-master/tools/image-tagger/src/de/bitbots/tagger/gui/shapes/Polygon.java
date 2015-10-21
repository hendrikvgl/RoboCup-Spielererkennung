package de.bitbots.tagger.gui.shapes;

import java.awt.Color;
import java.awt.Graphics;
import java.awt.Point;
import java.util.ArrayList;
import java.util.List;

import javax.swing.JPanel;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;

public class Polygon extends JPanel {
	private static final long serialVersionUID = 1L;
	private static final Color PINK = new Color(255, 0, 255);

	protected ShapeComponent[] points;
	private boolean closed;

	public Polygon(int count) {
		setLayout(null);
		setOpaque(false);

		closed = true;

		points = new ShapeComponent[count];
		for(int i = 0; i < count; i++) {
			ShapeComponent point = new RectangleShapeComponent();
			point.setResizable(false);
			point.setSize(8, 8);
			point.setCenter((int) (25 + 20 * Math.sin(i * Math.PI * 2 / count)),
				(int) (25 + 20 * Math.cos(i * Math.PI * 2 / count)));
			point.setForeground(PINK);
			point.addDragChangeListener(pointChangeListener);
			add(point);

			points[i] = point;
		}
	}

	@Override
	protected void paintComponent(Graphics g) {
		g.setColor(PINK);
		for(int i = 1; i < points.length; i++) {
			Point pa = points[i - 1].getCenter();
			Point pb = points[i].getCenter();
			g.drawLine(pa.x, pa.y, pb.x, pb.y);
		}
		if(closed) {
			Point pa = points[0].getCenter();
			Point pb = points[points.length - 1].getCenter();
			g.drawLine(pa.x, pa.y, pb.x, pb.y);
		}
	}

	public List<Point> getCenterPoints() {
		List<Point> centers = new ArrayList<Point>();
		for(ShapeComponent sc : points) {
			centers.add(sc.getCenter());
		}

		return centers;
	}

	public void setCenterPoints(List<Point> centers) {
		for(int i = 0; i < points.length; i++) {
			points[i].setCenter(centers.get(i).x, centers.get(i).y);
		}
	}

	private ChangeListener pointChangeListener = new ChangeListener() {
		@Override
		public void stateChanged(ChangeEvent event) {
			repaint();
			if(externalChangeListener != null) {
				externalChangeListener.stateChanged(event);
			}
		}
	};
	private ChangeListener externalChangeListener;

	public void setChangeListener(ChangeListener cl) {
		externalChangeListener = cl;
	}
}
