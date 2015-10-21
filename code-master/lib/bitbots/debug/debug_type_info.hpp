#ifndef _DEBUG_TYPE_INFO_HPP
#define _DEBUG_TYPE_INFO_HPP

#include <string>
#include <vector>

#include <Eigen/Core>

#include "../util/eigen_util.hpp"
#include "debug_paint.hpp"

namespace Debug {

    enum DebugType : uint8_t{BOOL, UCHAR, USHORT, UINT, ULONG, CHAR, SHORT, INT, LONG, FLOAT, DOUBLE, STRING,
        SHAPE, SHAPE_VECTOR ,BWMATRIX, RGBMATRIX, LOG, WARNING
    };

    template<class T> struct TypeInfo;

    #define TYPE_INFO(TYPE, ENUM_TYPE,...) \
    /*First Argument is the type, the namespace behind*/ \
    static const char* ENUM_TYPE ## _name = #TYPE; \
    template<> struct TypeInfo<__VA_ARGS__  TYPE> { \
        enum Type{Type=ENUM_TYPE}; \
        const char* name = ENUM_TYPE ## _name; \
        TypeInfo() {}; \
    };

#define EIGEN_MATRIX_TYPE_INFO(ENUM_TYPE, ...) \
    static const char* ENUM_TYPE ## _name = std::string(std::string("Mat") + std::to_string(sizeof(__VA_ARGS__::Scalar))).data(); \
    template<> struct TypeInfo<__VA_ARGS__ > { \
        enum Type{Type=ENUM_TYPE}; \
        const char* name = ENUM_TYPE ## _name; \
        TypeInfo(){} \
    };

    EIGEN_MATRIX_TYPE_INFO(BWMATRIX, Eigen::MatrixHolder<Eigen::RMatrixXUb>)
    EIGEN_MATRIX_TYPE_INFO(RGBMATRIX, Eigen::MatrixHolder<Eigen::RMatrixVec3Ub>)

    TYPE_INFO(uint8_t, UCHAR,)
    TYPE_INFO(uint16_t, USHORT,)
    TYPE_INFO(uint32_t, UINT,)
    TYPE_INFO(uint64_t, ULONG,)

    TYPE_INFO(int8_t, CHAR,)
    TYPE_INFO(int16_t, SHORT,)
    TYPE_INFO(int32_t, INT,)
    TYPE_INFO(int64_t, LONG,)

    TYPE_INFO(bool, BOOL,)
    TYPE_INFO(float, FLOAT,)
    TYPE_INFO(double, DOUBLE,)

    TYPE_INFO(string, STRING,std::)

    TYPE_INFO(Shape, SHAPE, Paint::)
    TYPE_INFO(vector<Paint::Shape>, SHAPE_VECTOR, std::)

    #undef TYPE_INFO
}

#endif

