#include "debug_paint.hpp"

using namespace Debug::Paint;

Color Debug::Paint::Black(0, 0, 0);
Color Debug::Paint::White(1, 1, 1);

Color Debug::Paint::Red(1, 0, 0);
Color Debug::Paint::Green(0, 1, 0);
Color Debug::Paint::Blue(0, 0, 1);
Color Debug::Paint::Pink(1, 0, 1);
Color Debug::Paint::Yellow(1, 1, 0);
Color Debug::Paint::Cyan(0, 1, 1);

template<typename T>
inline void fill_fixed_size_array(T* arr, T val) {
    arr[0] = val;
}

template<typename T,  typename... Values>
inline void fill_fixed_size_array(T* arr, T val, Values... args) {
    arr[0] = val;
    fill_fixed_size_array(arr + 1, args...);
}

Shape Debug::Paint::point(float x, float y, const Color& color) {
    Shape shape(ShapeType::s_point);
    float* values = new float[shape_type_to_num_of_components(s_point)];
    fill_fixed_size_array(values, x, y);
    shape.set_predefined_shape(values);
    shape.set_color_direct(color);
    return shape;
}

Shape Debug::Paint::dot(float x, float y, const Color& color) {
    Shape shape(ShapeType::s_dot);
    float* values = new float[shape_type_to_num_of_components(s_dot)];
    fill_fixed_size_array(values, x, y);
    shape.set_predefined_shape(values);
    shape.set_color_direct(color);
    return shape;
}

Shape Debug::Paint::circle(float x, float y, float radius, const Color& color) {
    Shape shape(ShapeType::s_circle);
    float* values = new float[shape_type_to_num_of_components(s_circle)];
    fill_fixed_size_array(values, x, y, radius);
    shape.set_predefined_shape(values);
    shape.set_color_direct(color);
    return shape;
}

Shape Debug::Paint::rect(float x, float y, float width, float height, const Color& color) {
    Shape shape(ShapeType::s_rect);
    float* values = new float[shape_type_to_num_of_components(s_rect)];
    fill_fixed_size_array(values, x, y, width, height);
    shape.set_predefined_shape(values);
    shape.set_color_direct(color);
    return shape;
}

Shape Debug::Paint::line(float x1, float y1, float x2, float y2, const Color& color) {
    Shape shape(ShapeType::s_line);
    float* values = new float[shape_type_to_num_of_components(s_line)];
    fill_fixed_size_array(values, x1, y1, x2, y2);
    shape.set_predefined_shape(values);
    shape.set_color_direct(color);
    return shape;
}

static inline void fill_rect_shape(std::map<std::string, float>& mapp, float x, float y, float width, float height) {
    mapp["x"] = x;
    mapp["y"] = y;
    mapp["width"] = width;
    mapp["height"] = height;
}

Shape Debug::Paint::text(float x, float y, const std::string& str, const Color& color) {
    Shape shape(ShapeType::s_text, str);
    float* values = new float[shape_type_to_num_of_components(s_text)];
    fill_fixed_size_array(values, x, y);
    shape.set_predefined_shape(values);
    shape.set_color_direct(color);
    return shape;
}

Shape Debug::Paint::robot(float x, float y, float rot, const Color& color) {
    Shape shape(ShapeType::s_robot);
    float* values = new float[shape_type_to_num_of_components(s_robot)];
    fill_fixed_size_array(values, x, y, rot);
    shape.set_predefined_shape(values);
    shape.set_color_direct(color);
    return shape;
}

namespace {

static inline void fill_point_shape(std::map<std::string, float>& mapp, float x, float y) {
    mapp["x"] = x;
    mapp["y"] = y;
}

static inline void fill_dot_shape(std::map<std::string, float>& mapp, float x, float y) {
    mapp["x"] = x;
    mapp["y"] = y;
}

static inline void fill_circle_shape(std::map<std::string, float>& mapp, float x, float y, float radius) {
    mapp["x"] = x;
    mapp["y"] = y;
    mapp["radius"] = radius;
}

static inline void fill_line_shape(std::map<std::string, float>& mapp, float x1, float y1, float x2, float y2) {
    mapp["x1"] = x1;
    mapp["y1"] = y1;
    mapp["x2"] = x2;
    mapp["y2"] = y2;
}

static inline void fill_text_shape(std::map<std::string, float>& mapp, float x, float y) {
    mapp["x"] = x;
    mapp["y"] = y;
}

static inline void fill_robot_shape(std::map<std::string, float>& mapp, float x, float y, float rot) {
    mapp["x"] = x;
    mapp["y"] = y;
    mapp["rot"] = rot;
}

} //anonymous namespace

void Shape::ensure_map_is_filled(std::map<std::string, float>& mapp) {
    if(m_direct_values == nullptr || m_direct_values == NULL) {
        return;
    }
    #define V m_direct_values
    switch(m_shape_type) {
        case(ShapeType::s_circle): {
            fill_circle_shape(mapp, V[0], V[1], V[2]);
            break;
        }
        case(ShapeType::s_dot): {
            fill_dot_shape(mapp, V[0], V[1]);
            break;
        }
        case(ShapeType::s_line): {
            fill_line_shape(mapp, V[0], V[1], V[2], V[3]);
            break;
        }
        case(ShapeType::s_point): {
            fill_point_shape(mapp, V[0], V[1]);
            break;
        }
        case(ShapeType::s_rect): {
            fill_rect_shape(mapp, V[0], V[1], V[2], V[3]);
            break;
        }
        case(ShapeType::s_robot): {
            fill_robot_shape(mapp, V[0], V[1], V[2]);
            break;
        }
        case(ShapeType::s_text): {
            fill_text_shape(mapp, V[0], V[1]);
            break;
        }
        default: {
            throw std::runtime_error("This shape type is not supported");
        }
    }
    int color_begin_idx = shape_type_to_num_of_components(m_shape_type) - 3;
    #ifdef DEBUG_ENABLES_DYNAMIC_SHAPES
    set("color", Color(V[color_begin_idx], V[color_begin_idx + 1], V[color_begin_idx + 2]));
    #else
    set("color", Color(V[color_begin_idx], V[color_begin_idx + 1], V[color_begin_idx + 2]), mapp);
    #endif
    #undef V
    //m_direct_values = nullptr;
}

