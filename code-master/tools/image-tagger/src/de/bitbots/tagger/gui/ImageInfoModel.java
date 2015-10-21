
package de.bitbots.tagger.gui;


import java.awt.Image;
import java.awt.Point;
import java.awt.Rectangle;
import java.io.File;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;

import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;


public class ImageInfoModel implements Serializable {

	private static final long serialVersionUID = 1L;

	private transient Collection<ChangeListener> listeners;

	private final File image;

	// Infos zum Ball
	private boolean ballVisible;
	private boolean ballEntirelyVisible;
	private Point ballCenter;
	private int ballRadius;

	private boolean yellowGoalLeftVisible;
	private Rectangle yellowGoalLeftRectangle;

	private boolean yellowGoalRightVisible;
	private Rectangle yellowGoalRightRectangle;

	private boolean cyanTeamMarkerVisible;
	private Rectangle cyanTeamMarkerRectangle;

	private boolean magentaTeamMarkerVisible;
	private Rectangle magentaTeamMarkerRectangle;

	private Rectangle carpetRectangle;

	private List<Point> floorPlanePoints;
	private List<Point> linePoints;

	private boolean dataSaved;

	private boolean invalidCoordinates;


	public ImageInfoModel(File image) {
		listeners = new ArrayList<ChangeListener>();
		this.image = image;
		dataSaved = true;
		invalidCoordinates = false;
	}

	public void addChangeListener(ChangeListener li) {
		listeners.add(li);
	}

	public void removeChangeListener(ChangeListener li) {
		listeners.remove(li);
	}

	public File getImageFile() {
		return image;
	}

	public void setBallVisible(boolean visible) {
		ballVisible = visible;
		dataSaved = false;
	}

	public boolean isBallVisible() {
		return ballVisible;
	}

	public boolean isBallEntirelyVisible() {
		return ballEntirelyVisible;
	}

	public void setBallEntirelyVisible(boolean ballEntirelyVisible) {
		this.ballEntirelyVisible = ballEntirelyVisible;
		dataSaved = false;
	}

	public boolean isYellowGoalLeftVisible() {
		return yellowGoalLeftVisible;
	}

	public void setYellowGoalLeftVisible(boolean yellowGoalLeftVisible) {
		this.yellowGoalLeftVisible = yellowGoalLeftVisible;
		dataSaved = false;
	}

	public boolean isYellowGoalRightVisible() {
		return yellowGoalRightVisible;
	}

	public void setYellowGoalRightVisible(boolean yellowGoalRightVisible) {
		this.yellowGoalRightVisible = yellowGoalRightVisible;
		dataSaved = false;
	}

	public boolean isCyanTeamMarkerVisible() {
		return cyanTeamMarkerVisible;
	}

	public void setCyanTeamMarkerVisible(boolean cyanTeamMarkerVisible) {
		this.cyanTeamMarkerVisible = cyanTeamMarkerVisible;
		dataSaved = false;
	}

	public boolean isMagentaTeamMarkerVisible() {
		return magentaTeamMarkerVisible;
	}

	public void setMagentaTeamMarkerVisible(boolean magentaTeamMarkerVisible) {
		this.magentaTeamMarkerVisible = magentaTeamMarkerVisible;
		dataSaved = false;
	}

	public Point getBallCenter() {
		return ballCenter;
	}

	public void setBallCenter(Point ballCenter) {
		this.ballCenter = ballCenter;
		dataSaved = false;
	}

	public int getBallRadius() {
		return ballRadius;
	}

	public void setBallRadius(int ballRadius) {
		this.ballRadius = ballRadius;
		dataSaved = false;
	}

	public Rectangle getYellowGoalLeftRectangle() {
		return yellowGoalLeftRectangle;
	}

	public void setYellowGoalLeftRectangle(Rectangle yellowGoalLeftRectangle) {
		this.yellowGoalLeftRectangle = yellowGoalLeftRectangle;
		dataSaved = false;
	}

	public Rectangle getYellowGoalRightRectangle() {
		return yellowGoalRightRectangle;
	}

	public void setYellowGoalRightRectangle(Rectangle yellowGoalRightRectangle) {
		this.yellowGoalRightRectangle = yellowGoalRightRectangle;
		dataSaved = false;
	}

	public Rectangle getCyanTeamMarkerRectangle() {
		return cyanTeamMarkerRectangle;
	}

	public void setCyanTeamMarkerRectangle(Rectangle cyanTeamMarkerRectangle) {
		this.cyanTeamMarkerRectangle = cyanTeamMarkerRectangle;
		dataSaved = false;
	}

	public Rectangle getMagentaTeamMarkerRectangle() {
		return magentaTeamMarkerRectangle;
	}

	public void setMagentaTeamMarkerRectabgle(Rectangle magentaTeamMarkerRectangle) {
		this.magentaTeamMarkerRectangle = magentaTeamMarkerRectangle;
		dataSaved = false;
	}

	public void forgetCarpet() {
		carpetRectangle = null;
		dataSaved = false;
	}

	public boolean isCarpetVisible() {
		return carpetRectangle != null;
	}

	public void setCarpetRectangle(Rectangle rectangle) {
		carpetRectangle = rectangle;
		dataSaved = false;
	}

	public Rectangle getCarpetRectangle() {
		return carpetRectangle;
	}

	public void forgetFloorPlanePoints() {
		floorPlanePoints = null;
		dataSaved = false;
	}

	public void setFloorPlanePoints(Point a, Point b, Point c) {
		floorPlanePoints = Arrays.asList(a, b, c);
		dataSaved = false;
	}

	public List<Point> getFloorPlanePoints() {
		return floorPlanePoints;
	}

	public boolean hasFloorPlanePoints() {
		return floorPlanePoints != null;
	}

	public void forgetLinePoints() {
		linePoints = null;
		dataSaved = false;
	}

	public boolean hasLinePoints() {
		return linePoints != null;
	}

	public void setLinePoints(Point a, Point b, Point c, Point d) {
		linePoints = Arrays.asList(a, b, c, d);
		dataSaved = false;
	}

	public void setLinePoints(List<Point> points) {
		linePoints = new ArrayList<Point>(points);
		dataSaved = false;
	}

	public List<Point> getLinePoints() {
		return linePoints;
	}

	protected void fireChangeEvent() {
		ChangeEvent event = new ChangeEvent(this);
		for (ChangeListener li : listeners) {
			li.stateChanged(event);
		}
	}

	public void notifyListeners(Image img) {
		validate(img);
		fireChangeEvent();
	}

	private void validate(Image img) {
		if (ballCenter == null || !ballVisible) {
			ballVisible = false;
			ballEntirelyVisible = false;
		}

		if (yellowGoalLeftVisible && yellowGoalLeftRectangle == null) {
			yellowGoalLeftRectangle = new Rectangle(100, 20, 48, 48);
		}

		if (yellowGoalRightVisible && yellowGoalRightRectangle == null) {
			yellowGoalRightRectangle = new Rectangle(200, 20, 48, 48);
		}

		if (cyanTeamMarkerVisible && cyanTeamMarkerRectangle == null) {
			cyanTeamMarkerRectangle = new Rectangle(300, 20, 48, 48);
		}

		if (magentaTeamMarkerVisible && magentaTeamMarkerRectangle == null) {
			magentaTeamMarkerRectangle = new Rectangle(300, 20, 48, 48);
		}
		if (img != null) {
			invalidCoordinates = !checkCoordinates(img);
		}
	}

	private void readObject(ObjectInputStream in) throws IOException,
	                                             ClassNotFoundException {
		in.defaultReadObject();
		listeners = new ArrayList<ChangeListener>();
	}

	public void copyTo(ImageInfoModel model) {
		if (!model.ballVisible) {
			model.ballVisible = ballVisible;
			model.ballEntirelyVisible = ballEntirelyVisible;
			model.ballCenter = ballCenter;
			model.ballRadius = ballRadius;
		}
		if (!model.yellowGoalLeftVisible) {
			model.yellowGoalLeftVisible = yellowGoalLeftVisible;
			model.yellowGoalLeftRectangle = yellowGoalLeftRectangle;
		}
		if (!model.yellowGoalRightVisible) {
			model.yellowGoalRightVisible = yellowGoalRightVisible;
			model.yellowGoalRightRectangle = yellowGoalRightRectangle;
		}
		if (!model.cyanTeamMarkerVisible) {
			model.cyanTeamMarkerVisible = cyanTeamMarkerVisible;
			model.cyanTeamMarkerRectangle = cyanTeamMarkerRectangle;
		}
		if (!model.magentaTeamMarkerVisible) {
			model.magentaTeamMarkerVisible = magentaTeamMarkerVisible;
			model.magentaTeamMarkerRectangle = magentaTeamMarkerRectangle;
		}
		if (model.carpetRectangle == null) {
			model.carpetRectangle = carpetRectangle;
		}
		if (model.floorPlanePoints == null) {
			model.floorPlanePoints = floorPlanePoints;
		}
		if (model.linePoints == null) {
			model.linePoints = linePoints;
		}
		model.dataSaved = false;
		model.notifyListeners(null);
	}

	public boolean hasData() {
		if (ballVisible) { return true; }
		if (yellowGoalLeftVisible) { return true; }
		if (yellowGoalRightVisible) { return true; }
		if (cyanTeamMarkerVisible) { return true; }
		if (magentaTeamMarkerVisible) { return true; }
		if (carpetRectangle != null) { return true; }
		if (floorPlanePoints != null) { return true; }
		if (linePoints != null) { return true; }
		return false;
	}

	public boolean isDataSaved() {
		return dataSaved;
	}

	public void setDataSaved(boolean b) {
		dataSaved = b;
	}

	public boolean hasInvalidCoordinates() {
		return invalidCoordinates;
	}

	private boolean checkCoordinates(Image img) {
		if (ballVisible) {
			if (!isValid(img, new Rectangle(ballCenter.x - ballRadius,
			                                ballCenter.y - ballRadius,
			                                2 * ballRadius,
			                                2 * ballRadius))) { return false; }
		}
		if (yellowGoalLeftVisible) {
			if (!isValid(img, yellowGoalLeftRectangle)) { return false; }
		}
		if (yellowGoalRightVisible) {
			if (!isValid(img, yellowGoalRightRectangle)) { return false; }
		}
		if (cyanTeamMarkerVisible) {
			if (!isValid(img, cyanTeamMarkerRectangle)) { return false; }
		}
		if (magentaTeamMarkerVisible) {
			if (!isValid(img, magentaTeamMarkerRectangle)) { return false; }
		}
		if (carpetRectangle != null) {
			if (!isValid(img, carpetRectangle)) { return false; }
		}
		if (floorPlanePoints != null) {
			if (!isValid(img, floorPlanePoints)) { return false; }
		}
		if (linePoints != null) {
			if (!isValid(img, linePoints)) { return false; }
		}
		return true;
	}

	private boolean isValid(Image img, Rectangle rectangle) {
		if (img == null) return false;
		int w = img.getWidth(null);
		int h = img.getHeight(null);
		if (rectangle.x < 0 || rectangle.x >= w) { return false; }
		if (rectangle.y < 0 || rectangle.y >= h) { return false; }
		if (rectangle.x + rectangle.width < 0 || rectangle.x + rectangle.width >= w) { return false; }
		if (rectangle.y + rectangle.height < 0 || rectangle.y + rectangle.height >= h) { return false; }
		return true;
	}

	private boolean isValid(Image img, List<Point> points) {
		if (img == null) return false;
		int w = img.getWidth(null);
		int h = img.getHeight(null);
		for (Point point : points) {
			if (point.x < 0 || point.x >= w) { return false; }
			if (point.y < 0 || point.y >= h) { return false; }
		}
		return true;
	}
}
