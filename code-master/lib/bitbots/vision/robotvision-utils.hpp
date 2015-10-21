#ifndef __ROBOTVISION_UTILS_HPP
    #error Only import this from robovision.hpp
#endif

namespace Vision {
namespace intern {
    /**
        Gibt die Distanz zwischen der Linie [a b] und dem Punkt c.
    */
    inline
    float distance_line_point(const Eigen::Vector2f& a, const Eigen::Vector2f& b, const Eigen::Vector2f& c) {
        return abs( (b.x()-a.x())*c.y() + (a.y()-b.y())*c.x() + a.x()*b.y() - b.x()*a.y() ) / (b-a).norm();
    }

    template<class DerivedA, class DerivedB, class DerivedC>
    void convolve(const Eigen::ArrayBase<DerivedA>& input,
            const Eigen::ArrayBase<DerivedB>& kernel,
            const Eigen::DenseBase<DerivedC>& result_) {

        Eigen::DenseBase<DerivedC>& result = const_cast<Eigen::DenseBase<DerivedC>&>(result_);

        if((kernel.rows() & 1) == 0 || kernel.rows() < 3 || input.rows() - kernel.rows() <= 0)
            throw std::runtime_error("convolve: kernel to small or even");

        result.derived().resize(input.rows() - kernel.rows(), 1);

        for(int i = 0; i < result.rows(); i++)
            result(i) = input.block(i, 0, kernel.rows(), 1).cwiseProduct(kernel).sum();
    }

    template<class Derived>
    typename Derived::Scalar stddev(const Eigen::ArrayBase<Derived>& input) {
        return std::sqrt((input - input.mean()).square().sum() / (input.rows()-1));
    }

} } // namespace

