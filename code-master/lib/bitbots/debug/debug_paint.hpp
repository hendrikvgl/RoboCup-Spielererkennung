#ifndef __DEBUG_PAINT_H__
#define __DEBUG_PAINT_H__

#include <map>
#include <string>
#include <sstream>
#include <assert.h>
#include <stdexcept>

#include <Eigen/Core>
#include <boost/tuple/tuple.hpp>

namespace Debug {
namespace Paint {

typedef boost::tuple<float, float, float> Color;
enum ShapeType{s_other=0, s_circle, s_dot, s_line, s_point, s_rect, s_robot, s_text};
//Forward decalration
static inline const std::string& shape_type_to_text(int s);
static inline size_t shape_type_to_num_of_components(int s);

class Shape {
private:
    int m_shape_type;
    std::string m_text;
    #ifdef DEBUG_ENABLES_DYNAMIC_SHAPES
    std::string m_type;
    std::map<std::string, float> m_values;
    #endif
    float* m_direct_values=NULL;

    void ensure_map_is_filled(std::map<std::string, float>& mapp);

public:

    Shape()
    : m_shape_type(s_other), m_direct_values(nullptr) {}

    #ifdef DEBUG_ENABLES_DYNAMIC_SHAPES
    Shape(const std::string& type, const std::string& text = std::string())
    : m_shape_type(ShapeType::s_other), m_type(type), m_text(text), m_direct_values(NULL) {}
    #endif

    Shape(ShapeType shape_type, const std::string& text = std::string())
    : m_shape_type(shape_type), m_text(text), m_direct_values(NULL) {
        assert(shape_type != s_other);
    }

    Shape(const Shape& other)
    :  m_shape_type(other.m_shape_type), m_text(other.m_text)
       #ifdef DEBUG_ENABLES_DYNAMIC_SHAPES
       m_type(other.m_type), m_values(other.m_values)
       #endif
   {
        unsigned count = shape_type_to_num_of_components(m_shape_type);
        m_direct_values = new float[count];
        for(unsigned i = 0; i < count; ++i) {
            m_direct_values[i] = other.m_direct_values[i];
        }
    }

    Shape(Shape&& other)
    :  m_shape_type(other.m_shape_type), m_text(std::move(other.m_text)),
       #ifdef DEBUG_ENABLES_DYNAMIC_SHAPES
       m_type(other.m_type), m_values(other.m_values),
       #endif
    m_direct_values(other.m_direct_values) {
        other.m_direct_values = nullptr;
    }

    Shape& operator=(const Shape& other) {
        this->~Shape();
        new (this) Shape(other);
        return *this;
    }

    ~Shape() {
        delete m_direct_values;
    }

    #ifdef DEBUG_ENABLES_DYNAMIC_SHAPES
    Shape& set(const std::string& name, float value) {
        m_values[name] = value;
        return *this;
    }

    Shape& set(const std::string& name, const Color& color) {
        m_values[name + ".r"] = color.get<0>();
        m_values[name + ".g"] = color.get<1>();
        m_values[name + ".b"] = color.get<2>();
        return *this;
    }
    #else
    Shape& set(const std::string& name, const Color& color, std::map<std::string, float>& mapp) {
        mapp[name + ".r"] = color.get<0>();
        mapp[name + ".g"] = color.get<1>();
        mapp[name + ".b"] = color.get<2>();
        return *this;
    }
    #endif

    Shape& set_predefined_shape(float* values) {
        assert(m_direct_values == nullptr || m_direct_values == NULL);
        m_direct_values = values;
        return *this;
    }

    Shape& set_color_direct(const Color& color) {
        assert(m_direct_values != NULL && m_direct_values != nullptr);
        int direct_value_size = shape_type_to_num_of_components(m_shape_type);
        m_direct_values[direct_value_size - 3] = color.get<0>();
        m_direct_values[direct_value_size - 2] = color.get<1>();
        m_direct_values[direct_value_size - 1] = color.get<2>();
        return *this;
    }

    Shape& describe(const std::string& text) {
        this->m_text = text;
        return *this;
    }

    const std::string& get_type() {
        #ifdef DEBUG_ENABLES_DYNAMIC_SHAPES
        return m_shape_type == ShapeType::s_other ?  m_type: shape_type_to_text(m_shape_type);
        #else
        return shape_type_to_text(m_shape_type);
        #endif
    }

    const std::string& get_text() {
        return m_text;
    }

    #ifdef DEBUG_ENABLES_DYNAMIC_SHAPES
    const std::map<std::string, float>& get_values() const {
        const_cast<Shape*>(this)->ensure_map_is_filled(m_values);
        return m_values;
    }
    #endif

    #ifdef DEBUG_ENABLES_DYNAMIC_SHAPES
    std::map<std::string, float>& get_values() {
        ensure_map_is_filled(m_values);
        return m_values;
    }
    #else
    std::map<std::string, float> get_values() {
        std::map<std::string, float> to_return;
        ensure_map_is_filled(to_return);
        return to_return;
    }
    #endif

    template<class Archive>
    friend void serialize(Archive& ar, Shape& shape);
};

template<class Archive>
void serialize(Archive& ar, Shape& shape) {
    ar & shape.m_shape_type;
    assert(shape.m_shape_type != s_other);
    ar & shape.m_text;
    if(shape.m_shape_type == ShapeType::s_other) {
        #ifdef DEBUG_ENABLES_DYNAMIC_SHAPES
        shape.ensure_map_is_filled(shape.m_values);
        ar & shape.m_type;
        ar & shape.m_values;
        #endif
    } else {
        int value_count = shape_type_to_num_of_components(shape.m_shape_type);
        if(Archive::is_loading::value) {
            shape.m_direct_values = new float[value_count];
        }
        ar(shape.m_direct_values, value_count);
    }
}

namespace {
    const std::string str_circle = "circle",
                      str_dot = "dot",
                      str_line = "line",
                      str_point = "point",
                      str_rect = "rect",
                      str_robot = "robot",
                      str_text = "text";
} //anonymous namespace

static inline const std::string& shape_type_to_text(int s) {
    switch(s){
        #define SWITCH_CASE(CASE) \
        case(ShapeType::s_ ## CASE): \
            return str_ ## CASE;

        SWITCH_CASE(circle);
        SWITCH_CASE(dot);
        SWITCH_CASE(line);
        SWITCH_CASE(point);
        SWITCH_CASE(rect);
        SWITCH_CASE(robot);
        SWITCH_CASE(text);
        default:
            throw std::runtime_error("This Shape ist not supported");
    }
    #undef SWITCH_CASE
}

static inline size_t shape_type_to_num_of_components(int s) {
    switch(s){
        #define SWITCH_CASE(CASE, NUM) \
        case(ShapeType::CASE): \
            return NUM + 3;

        SWITCH_CASE(s_circle, 3);
        SWITCH_CASE(s_dot, 2);
        SWITCH_CASE(s_line, 4);
        SWITCH_CASE(s_point, 2);
        SWITCH_CASE(s_rect, 4);
        SWITCH_CASE(s_robot,3);
        SWITCH_CASE(s_text,2);
        default:
            throw std::runtime_error("This Shape ist not supported");
    }
    #undef SWITCH_CASE
}

// Schubladen denken
extern Color Black;
extern Color White;

// Farben
extern Color Red;
extern Color Green;
extern Color Blue;
extern Color Pink;
extern Color Yellow;
extern Color Cyan;

Shape dot(float x, float y, const Color& color=White);
Shape point(float x, float y, const Color& color=White);
Shape line(float x1, float y1, float x2, float y2, const Color& color=White);
Shape circle(float x, float y, float radius, const Color& color=White);
Shape rect(float x, float y, float w, float h, const Color& color=White);
Shape text(float x, float y, const std::string& str, const Color& color=White);
Shape robot(float x, float y, float rot, const Color& color=Pink);


template<class Derived>
inline Shape robot(const Eigen::DenseBase<Derived>& pos, const Color& color=Pink) {
    return robot(pos(0), pos(1), pos(2), color);
}

template<class Derived>
inline Shape circle(const Eigen::DenseBase<Derived>& pos, float radius, const Color& color=White) {
    return circle(pos(0), pos(1), radius, color);
}

template<class Derived>
inline Shape point(const Eigen::DenseBase<Derived>& pos, const Color& color=White) {
    return point(pos(0), pos(1), color);
}

template<class Derived>
inline Shape dot(const Eigen::DenseBase<Derived>& pos, const Color& color=White) {
    return dot(pos(0), pos(1), color);
}

template<class A, class B>
inline Shape line(const Eigen::DenseBase<A>& a, const Eigen::DenseBase<B>& b, const Color& color=White) {
    return line(a(0), a(1), b(0), b(1), color);
}

template<class A, class B>
inline Shape rect(const Eigen::DenseBase<A>& a, const Eigen::DenseBase<B>& b, const Color& color=White) {
    return rect(a(0), a(1), b(0)-a(0), b(1)-a(1), color);
}

inline
Shape text(float x, float y, const std::stringstream& str, const Color& color=White) {
    return text(x, y, str.str(), color);
}


template<class Derived, class S>
inline Shape text(const Eigen::DenseBase<Derived>& a, const S& str, const Color& color=White) {
    return text(a(0), a(1), str, color);
}

}} // namespace

#endif /* __DEBUG_PAINT_H__ */

