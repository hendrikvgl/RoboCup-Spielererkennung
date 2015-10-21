# -*- coding:utf-8 -*-
from collections import namedtuple

from panda3d.core import GeomVertexWriter, GeomVertexData, GeomVertexFormat, Geom, GeomTriangles, GeomNode

GeomResult = namedtuple("GeomResult", ["geom", "center", "volume"])

class GeomGenerator(object):

    @staticmethod
    def volume_for_cube(points):
        px = [e[0] for e in points]
        py = [e[1] for e in points]
        pz = [e[2] for e in points]
        minx = min(px)
        miny = min(py)
        minz = min(pz)

        maxx = max(px)
        maxy = max(py)
        maxz = max(pz)

        dx = maxx - minx
        dy = maxy - miny
        dz = maxz - minz

        return dx*dy*dz


    @staticmethod
    def get_foot_geom():
        #Format
        format = GeomVertexFormat.getV3n3cpt2()
        #VertexData
        vdata = GeomVertexData('name', format, Geom.UHDynamic)
        ##VertexWriter
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        texcoord = GeomVertexWriter(vdata, 'texcoord')

        Ax, Ay = (-10, -10)
        Bx, By = (10, -10)
        Cx, Cy = (0, 20)
        z0, z1 = -1, 1

        points = [
            (Ax, Ay, z0),
            (Bx, By, z0),
            (Cx, Cy, z0),
            (Ax, Ay, z1),
            (Bx, By, z1),
            (Cx, Cy, z1)
        ]

        for p in points:
            vertex.addData3f(*p)

        color.addData4f(1, 1, 1, 1)
        color.addData4f(1, 1, 1, 1)
        color.addData4f(1, 1, 1, 1)
        color.addData4f(1, 0, 1, 1)
        color.addData4f(1, 0, 1, 1)
        color.addData4f(1, 0, 1, 1)

        normal.addData3f(0, 0, -1)
        normal.addData3f(0, 0, -1)
        normal.addData3f(0, 0, -1)

        normal.addData3f(0, 0, 1)
        normal.addData3f(0, 0, 1)
        normal.addData3f(0, 0, 1)

        ### Create Geom
        geom = Geom(vdata)
        ### Create Primitives
        prim = GeomTriangles(Geom.UHStatic)
        for i in range(6):
            for k in range(6):
                for t in range(6):
                    prim.addVertices(i, k, t)
        prim.closePrimitive()

        geom.addPrimitive(prim)

        node = GeomNode('gnode')
        node.addGeom(geom)

        xc = sum(x for (x, y, z) in points) / float(len(points))
        yc = sum(y for (x, y, z) in points) / float(len(points))
        zc = sum(z for (x, y, z) in points) / float(len(points))

        Ax, Ay = points[0][0:2]
        Bx, By = points[1][0:2]
        Cx, Cy = points[2][0:2]

        volume = abs(Ax * (By-Cy) + Bx*(Cy -Ay) + Cx * (Ay -By) / 2)

        return GeomResult(node, (xc, yc, zc), volume)


    @staticmethod
    def create_box():
        #Format
        format = GeomVertexFormat.getV3n3cpt2()
        #VertexData
        vdata = GeomVertexData('name', format, Geom.UHDynamic)


        ##VertexWriter
        vertex      = GeomVertexWriter(vdata, 'vertex')
        normal      = GeomVertexWriter(vdata, 'normal')
        color       = GeomVertexWriter(vdata, 'color')
        texcoord    = GeomVertexWriter(vdata, 'texcoord')

        points = [
            (-1, -1, -1),
            (-1, 1, -1),
            (1, -1, -1),
            (1, 1, -1),
            (-1, -1, 1),
            (-1, 1, 1),
            (1, -1, 1),
            (1, 1, 1)
        ]

        for p in points:
            vertex.addData3f(*p)

        color.addData4f(1, 1, 1, 1)
        color.addData4f(1, 1, 1, 1)
        color.addData4f(1, 1, 1, 1)
        color.addData4f(1, 1, 1, 1)
        color.addData4f(1, 1, 1, 1)
        color.addData4f(1, 1, 1, 1)
        color.addData4f(1, 1, 1, 1)
        color.addData4f(1, 1, 1, 1)

        normal.addData3f(0, 0, 1)
        normal.addData3f(0, 0, 1)
        normal.addData3f(0, 0, 1)
        normal.addData3f(0, 0, 1)
        normal.addData3f(0, 0, 1)
        normal.addData3f(0, 0, 1)
        normal.addData3f(0, 0, 1)
        normal.addData3f(0, 0, 1)

        ### Create Geom
        geom = Geom(vdata)
        ### Create Primitives
        prim = GeomTriangles(Geom.UHStatic)
        prim.addVertices(0, 1, 2)
        prim.addVertices(2, 1, 3)

        prim.addVertices(4, 5, 6)
        prim.addVertices(4, 6, 7)

        for i in range(8):
            for k in range(8):
                for t in range(8):
                    prim.addVertices(i, k, t)

        prim.closePrimitive()

        geom.addPrimitive(prim)

        node = GeomNode('gnode')
        node.addGeom(geom)

        xc = sum(x for (x, y, z) in points) / float(len(points))
        yc = sum(y for (x, y, z) in points) / float(len(points))
        zc = sum(z for (x, y, z) in points) / float(len(points))

        return GeomResult(node, (xc, yc, zc), GeomGenerator.volume_for_cube(points))
