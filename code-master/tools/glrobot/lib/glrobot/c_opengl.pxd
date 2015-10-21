cdef extern from "GL/gl.h":
    int GL_STATIC_DRAW
    int GL_DYNAMIC_DRAW
    
    int GL_ARRAY_BUFFER
    int GL_ELEMENT_ARRAY_BUFFER
    
    int GL_VERTEX_ARRAY
    int GL_NORMAL_ARRAY
    int GL_TEXTURE_COORD_ARRAY
    
    int GL_TEXTURE_2D
    
    int GL_POINTS
    int GL_LINE_STRIP
    int GL_TRIANGLES
    
    int GL_FLOAT
    int GL_UNSIGNED_SHORT
    
    void glPushMatrix()
    void glPopMatrix()
    
    void glRotatef(float, int, int, int)
    void glTranslatef(float, float, float)
    void glScalef(float, float, float)
    void glMultMatrixf(float*)

    void glGenBuffers(int, int*)
    void glDeleteBuffers(int, int*)
    void glBindBuffer(int, int)
    void glBufferData(int, int, char*, int)
    
    void glEnable(int)
    void glDisable(int)
    void glColor4f(float, float, float, float)
    
    void glEnableClientState(int)
    void glDisableClientState(int)
    
    void glVertexPointer(int, int, int, void*)
    void glTexCoordPointer(int, int, int, void*)
    void glNormalPointer(int, int, void*)
    
    void glDrawArrays(int, int, int)
    void glDrawElements(int, int, int, void*)
    
    int GL_UNPACK_ALIGNMENT
    int GL_TEXTURE_WRAP_S
    int GL_TEXTURE_WRAP_T
    int GL_TEXTURE_MIN_FILTER
    int GL_TEXTURE_MAG_FILTER
    int GL_CLAMP
    int GL_LINEAR
    int GL_NEAREST
    int GL_RGB
    int GL_RGBA
    int GL_UNSIGNED_BYTE
    
    void glGenTextures(int, int*)
    void glDeleteTextures(int, int*)
    void glBindTexture(int, int)
    void glTexImage2D(int, int, int, int, int, int, int, int, char*)
    void glPixelStorei(int, int)
    void glTexParameteri(int, int, int)
    
