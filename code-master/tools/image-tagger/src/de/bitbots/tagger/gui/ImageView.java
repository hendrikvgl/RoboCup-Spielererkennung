
package de.bitbots.tagger.gui;


import java.awt.Color;
import java.awt.Dimension;
import java.awt.Graphics;
import java.awt.GraphicsConfiguration;
import java.awt.GraphicsDevice;
import java.awt.GraphicsEnvironment;
import java.awt.Image;
import java.awt.Point;
import java.awt.Rectangle;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.List;

import javax.swing.JMenuItem;
import javax.swing.JPanel;
import javax.swing.JPopupMenu;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;

import de.bitbots.tagger.gui.shapes.CircleShapeComponent;
import de.bitbots.tagger.gui.shapes.Polygon;
import de.bitbots.tagger.gui.shapes.RectangleShapeComponent;
import de.bitbots.tagger.gui.shapes.ShapeComponent;


public class ImageView extends JPanel {

	private static final long serialVersionUID = 1L;

	private Image image;
	protected ImageInfoModel model;

	protected ShapeComponent ball;
	protected ShapeComponent carpet;
	protected ShapeComponent yellowGoalLeft;
	protected ShapeComponent yellowGoalRight;
	protected ShapeComponent cyanTeamMarker;
	protected ShapeComponent magentaTeamMarker;

	private ShapeComponent[] carpetPoints;

	private Polygon linePoints;


	public ImageView(int width, int height) {
		setLayout(null);

		setupShapeComponents(width, height);
		setupPopupMenuListener();
	}

	private void setupShapeComponents(int width, int height) {
		setupBallComponent();
		setupGoalComponents();
		setupFieldComponents(width, height);
		setupTeamMarkerComponent();
	}

	private void setupFieldComponents(int width, int height) {
		carpet = new RectangleShapeComponent();
		carpet.setForeground(Color.GREEN);
		carpet.addChangeListener(imageChangeListener);
		carpet.setBounds(20, 100, 32, 32);
		carpet.setVisible(false);
		add(carpet);

		carpetPoints = new ShapeComponent[3];
		for (int i = 0; i < 3; i++) {
			carpetPoints[i] = new RectangleShapeComponent();
			carpetPoints[i].addChangeListener(imageChangeListener);
			carpetPoints[i].setForeground(Color.PINK);
			carpetPoints[i].setVisible(false);
			carpetPoints[i].setSize(8, 8);
			carpetPoints[i].setResizable(false);

			carpetPoints[i].addDragChangeListener(new ChangeListener() {

				@Override
				public void stateChanged(ChangeEvent e) {
					repaint();
				}
			});

			add(carpetPoints[i]);
		}

		linePoints = new Polygon(4);
		linePoints.setBounds(0, 0, width, height);
		linePoints.setVisible(false);
		linePoints.setChangeListener(imageChangeListener);
		add(linePoints);
	}

	private void setupBallComponent() {
		ball = new CircleShapeComponent();
		ball.setBounds(20, 20, 32, 32);
		ball.setForeground(Color.RED);
		ball.addChangeListener(imageChangeListener);
		ball.setSquare(true);
		ball.setVisible(false);
		add(ball);
	}

    private void setupTeamMarkerComponent() {
		cyanTeamMarker = new RectangleShapeComponent();
		magentaTeamMarker = new RectangleShapeComponent();

        cyanTeamMarker.setBounds(100 + 200, 20, 32, 24);
        cyanTeamMarker.setForeground(Color.CYAN);
        cyanTeamMarker.addChangeListener(imageChangeListener);
        cyanTeamMarker.setVisible(false);
        add(cyanTeamMarker);

        magentaTeamMarker.setBounds(100 + 200, 20, 32, 24);
        magentaTeamMarker.setForeground(Color.MAGENTA);
        magentaTeamMarker.addChangeListener(imageChangeListener);
        magentaTeamMarker.setVisible(false);
        add(magentaTeamMarker);
    }

	private void setupGoalComponents() {
		yellowGoalLeft = new RectangleShapeComponent();
		yellowGoalRight = new RectangleShapeComponent();

		ShapeComponent[] posts = {
		        yellowGoalLeft,
		        yellowGoalRight
		};
		Color color[] = {
		        Color.YELLOW,
		        Color.YELLOW
		};

		for (int i = 0; i < posts.length; i++) {
			ShapeComponent post = posts[i];
			post.setBounds(100 + 100 * i, 20, 32, 24);
			post.setForeground(color[i]);
			post.addChangeListener(imageChangeListener);
			post.setVisible(false);
			add(post);
		}
	}

	private void setupPopupMenuListener() {
		addMouseListener(new MouseAdapter() {

			@Override
			public void mousePressed(final MouseEvent e) {
				if (!e.isPopupTrigger()) { return; }

				JPopupMenu popup = new JPopupMenu();
				JMenuItem item;
				if (!model.isBallVisible()) {
					item = popup.add("Ball");
					item.setForeground(Color.RED);
					item.addActionListener(new ActionListener() {

						@Override
						public void actionPerformed(ActionEvent arg0) {
							model.setBallCenter(new Point(e.getX(), e.getY()));
							model.setBallRadius(32);
							model.setBallVisible(true);
							model.setBallEntirelyVisible(true);
							model.notifyListeners(image);
						}
					});
				}

				if (!model.isYellowGoalLeftVisible()) {
					item = popup.add("Linker gelber Pfosten");
					item.setForeground(Color.YELLOW);
					item.addActionListener(new ActionListener() {

						@Override
						public void actionPerformed(ActionEvent arg0) {
							model.setYellowGoalLeftRectangle(new Rectangle(e.getX() - 32,
							                                               e.getY() - 32,
							                                               64,
							                                               64));
							model.setYellowGoalLeftVisible(true);
							model.notifyListeners(image);
						}
					});
				}

				if (!model.isYellowGoalRightVisible()) {
					item = popup.add("Rechter gelber Pfosten");
					item.setForeground(Color.YELLOW);
					item.addActionListener(new ActionListener() {

						@Override
						public void actionPerformed(ActionEvent arg0) {
							model.setYellowGoalRightRectangle(new Rectangle(e.getX() - 32,
							                                                e.getY() - 32,
							                                                64,
							                                                64));
							model.setYellowGoalRightVisible(true);
							model.notifyListeners(image);
						}
					});
				}

				if (!model.isCyanTeamMarkerVisible()) {
					item = popup.add("Cyan Team Marker");
					item.setForeground(Color.CYAN);
					item.addActionListener(new ActionListener() {

						@Override
						public void actionPerformed(ActionEvent arg0) {
							model.setCyanTeamMarkerRectangle(new Rectangle(e.getX() - 32,
							                                             e.getY() - 32,
							                                             64,
							                                             64));
							model.setCyanTeamMarkerVisible(true);
							model.notifyListeners(image);
						}
					});
				}

				if (!model.isMagentaTeamMarkerVisible()) {
					item = popup.add("Magenta Team Marker");
					item.setForeground(Color.MAGENTA);
					item.addActionListener(new ActionListener() {

						@Override
						public void actionPerformed(ActionEvent arg0) {
							model.setMagentaTeamMarkerRectabgle(new Rectangle(e.getX() - 32,
							                                              e.getY() - 32,
							                                              64,
							                                              64));
							model.setMagentaTeamMarkerVisible(true);
							model.notifyListeners(image);
						}
					});
				}

				if (model.getCarpetRectangle() == null) {
					item = popup.add("Teppich");
					item.setForeground(Color.GREEN);

					item.addActionListener(new ActionListener() {

						@Override
						public void actionPerformed(ActionEvent arg0) {
							model.setCarpetRectangle(new Rectangle(e.getX() - 32,
							                                       e.getY() - 32,
							                                       64,
							                                       64));
							model.notifyListeners(image);
						}
					});
				}

				if (model.getFloorPlanePoints() == null) {
					item = popup.add("Bodenpunkte");
					item.setForeground(Color.PINK);
					item.addActionListener(new ActionListener() {

						@Override
						public void actionPerformed(ActionEvent arg0) {
							int x = e.getX();
							int y = e.getY();
							model.setFloorPlanePoints(new Point(x - 20, y),
							                          new Point(x, y),
							                          new Point(x + 20, y));
							model.notifyListeners(image);
						}
					});
				}

				if (model.getLinePoints() == null) {
					item = popup.add("Feldlinie");
					item.setForeground(new Color(255, 0, 255));
					item.addActionListener(new ActionListener() {

						@Override
						public void actionPerformed(ActionEvent arg0) {
							int x = e.getX();
							int y = e.getY();
							model.setLinePoints(new Point(x - 20, y + 20),
							                    new Point(x + 20, y + 20),
							                    new Point(x + 20, y - 20),
							                    new Point(x - 20, y - 20));
							model.notifyListeners(image);
						}
					});
				}

				popup.show(e.getComponent(), e.getX(), e.getY());
			}
		});
	}

	@Override
	protected void paintComponent(Graphics g) {
		if (image == null) { return; }

		g.drawImage(image, 0, 0, getWidth(), getHeight(), null);
		if (carpetPoints[0].isVisible()) {
			Point a = carpetPoints[0].getCenter();
			Point b = carpetPoints[1].getCenter();
			Point c = carpetPoints[2].getCenter();

			g.setColor(Color.PINK);
			g.drawLine(a.x, a.y, b.x, b.y);
			g.drawLine(c.x, c.y, b.x, b.y);
		}
	}

	public void setImage(Image image) {
		if (image != null) {
			if (this.image == null || this.image.getWidth(null) != image.getWidth(null)
			    || this.image.getHeight(null) != image.getHeight(null)) {
				GraphicsEnvironment ge = GraphicsEnvironment.getLocalGraphicsEnvironment();
				GraphicsDevice gd = ge.getDefaultScreenDevice();
				GraphicsConfiguration gc = gd.getDefaultConfiguration();

				this.image = gc.createCompatibleImage(image.getWidth(null), image.getHeight(null));
			}

			this.image.getGraphics().drawImage(image, 0, 0, null);

			Dimension size = new Dimension(image.getWidth(null), image.getHeight(null));
			if (!size.equals(getPreferredSize())) {
				setPreferredSize(size);
			}
		} else {
			this.image = null;
		}

		revalidate();
		repaint();
	}

	public void setImageInfoModel(ImageInfoModel model) {
		if (this.model != null) {
			this.model.removeChangeListener(infoChangeListener);
		}

		this.model = model;
		this.model.addChangeListener(infoChangeListener);
		this.model.notifyListeners(image);
	}


	private final ChangeListener imageChangeListener = new ChangeListener() {

		@Override
		public void stateChanged(ChangeEvent e) {
			model.setBallCenter(ball.getCenter());
			model.setBallRadius(ball.getWidth() / 2);

			model.setYellowGoalLeftRectangle(yellowGoalLeft.getBounds());
			model.setYellowGoalRightRectangle(yellowGoalRight.getBounds());
			model.setCyanTeamMarkerRectangle(cyanTeamMarker.getBounds());
			model.setMagentaTeamMarkerRectabgle(magentaTeamMarker.getBounds());

			if (carpet.isVisible()) {
				model.setCarpetRectangle(carpet.getBounds());
			}

			if (carpetPoints[0].isVisible()) {
				model.setFloorPlanePoints(carpetPoints[0].getCenter(),
				                          carpetPoints[1].getCenter(),
				                          carpetPoints[2].getCenter());
			}

			if (model.hasLinePoints()) {
				model.setLinePoints(linePoints.getCenterPoints());
			}

			model.notifyListeners(image);
		}
	};

	private final ChangeListener infoChangeListener = new ChangeListener() {

		@Override
		public void stateChanged(ChangeEvent event) {
			// Gelbes Tor
			yellowGoalLeft.setVisible(model.isYellowGoalLeftVisible());
			if (model.getYellowGoalLeftRectangle() != null) {
				yellowGoalLeft.setBounds(model.getYellowGoalLeftRectangle());
			}

			yellowGoalRight.setVisible(model.isYellowGoalRightVisible());
			if (model.getYellowGoalRightRectangle() != null) {
				yellowGoalRight.setBounds(model.getYellowGoalRightRectangle());
			}

			// Cyan Team Marker
			cyanTeamMarker.setVisible(model.isCyanTeamMarkerVisible());
			if (model.getCyanTeamMarkerRectangle() != null) {
				cyanTeamMarker.setBounds(model.getCyanTeamMarkerRectangle());
			}

            // Magenta Team Marker
			magentaTeamMarker.setVisible(model.isMagentaTeamMarkerVisible());
			if (model.getMagentaTeamMarkerRectangle() != null) {
				magentaTeamMarker.setBounds(model.getMagentaTeamMarkerRectangle());
			}

			// Ball
			ball.setVisible(model.isBallVisible());
			if (model.getBallCenter() != null) {
				ball.setSize(model.getBallRadius() * 2, model.getBallRadius() * 2);
				ball.setCenter(model.getBallCenter().x, model.getBallCenter().y);
			}

			// Teppich
			carpet.setVisible(model.isCarpetVisible());
			if (model.getCarpetRectangle() != null) {
				carpet.setBounds(model.getCarpetRectangle());
			}

			List<Point> points = model.getFloorPlanePoints();
			for (int i = 0; i < 3; i++) {
				if (model.hasFloorPlanePoints()) {
					carpetPoints[i].setVisible(true);
					carpetPoints[i].setCenter(points.get(i).x, points.get(i).y);
				} else {
					carpetPoints[i].setVisible(false);
				}
			}

			linePoints.setVisible(model.hasLinePoints());
			if (model.hasLinePoints()) {
				linePoints.setCenterPoints(model.getLinePoints());
			}
		}
	};


	public Image getImage() {
		return image;
	}
}
