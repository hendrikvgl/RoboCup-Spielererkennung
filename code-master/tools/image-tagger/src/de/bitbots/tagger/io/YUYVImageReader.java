package de.bitbots.tagger.io;

import java.awt.image.BufferedImage;
import java.io.IOException;
import java.io.InputStream;

public class YUYVImageReader {

    /**
     * Ließt ein Bild aus einem Stream
     */
    public static BufferedImage readColorImage(InputStream input, int width, int height) throws IOException {
        byte[] data = new byte[width * height * 2];

        int amount = data.length;
        while(amount > 0) {
            int len = input.read(data, data.length - amount, amount);
            if(len <= 0) {
                throw new IOException("Not enough data to Read.\nDid you specify your image resolution giving for e.g. --size=800x600 as first argument?");
            }

            amount -= len;
        }

        return readColorImage(data, width, height);
    }

    /**
     * Erzeugt ein Bild aus bytes. Das Bild wird dabei an der x-Achse gespiegelt
     * ausgelesen.
     */
    public static BufferedImage readBlackWhiteImage(byte[] data, int width, int height) {
        int[] gray = new int[width * height];
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                gray[y * width + x] = data[2 * ((height - y - 1) * width + x)];
            }
        }

        BufferedImage image = new BufferedImage(width, height, BufferedImage.TYPE_INT_ARGB);
        image.getRaster().setPixels(0, 0, width, height, gray);
        return image;
    }

    /**
     * Erzeugt ein Bild aus bytes. Das Bild wird dabei an der x-Achse gespiegelt
     * ausgelesen.
     */
    public static BufferedImage readColorImage(byte[] yuyv, int width, int height) {
        int[] rgb = new int[width * height];
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x += 2) {
                int offset = 2 * ((height - y - 1) * width + x);

                float U = (yuyv[offset + 1] & 0xff) - 128.f;
                float V = (yuyv[offset + 3] & 0xff) - 128.f;
                {
                    float Y = yuyv[offset] & 0xff;
                    int r = (int)(Y + 1.1773f * V);
                    int g = (int)(Y + 0.344f * U - 0.714f * V);
                    int b = (int)(Y + 1.403f * U);

                    rgb[width * y + x] =
                        0xff000000 | ((r < 0 ? 0 : (r > 255 ? 255 : r)) << 16)
                            | ((g < 0 ? 0 : (g > 255 ? 255 : g)) << 8)
                            | ((b < 0 ? 0 : (b > 255 ? 255 : b)) << 0);
                }

                {
                    float Y = yuyv[offset + 2] & 0xff;
                    int r = (int)(Y + 1.1773f * V);
                    int g = (int)(Y + 0.344f * U - 0.714f * V);
                    int b = (int)(Y + 1.403f * U);

                    rgb[width * y + x + 1] =
                        0xff000000 | ((r < 0 ? 0 : (r > 255 ? 255 : r)) << 16)
                            | ((g < 0 ? 0 : (g > 255 ? 255 : g)) << 8)
                            | ((b < 0 ? 0 : (b > 255 ? 255 : b)) << 0);
                }
            }
        }

        BufferedImage image = new BufferedImage(width, height, BufferedImage.TYPE_INT_ARGB);
        image.setRGB(0, 0, width, height, rgb, 0, width);
        return image;
    }
}
