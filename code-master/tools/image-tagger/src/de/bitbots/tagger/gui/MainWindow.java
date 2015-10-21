
package de.bitbots.tagger.gui;


import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.io.File;

import javax.swing.BorderFactory;
import javax.swing.DefaultListModel;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JList;
import javax.swing.JOptionPane;
import javax.swing.JScrollPane;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

import de.bitbots.tagger.gui.box.Box;
import de.bitbots.tagger.gui.box.HBox;
import de.bitbots.tagger.gui.box.VBox;
import de.bitbots.tagger.io.AsyncImageReaderTask;
import de.bitbots.tagger.io.DataStore;
import de.bitbots.tagger.io.ImageProvider;


public class MainWindow extends JFrame {

	private static final long serialVersionUID = 1L;
	protected static final String TITLE = "Bit-Bots Image Tagger";
	protected JList imageListView;
	protected ImageView imageView;
	protected File currentImageFile;
	protected JCheckBox optBallVisible;
	protected JCheckBox optBallEntirelyVisible;
	protected JCheckBox optCyanTeamMarkerVisible;
	protected JCheckBox optMagentaTeamMarkerVisible;
	protected JCheckBox optYellowGoalLeftVisible;
	protected JCheckBox optYellowGoalRightVisible;

	protected ImageInfoModel lastModel, model;
	private DataStore dataStore;
	private JCheckBox optCarpetVisible;
	private JCheckBox optFloorPlaneVisible;
	private DeactivateOnlyCheckBox optLineVisible;
	private FileListCellRenderer renderer;


	public MainWindow(int width, int height) {
		setTitle(TITLE);
		setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);
		addWindowListener(new WindowAdapter() {

			@Override
			public void windowClosing(WindowEvent evt) {
				System.out.println("saveDataStore");
				if (!saveDataStore()) {
					System.out.println("Show joption");
					if (JOptionPane.showConfirmDialog(MainWindow.this,
					                                  "Exit the program anyways?",
					                                  "Couldn't save changes!",
					                                  JOptionPane.YES_NO_OPTION) == JOptionPane.YES_OPTION) {
						MainWindow.this.dispose();
						System.exit(1);
					}
				} else {
					MainWindow.this.dispose();
					System.exit(1);
				}
			}
		});

		setupUserInterface(width, height);

		// doShowDirectoryChooser();
		// setImageDirectory(new File("/home/olli/robocup/bilder/berlin-2"));
	}

	private void setupUserInterface(int width, int height) {
		HBox hbox = new HBox();
		hbox.setBorder(BorderFactory.createEmptyBorder(5, 5, 5, 5));

		setupImageListView(width, height);

		// Liste scrollbar machen
		JScrollPane scroll = new JScrollPane(imageListView);
		scroll.setPreferredSize(new Dimension(150, 0));
		hbox.add(scroll, true);

		// Anzeige des Bildes
		imageView = new ImageView(width, height);
		hbox.add(imageView, false);

		// Die Settings
		hbox.add(createOptionsPane());

		getContentPane().add(hbox, BorderLayout.CENTER);
		pack();
	}

	private Component createOptionsPane() {
		Box box = new VBox();

		optBallVisible = new DeactivateOnlyCheckBox("Ball ist sichtbar");
		optBallVisible.addActionListener(optActionListener);
		box.add(optBallVisible);

		optBallEntirelyVisible = new JCheckBox("Ball vollständig sichtbar");
		optBallEntirelyVisible.addActionListener(optActionListener);
		optBallEntirelyVisible.setMnemonic(KeyEvent.VK_E);
		box.add(optBallEntirelyVisible);

		optCyanTeamMarkerVisible = new DeactivateOnlyCheckBox("Cyan Team Marker");
		optCyanTeamMarkerVisible.addActionListener(optActionListener);
		box.add(optCyanTeamMarkerVisible);

		optMagentaTeamMarkerVisible = new DeactivateOnlyCheckBox("Magenta Team Marker");
		optMagentaTeamMarkerVisible.addActionListener(optActionListener);
		box.add(optMagentaTeamMarkerVisible);

		optYellowGoalLeftVisible = new DeactivateOnlyCheckBox("Linker gelber Torpfosten");
		optYellowGoalLeftVisible.addActionListener(optActionListener);
		box.add(optYellowGoalLeftVisible);

		optYellowGoalRightVisible = new DeactivateOnlyCheckBox("Rechter gelber Torpfosten");
		optYellowGoalRightVisible.addActionListener(optActionListener);
		box.add(optYellowGoalRightVisible);

		optCarpetVisible = new DeactivateOnlyCheckBox("Teppich sichtbar");
		optCarpetVisible.addActionListener(optActionListener);
		box.add(optCarpetVisible);

		optFloorPlaneVisible = new DeactivateOnlyCheckBox("Grundebene definierbar");
		optFloorPlaneVisible.addActionListener(optActionListener);
		box.add(optFloorPlaneVisible);

		optLineVisible = new DeactivateOnlyCheckBox("Feldlinien");
		optLineVisible.addActionListener(optActionListener);
		box.add(optLineVisible);

		box.addFiller();
		box.add(createButtonPane());
		return box;
	}

	private Component createButtonPane() {
		VBox box = new VBox();
		box.setSpacing(5);

		JButton button = new JButton("Info übernehmen");
		button.setMnemonic(KeyEvent.VK_U);
		button.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
				if (lastModel != null && model != null) {
					lastModel.copyTo(model);
				}
			}
		});
		box.add(button);

		button = new JButton("Voriges Bild");
		button.setMnemonic(KeyEvent.VK_V);
		button.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
				int idx = imageListView.getSelectedIndex() - 1;
				if (idx >= 0) {
					imageListView.setSelectedIndex(idx);
				}
			}
		});
		box.add(button);

		button = new JButton("Nächstes Bild");
		button.setMnemonic(KeyEvent.VK_N);
		button.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
				int idx = imageListView.getSelectedIndex() + 1;
				if (idx < imageListView.getModel().getSize()) {
					imageListView.setSelectedIndex(idx);
				}
				saveDataStore();
			}
		});
		box.add(button);

		button = new JButton("Speichern");
		button.setMnemonic(KeyEvent.VK_S);
		button.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
				saveDataStore();
			}
		});
		box.add(button);

		button = new JButton("Exportieren");
		button.setMnemonic(KeyEvent.VK_X);
		button.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
				try {
					dataStore.export();
				} catch (Exception err) {
					showErrorMessage(err);
				}
			}
		});
		box.add(button);

		button = new JButton("Neu laden");
		button.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
				if (JOptionPane.showConfirmDialog(MainWindow.this,
				                                  "Alle Änderungen gehen verloren!",
				                                  "Sicher?",
				                                  JOptionPane.YES_NO_OPTION) == JOptionPane.YES_OPTION) {
					reloadDataStore();
				}
			}
		});
		box.add(button);

		return box;
	}

	protected void reloadDataStore() {
		if (currentImageFile != null) {
			loadDataStore(currentImageFile.getParentFile());
		}
	}

	protected boolean saveDataStore() {
		boolean success;
		try {
			dataStore.save();
			setTitle(TITLE);
			success = true;
		} catch (Exception e) {
			showErrorMessage(e);
			success = false;
		}
		imageListView.repaint();
		return success;
	}

	private void setupImageListView(final int width, final int height) {
		// Liste mit den Dateinamen
		imageListView = new JList();
		renderer = new FileListCellRenderer();
		imageListView.setCellRenderer(renderer);

		imageListView.addListSelectionListener(new ListSelectionListener() {

			@Override
			public void valueChanged(ListSelectionEvent e) {
				setImageFile((File)imageListView.getSelectedValue(), width, height);
			}
		});
	}

	protected void setImageFile(File file, int width, int height) {
		if (file.equals(currentImageFile)) { return; }

		currentImageFile = file;
		imageListView.setSelectedValue(file, true);

		loadImage(file, width, height);
		updateImageInfoModel();
	}

	private void updateImageInfoModel() {
		if (currentImageFile == null) { return; }

		ImageInfoModel model = dataStore.getImageInfoModel(currentImageFile);
		setImageInfoModel(model);
	}

	private void setImageInfoModel(ImageInfoModel imageInfoModel) {
		if (model != null) {
			model.removeChangeListener(infoChangeListener);
			if (model.hasData()) {
				lastModel = model;
			}
		}

		model = imageInfoModel;
		model.addChangeListener(infoChangeListener);
		imageView.setImageInfoModel(model);
		model.notifyListeners(imageView.getImage());
	}

	private void loadImage(final File file, int width, int height) {
		setEnabled(false);
		imageView.setImage(null);

		new AsyncImageReaderTask(file, width, height) {

			@Override
			protected void done() {
				if (currentImageFile != file) { return; }

				setEnabled(true);

				if (getException() != null) {
					currentImageFile = null;
					showErrorMessage(getException());
					return;
				}

				imageView.setImage(getImage());
				pack();
			};
		}.execute();
	}

	protected void showErrorMessage(Exception exception) {
		JOptionPane.showMessageDialog(this, exception.getLocalizedMessage());
	}

	public void doShowDirectoryChooser() {
		JFileChooser chooser = new JFileChooser();
		chooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
		int retValue = chooser.showOpenDialog(this);
		if (retValue == JFileChooser.APPROVE_OPTION) {
			setImageDirectory(chooser.getSelectedFile(), 1280, 720);
		}
	}

	public void setImageDirectory(File directory, final int width, final int height) {
		imageListView.setModel(new DefaultListModel());
		loadDataStore(directory);

		new ImageProvider(directory) {

			@Override
			protected void done() {
				DefaultListModel model = new DefaultListModel();
				for (File file : getFileList()) {
					model.addElement(file);
				}

				imageListView.setModel(model);
				if (getFileList().size() > 0) {
					setImageFile(getFileList().get(0), width, height);
				}
			}
		}.execute();
	}

	private void loadDataStore(File directory) {
		File file = new File(directory, "DATA");
		if (!file.exists() || !file.isFile() || !file.canRead()) {
			setDataStore(new DataStore(file));
			setTitle(TITLE);
			return;
		}

		try {
			setDataStore(DataStore.load(file));
			setTitle(TITLE);
		} catch (Exception e) {
			showErrorMessage(e);
		}
	}

	private void setDataStore(DataStore dataStore) {
		this.dataStore = dataStore;
		renderer.setDataStore(dataStore);
		updateImageInfoModel();
	}


	private final ChangeListener infoChangeListener = new ChangeListener() {

		@Override
		public void stateChanged(ChangeEvent event) {
			optBallVisible.setSelected(model.isBallVisible());
			optBallEntirelyVisible.setSelected(model.isBallEntirelyVisible());
			optYellowGoalLeftVisible.setSelected(model.isYellowGoalLeftVisible());
			optYellowGoalRightVisible.setSelected(model.isYellowGoalRightVisible());
			optCyanTeamMarkerVisible.setSelected(model.isCyanTeamMarkerVisible());
			optMagentaTeamMarkerVisible.setSelected(model.isMagentaTeamMarkerVisible());
			optCarpetVisible.setSelected(model.isCarpetVisible());
			optFloorPlaneVisible.setSelected(model.hasFloorPlanePoints());
			optLineVisible.setSelected(model.hasLinePoints());

			optBallEntirelyVisible.setEnabled(model.isBallVisible());

			imageListView.repaint();
			if (!model.isDataSaved()) {
				setTitle("*" + TITLE);
			}
		}
	};

	ActionListener optActionListener = new ActionListener() {

		@Override
		public void actionPerformed(ActionEvent e) {
			model.setBallVisible(optBallVisible.isSelected());
			model.setBallEntirelyVisible(optBallEntirelyVisible.isSelected());
			model.setYellowGoalLeftVisible(optYellowGoalLeftVisible.isSelected());
			model.setYellowGoalRightVisible(optYellowGoalRightVisible.isSelected());
			model.setCyanTeamMarkerVisible(optCyanTeamMarkerVisible.isSelected());
			model.setMagentaTeamMarkerVisible(optMagentaTeamMarkerVisible.isSelected());

			if (!optCarpetVisible.isSelected()) {
				model.forgetCarpet();
			}

			if (!optFloorPlaneVisible.isSelected()) {
				model.forgetFloorPlanePoints();
			}

			if (!optLineVisible.isSelected()) {
				model.forgetLinePoints();
			}

			model.notifyListeners(imageView.getImage());
		}
	};

}
