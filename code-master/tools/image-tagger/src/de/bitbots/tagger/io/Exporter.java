package de.bitbots.tagger.io;

import java.awt.Point;
import java.awt.Rectangle;
import java.io.File;
import java.io.FileWriter;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import de.bitbots.tagger.gui.ImageInfoModel;

public class Exporter {
	private DataStore store;

	public Exporter(DataStore store) {
		this.store = store;
	}

	public void export(File target) throws Exception {
		JSONArray array = export();
		FileWriter output = new FileWriter(target);
		try {
			array.write(output);
		} finally {
			try {
				output.close();
			} catch (Exception e) {
				// ignore
			}
		}
	}

	private JSONArray export() throws JSONException {
		JSONArray array = new JSONArray();
		for(ImageInfoModel info : store.getImageInfoModels()) {
			array.put(exportImageInfo(info));
		}
		return array;
	}

	private JSONObject exportImageInfo(ImageInfoModel info) throws JSONException {
		JSONObject obj = new JSONObject();
		obj.put("file", info.getImageFile());
		if(info.isBallVisible()) {
			obj.put(
				"ball",
				new JSONObject().put("x", info.getBallCenter().x).put("y", info.getBallCenter().y)
					.put("radius", info.getBallRadius()).put("entirely-visible", info.isBallEntirelyVisible()));
		}

		if(info.isCyanTeamMarkerVisible()) {
			obj.put("cyan-team-marker", exportRectangle(info.getCyanTeamMarkerRectangle()));
		}

		if(info.isMagentaTeamMarkerVisible()) {
			obj.put("magenta-team-marker", exportRectangle(info.getMagentaTeamMarkerRectangle()));
		}

		if(info.isYellowGoalLeftVisible()) {
			obj.put("yellow-goal-left", exportRectangle(info.getYellowGoalLeftRectangle()));
		}

		if(info.isYellowGoalRightVisible()) {
			obj.put("yellow-goal-right", exportRectangle(info.getYellowGoalRightRectangle()));
		}

		if(info.isCarpetVisible()) {
			obj.put("carpet", exportRectangle(info.getCarpetRectangle()));
		}

		if(info.hasFloorPlanePoints()) {
			for(Point point : info.getFloorPlanePoints()) {
				obj.accumulate("floor", new JSONObject(point, new String[] { "x", "y" }));
			}
		}

		if(info.hasLinePoints()) {
			for(Point point : info.getLinePoints()) {
				obj.accumulate("field-line", new JSONObject(point, new String[] { "x", "y" }));
			}
		}

		return obj;
	}

	private JSONObject exportRectangle(Rectangle rect) {
		return new JSONObject(rect, new String[] { "x", "y", "width", "height" });
	}
}
