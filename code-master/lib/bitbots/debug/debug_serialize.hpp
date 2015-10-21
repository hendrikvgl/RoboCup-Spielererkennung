#ifndef _DEBUG_BOOST_SERIALIZATION_HPP
#define _DEBUG_BOOST_SERIALIZATION_HPP

#include <string>
#include <fstream>

#include <boost/mpl/bool.hpp>
#include <boost/shared_ptr.hpp>
#include <Eigen/Core>

#include "debug_type_info.hpp"

namespace Debug{
namespace Serialize {

#define EIGEN_MATIRXHOLDER_SERIALIZE_SPECILIZATION(MATRIX_T) \
template<class Archive> \
void serialize(Archive& ar, MATRIX_T& mat) { \
    uint32_t rows, cols; \
    if(Archive::is_saving::value) { \
        rows = mat.rows(); \
        cols = mat.cols(); \
    } \
    \
    ar & rows; \
    ar & cols; \
    \
    if(Archive::is_loading::value) { \
        mat.create(rows, cols); \
    } \
    for(int y = 0; y < mat.rows(); y++) \
        ar.raw((char*)(&mat(y,0)), sizeof(MATRIX_T::Scalar)*mat.cols()); \
}

    EIGEN_MATIRXHOLDER_SERIALIZE_SPECILIZATION(Eigen::MatrixHolder<Eigen::RMatrixXUb>)
    EIGEN_MATIRXHOLDER_SERIALIZE_SPECILIZATION(Eigen::MatrixHolder<Eigen::RMatrixXb>)
    EIGEN_MATIRXHOLDER_SERIALIZE_SPECILIZATION(Eigen::MatrixHolder<Eigen::RMatrixVec3Ub>)
    EIGEN_MATIRXHOLDER_SERIALIZE_SPECILIZATION(Eigen::MatrixHolder<Eigen::RMatrixVec3b>)

template<class Archive, class T, int N>
void serialize(Archive& ar, Eigen::Matrix<T, N, 1>& vec) {
    ar.raw(&vec(0), N);
}

template<class Archive>
void serialize(Archive& ar, std::string& str) {
    uint32_t size = str.size();
    ar & size;

    if(Archive::is_saving::value) {
        ar.raw(str.c_str(), str.size());
    }

    if(Archive::is_loading::value) {
        str.resize(size);
        for(unsigned i = 0; i < size; i++) {
            ar & str[i];
        }
    }
}

template<class Archive, class T>
void serialize(Archive& ar, std::vector<T>& vec) {
    uint32_t size;
    if(Archive::is_saving::value) {
        size = vec.size();
        ar & size;
    }

    if(Archive::is_loading::value) {
        ar & size;
        vec.resize(size);
    }

    for(unsigned i = 0; i < size; i++) {
        ar & vec[i];
    }
}

template<class Archive, class A, class B>
void serialize(Archive& ar, std::map<A, B>& map) {
    uint32_t size;abort();

    if(Archive::is_saving::value) {
        size = map.size();
        ar & size;

        typename std::map<A, B>::iterator it;
        for(it = map.begin(); it != map.end(); it++) {
            std::string key = it->first;
            ar & key;
            ar & it->second;
        }
    }

    if(Archive::is_loading::value) {
        ar & size;

        for(unsigned i = 0; i < size; i++) {
            A key;
            ar & key;
            ar & map[key];
        }
    }
}

#define SERIALIZE_PRIMITIVE(type) \
template<class Archive> inline void serialize(Archive& ar, type& val) { \
    ar.raw(&val); \
}

SERIALIZE_PRIMITIVE(char)
SERIALIZE_PRIMITIVE(int8_t)
SERIALIZE_PRIMITIVE(int16_t)
SERIALIZE_PRIMITIVE(int32_t)
SERIALIZE_PRIMITIVE(int64_t)

SERIALIZE_PRIMITIVE(uint8_t)
SERIALIZE_PRIMITIVE(uint16_t)
SERIALIZE_PRIMITIVE(uint32_t)
SERIALIZE_PRIMITIVE(uint64_t)

SERIALIZE_PRIMITIVE(bool)
SERIALIZE_PRIMITIVE(float)
SERIALIZE_PRIMITIVE(double)

#undef SERIALIZE_PRIMITIVE


#define SERIALIZE_POINTER(type) \
template<class Archive> inline void serialize(Archive& ar, type* val, size_t count) { \
ar.raw(val, count); \
}

SERIALIZE_POINTER(float)
SERIALIZE_POINTER(double)

#undef SERIALIZE_POINTER

class OutputArchive {
private:
    std::ostream& output;

public:
    OutputArchive(std::ostream& output)
        : output(output) {}

    template<class T>
    void operator & (const T& value) {
        serialize(*this, const_cast<T&>(value));
    }

    template<class T>
    void operator() (T* value, size_t count) {
        serialize(*this, value, count);
    }

    template<class T>
    void raw(T* value, const int n = 1) {
        output.write((char*)value, sizeof(T)*n);
    }

    typedef boost::mpl::bool_<true> is_saving;
    typedef boost::mpl::bool_<false> is_loading;
};


class InputArchive {
private:
    std::istream& input;

public:
    InputArchive(std::istream& input)
        : input(input) {}

    template<class T>
    void operator & (T& value) {
        serialize(*this, value);
    }

    template<class T>
    void operator() (T* value, size_t count) {
        serialize(*this, value, count);
    }

    template<class T>
    void raw(T* value, const int n = 1) {
        input.read((char*)value, sizeof(T)*n);
    }

    typedef boost::mpl::bool_<false> is_saving;
    typedef boost::mpl::bool_<true> is_loading;
};


// namespaces
} }

#endif

