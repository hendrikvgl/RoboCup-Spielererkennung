#ifndef _SAMPLE_HPP
#define _SAMPLE_HPP

#include <Eigen/Core>
#include <Eigen/StdVector>

namespace Vision{
namespace Sample {
enum SamplingDistanceType{OFF = 0, U_DIST, V_DIST, UV_DIST, FULL_DIST, SUM};

/**
 * A sample representing a point in the picture.
 * Additionally it stores a reference to the index in the pointcload
 */
template<class vector_type, class index_type>
class Index_Sample : public Eigen::Matrix<vector_type, 2, 1> {
private:
    index_type index;

public:
    EIGEN_MAKE_ALIGNED_OPERATOR_NEW

    Index_Sample(const Eigen::Matrix<vector_type, 2, 1>& pos, int index)
        : Eigen::Matrix<vector_type, 2, 1>(pos), index(index) {
    }

    Index_Sample()
        : Eigen::Matrix<vector_type, 2, 1>(0,0), index(0){
    }

    index_type get_index() const {
        return index;
    }

    Eigen::Matrix<vector_type, 2, 1>& vector(){
        return *this;
    }

    const Eigen::Matrix<vector_type, 2, 1>& vector()const{
        return *this;
    }

    template<SamplingDistanceType type>
    bool is_close_to(const Index_Sample<vector_type, index_type>& other __attribute__((unused)) ) const {
        return true;
    }
};

/**
 * A sample representing a point in the picture.
 * Additionally it stores a reference to the index in the pointcload and the index
 * of the parent, when set
 */
template<class vector_type, class index_type, class parent_type>
class Double_Index_Sample : public Index_Sample<vector_type, index_type> {
private:
    parent_type m_parent;

public:
    EIGEN_MAKE_ALIGNED_OPERATOR_NEW
    Double_Index_Sample(const Index_Sample<vector_type, index_type>& sample, int parent)
        : Index_Sample<vector_type, index_type>(sample), m_parent(parent) {
    }

    Double_Index_Sample()
        : Index_Sample<vector_type, index_type>(Eigen::Matrix<vector_type,2,1>(0,0),0), m_parent(0){
    }

    parent_type get_parent() const {
        return m_parent;
    }
};

/**
 * A sample representing a point in the picture.
 * Additionally it stores a reference to the index in the pointcload and an
 * colorvector
 */
template<class vector_type, class index_type, class info_vector_type>
class Index_Vector_Sample : public Index_Sample<vector_type, index_type>{
private:
    Eigen::Matrix<info_vector_type, 3, 1> masq;

public:
    EIGEN_MAKE_ALIGNED_OPERATOR_NEW

    template <class T>
    Index_Vector_Sample(const Eigen::Matrix<vector_type, 2, 1>& v, const index_type i, const Eigen::Matrix<T, 3, 1>& in)
    :Index_Sample<vector_type, index_type>(v,i), masq(in.template cast<info_vector_type>()){
    }

    template <class T>
    Index_Vector_Sample(const Index_Sample<vector_type, index_type>& sample, const Eigen::Matrix<T, 3, 1>& masq)
    : Index_Sample<vector_type, index_type>(sample), masq(masq.template cast<info_vector_type>()) {
    }

    Index_Vector_Sample()
    : Index_Sample<vector_type, index_type>(Eigen::Matrix<vector_type, 2, 1>(0, 0), 0), masq(Eigen::Matrix<info_vector_type, 3, 1>(0,0,0)) {
    }

    const Eigen::Matrix<info_vector_type, 3, 1>& get_masq() const{
        return masq;
    }

    template<int type = FULL_DIST, int thres=7>
    bool is_close_to(const Index_Vector_Sample<vector_type, index_type, info_vector_type>& other) const {
        switch(type){
            case(OFF):
                return true;
            case(U_DIST):
                return abs((masq(1) - other.masq(1))) < thres;
            case(V_DIST):
                return abs((masq(2) - other.masq(2))) < thres;
            case(UV_DIST):
                //return is_close_to<U_DIST>(other) && is_close_to<V_DIST>(other);
                return ((masq.template tail<2>()) - (other.masq.template tail<2>())).array().abs().maxCoeff() < thres;
            case(FULL_DIST):
                return (masq - other.masq).array().abs().maxCoeff() < thres;
            case(SUM):
                return (masq - other.masq).array().abs().sum() < thres;
            default:
                throw std::runtime_error("Invalid distance switch argument");
        }
    }
};

typedef Index_Sample<float, int> ColorSample;
typedef Index_Sample<int, int> VisionSample;
typedef Index_Vector_Sample<int, int, uint8_t> ColorColorSample;
typedef Double_Index_Sample<float, int, int> LineSample;
typedef Double_Index_Sample<int, int, int> VisionLineSample;

inline float distance(const Eigen::Vector2f& a, const Eigen::Vector2f&  b) {
    return (a - b).norm();
}

inline float distance_sqr(const Eigen::Vector2f& a, const Eigen::Vector2f& b) {
    return (a - b).squaredNorm();
}

} }//namespace

EIGEN_DEFINE_STL_VECTOR_SPECIALIZATION(Vision::Sample::ColorColorSample)
EIGEN_DEFINE_STL_VECTOR_SPECIALIZATION(Vision::Sample::VisionLineSample)
EIGEN_DEFINE_STL_VECTOR_SPECIALIZATION(Vision::Sample::VisionSample)
EIGEN_DEFINE_STL_VECTOR_SPECIALIZATION(Vision::Sample::ColorSample)
EIGEN_DEFINE_STL_VECTOR_SPECIALIZATION(Vision::Sample::LineSample)

#endif
