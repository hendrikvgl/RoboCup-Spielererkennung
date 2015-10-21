package de.bitbots.tagger.startup;

import java.io.File;

import javax.swing.SwingUtilities;
import javax.swing.UIManager;

import de.bitbots.tagger.gui.MainWindow;

public class Startup {
    static private void setSystemLookAndFeel() {
        String[] lafs = { "com.sun.java.swing.plaf.gtk.GTKLookAndFeel",
            "com.sun.java.swing.plaf.windows.WindowsLookAndFeel", UIManager.getSystemLookAndFeelClassName() };
        for(String laf : lafs) {
            try {
                UIManager.setLookAndFeel(laf);
                return;
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    static public void main(final String[] args) throws Exception {
        try {
            setSystemLookAndFeel();

            SwingUtilities.invokeLater(new Runnable() {
                @Override
                public void run() {
                    MainWindow win;

                    int width = 1280;
                    int height = 720;
                    if(args.length > 0) {
                        int begin = 0;
                        if(args[0].startsWith("--size=")) {
                            String s = args[0].replace("--size=", "");
                            String[] wn = s.split("x");
                            width = Integer.valueOf(wn[0]);
                            height = Integer.valueOf(wn[1]);
                        }
                        win = new MainWindow(width, height);
                        win.setVisible(true);
                        win.setImageDirectory(new File(args[1]), width, height);
                    } else {
                        win = new MainWindow(width, height);
                        win.setVisible(true);
                        win.doShowDirectoryChooser();
                    }
                }
            });
        } catch(Exception e) {
            System.out.println("An error occured, maybe you use a wrong image size. Specify you image resolution giving for e.g --size=800x600 as first parameter");
            throw e;
        }
    }
}
