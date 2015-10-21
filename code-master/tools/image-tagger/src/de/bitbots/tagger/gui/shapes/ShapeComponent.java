package de.bitbots.tagger.gui.shapes;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.Point;
import java.awt.Rectangle;
import java.awt.RenderingHints;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.Collection;

import javax.swing.JComponent;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;

public abstract class ShapeComponent extends JComponent {
	private static final long serialVersionUID = 1L;
	final static private int quadSize = 8;
	final static BasicStroke DASHED_STROKE = new BasicStroke(1.0f, BasicStroke.CAP_BUTT, BasicStroke.JOIN_MITER, 3.0f,
		new float[] { 3.f }, 0.0f);

	private boolean square;
	private boolean drawBorder;
	private boolean antialiasing;
	private boolean resizable;

	private Collection<ChangeListener> listeners;
	private Collection<ChangeListener> dragListeners;

	public ShapeComponent() {
		listeners = new ArrayList<ChangeListener>();
		dragListeners = new ArrayList<ChangeListener>();

		setResizable(true);
		addMouseListener(mouse);
		addMouseMotionListener(mouse);
	}

	public void setResizable(boolean resizable) {
		this.resizable = resizable;
	}

	public boolean getResizable() {
		return resizable;
	}

	public void setAntialiasing(boolean antialiasing) {
		this.antialiasing = antialiasing;
	}

	public void setCenter(int x, int y) {
		setLocation(x - getWidth() / 2, y - getHeight() / 2);
	}

	public Point getCenter() {
		return new Point(getX() + getWidth() / 2, getY() + getHeight() / 2);
	}

	public void addChangeListener(ChangeListener li) {
		listeners.add(li);
	}

	public void removeChangeListener(ChangeListener li) {
		listeners.remove(li);
	}

	protected void fireChangeEvent() {
		ChangeEvent event = new ChangeEvent(this);
		for(ChangeListener li : listeners) {
			li.stateChanged(event);
		}
	}

	protected void fireDragChangeEvent() {
		ChangeEvent event = new ChangeEvent(this);
		for(ChangeListener li : dragListeners) {
			li.stateChanged(event);
		}
	}

	@Override
	protected void paintComponent(Graphics _g) {
		Graphics2D g = (Graphics2D) _g.create();

		if(resizable && getDrawBorder() && hasFocus()) {
			g.setColor(Color.BLACK);
			g.setStroke(DASHED_STROKE);
			g.drawRect(quadSize / 2, quadSize / 2, getWidth() - quadSize - 1, getHeight() - quadSize - 1);

			g.setColor(Color.WHITE);
			g.fillRect(0, 0, quadSize, quadSize);
			g.fillRect(getWidth() - quadSize - 1, 0, quadSize, quadSize);
			g.fillRect(getWidth() - quadSize - 1, getHeight() - quadSize - 1, quadSize, quadSize);
			g.fillRect(0, getHeight() - quadSize - 1, quadSize, quadSize);

			g.setColor(Color.BLACK);
			g.setStroke(new BasicStroke());
			g.drawRect(0, 0, quadSize, quadSize);
			g.drawRect(getWidth() - quadSize - 1, 0, quadSize, quadSize);
			g.drawRect(getWidth() - quadSize - 1, getHeight() - quadSize - 1, quadSize, quadSize);
			g.drawRect(0, getHeight() - quadSize - 1, quadSize, quadSize);
		}

		if(antialiasing) {
			g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
		}

		g.setColor(getForeground());
		paintShape(g);
	}

	public boolean getDrawBorder() {
		return drawBorder;
	}

	public void setDrawBorder(boolean drawBorder) {
		this.drawBorder = drawBorder;
	}

	public boolean isSquare() {
		return square;
	}

	public void setSquare(boolean square) {
		this.square = square;
	}

	static enum DragMode {
		NW, NE, SE, SW, MOVE
	}

	MouseAdapter mouse = new MouseAdapter() {
		private Rectangle bounds;
		private Point start;

		private DragMode mode;

		@Override
		public void mouseClicked(MouseEvent e) {
			requestFocus();
		};

		@Override
		public void mousePressed(MouseEvent e) {
			start = new Point(e.getXOnScreen(), e.getYOnScreen());
			bounds = getBounds();
			updateMode(e);
		};

		@Override
		public void mouseDragged(MouseEvent e) {
			if(start == null) {
				return;
			}

			int dx = e.getXOnScreen() - start.x;
			int dy = e.getYOnScreen() - start.y;

			Rectangle bounds = new Rectangle(this.bounds);
			switch (mode) {
			case MOVE:
				bounds.x += dx;
				bounds.y += dy;
				break;

			case NW:
				bounds.x += dx;
				bounds.y += dy;
				bounds.width -= dx;
				bounds.height -= dy;
				if(isSquare()) {
					if(bounds.width > bounds.height) {
						bounds.y -= bounds.width - bounds.height;
						bounds.height = bounds.width;
					} else {
						bounds.x -= bounds.height - bounds.width;
						bounds.width = bounds.height;
					}
				}
				break;

			case NE:
				bounds.y += dy;
				bounds.width += dx;
				bounds.height -= dy;
				if(isSquare()) {
					bounds.width = bounds.height;
				}
				break;

			case SE:
				bounds.width += dx;
				bounds.height += dy;
				if(isSquare()) {
					bounds.width = bounds.height = Math.max(bounds.width, bounds.height);
				}
				break;

			case SW:
				bounds.x += dx;
				bounds.width -= dx;
				bounds.height += dy;
				if(isSquare()) {
					bounds.height = bounds.width;
				}
				break;

			}

			setBounds(bounds);
			fireDragChangeEvent();
		};

		private void updateMode(MouseEvent event) {
			int x = event.getX();
			int y = event.getY();

			mode = DragMode.MOVE;
			if(event.getButton() == 2 || !resizable) {
				return;
			}

			boolean isLeft = (x <= quadSize);
			boolean isRight = (x >= getWidth() - quadSize - 1);
			boolean isTop = (y <= quadSize);
			boolean isBottom = (y >= getHeight() - quadSize - 1);

			if((event.getModifiers() & MouseEvent.CTRL_MASK) != 0 || event.getButton() == MouseEvent.BUTTON3) {
				isLeft = (x <= getWidth() / 2);
				isRight = !isLeft;
				isTop = (y <= getHeight() / 2);
				isBottom = !isTop;
			}

			if(isLeft) {
				if(isTop) {
					mode = DragMode.NW;
				}
				if(isBottom) {
					mode = DragMode.SW;
				}
			}
			if(isRight) {
				if(isTop) {
					mode = DragMode.NE;
				}
				if(isBottom) {
					mode = DragMode.SE;
				}
			}
		}

		@Override
		public void mouseReleased(MouseEvent e) {
			start = null;
			fireChangeEvent();
		};
	};

	abstract protected void paintShape(Graphics2D gra);

	public void addDragChangeListener(ChangeListener changeListener) {
		dragListeners.add(changeListener);
	}

	public void removeDragChangeListener(ChangeListener changeListener) {
		dragListeners.remove(changeListener);
	}
}
