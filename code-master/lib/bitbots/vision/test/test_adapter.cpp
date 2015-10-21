#include <gtest/gtest.h>
#include <Eigen/Core>

#include "../adapter.hpp"

namespace Test {

TEST(Adapter, IYUV) {
    char iyuv_data[24] = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,31,32,33,34,41,42,43,44};
    Eigen::MapRMatb map(iyuv_data, 4, 6);
    Vision::Adapter::IYUVAdapter iyuv(map);

    EXPECT_EQ(iyuv(0,0), Eigen::Vector3i(1,31,41));
    EXPECT_EQ(iyuv(1,0), Eigen::Vector3i(2,31,41));
    EXPECT_EQ(iyuv(2,0), Eigen::Vector3i(3,32,42));
    EXPECT_EQ(iyuv(3,0), Eigen::Vector3i(4,32,42));

    EXPECT_EQ(iyuv(0,1), Eigen::Vector3i(5,31,41));
    EXPECT_EQ(iyuv(1,1), Eigen::Vector3i(6,31,41));
    EXPECT_EQ(iyuv(2,1), Eigen::Vector3i(7,32,42));
    EXPECT_EQ(iyuv(3,1), Eigen::Vector3i(8,32,42));

    EXPECT_EQ(iyuv(0,2), Eigen::Vector3i(9,33,43));
    EXPECT_EQ(iyuv(1,2), Eigen::Vector3i(10,33,43));
    EXPECT_EQ(iyuv(2,2), Eigen::Vector3i(11,34,44));
    EXPECT_EQ(iyuv(3,2), Eigen::Vector3i(12,34,44));

    EXPECT_EQ(iyuv(0,3), Eigen::Vector3i(13,33,43));
    EXPECT_EQ(iyuv(1,3), Eigen::Vector3i(14,33,43));
    EXPECT_EQ(iyuv(2,3), Eigen::Vector3i(15,34,44));
    EXPECT_EQ(iyuv(3,3), Eigen::Vector3i(16,34,44));

    EXPECT_EQ(iyuv.size<Eigen::Vector2i>(), Eigen::Vector2i(4,4));
}

TEST(Adapter, YUYV){
    char yuyv_data[32] = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32};
    Eigen::MapRMatb map(yuyv_data, 4, 8);
    Vision::Adapter::RawYUYVAdapter iyuv(map);

    EXPECT_EQ(iyuv(0,0), Eigen::Vector3i(1,2,4));
    EXPECT_EQ(iyuv(1,0), Eigen::Vector3i(3,2,4));
    EXPECT_EQ(iyuv(2,0), Eigen::Vector3i(5,6,8));
    EXPECT_EQ(iyuv(3,0), Eigen::Vector3i(7,6,8));

    EXPECT_EQ(iyuv(0,1), Eigen::Vector3i(9,10,12));
    EXPECT_EQ(iyuv(1,1), Eigen::Vector3i(11,10,12));
    EXPECT_EQ(iyuv(2,1), Eigen::Vector3i(13,14,16));
    EXPECT_EQ(iyuv(3,1), Eigen::Vector3i(15,14,16));

    EXPECT_EQ(iyuv(0,2), Eigen::Vector3i(17,18,20));
    EXPECT_EQ(iyuv(1,2), Eigen::Vector3i(19,18,20));
    EXPECT_EQ(iyuv(2,2), Eigen::Vector3i(21,22,24));
    EXPECT_EQ(iyuv(3,2), Eigen::Vector3i(23,22,24));

    EXPECT_EQ(iyuv(0,3), Eigen::Vector3i(25,26,28));
    EXPECT_EQ(iyuv(1,3), Eigen::Vector3i(27,26,28));
    EXPECT_EQ(iyuv(2,3), Eigen::Vector3i(29,30,32));
    EXPECT_EQ(iyuv(3,3), Eigen::Vector3i(31,30,32));

    EXPECT_EQ(iyuv.size<Eigen::Vector2i>(), Eigen::Vector2i(4,4));
}

TEST(Adapter, InvertedYUYV){
    char yuyv_data[32] = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32};
    Eigen::MapRMatb map(yuyv_data, 4, 8);
    Vision::Adapter::InvertedPictureAdapter<Vision::Adapter::RawYUYVAdapter> iyuv(map);

    EXPECT_EQ(iyuv(3,3), Eigen::Vector3i(1,2,4));
    EXPECT_EQ(iyuv(2,3), Eigen::Vector3i(3,2,4));
    EXPECT_EQ(iyuv(1,3), Eigen::Vector3i(5,6,8));
    EXPECT_EQ(iyuv(0,3), Eigen::Vector3i(7,6,8));

    EXPECT_EQ(iyuv(3,2), Eigen::Vector3i(9,10,12));
    EXPECT_EQ(iyuv(2,2), Eigen::Vector3i(11,10,12));
    EXPECT_EQ(iyuv(1,2), Eigen::Vector3i(13,14,16));
    EXPECT_EQ(iyuv(0,2), Eigen::Vector3i(15,14,16));

    EXPECT_EQ(iyuv(3,1), Eigen::Vector3i(17,18,20));
    EXPECT_EQ(iyuv(2,1), Eigen::Vector3i(19,18,20));
    EXPECT_EQ(iyuv(1,1), Eigen::Vector3i(21,22,24));
    EXPECT_EQ(iyuv(0,1), Eigen::Vector3i(23,22,24));

    EXPECT_EQ(iyuv(3,0), Eigen::Vector3i(25,26,28));
    EXPECT_EQ(iyuv(2,0), Eigen::Vector3i(27,26,28));
    EXPECT_EQ(iyuv(1,0), Eigen::Vector3i(29,30,32));
    EXPECT_EQ(iyuv(0,0), Eigen::Vector3i(31,30,32));

    EXPECT_EQ(iyuv.size<Eigen::Vector2i>(), Eigen::Vector2i(4,4));
}

}
using namespace Test;

int main(int argc, char** argv) {
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}