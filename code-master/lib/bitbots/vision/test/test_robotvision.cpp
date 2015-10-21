#include <Eigen/Core>
#include <iostream>

#include <unistd.h>
#include <malloc.h>
#include <assert.h>
#include <gtest/gtest.h>

#include "../../util/eigen_util.hpp"
#include "../../util/png.hpp"

#include "../robotvision.hpp"
using namespace std;
using namespace Eigen;
using namespace Vision;
using namespace Vision::Info;
using namespace Vision::Adapter;
using namespace Util;

namespace Test {

#if 0
typedef InvertedPictureAdapter<RawYUYVAdapter> VAdapter;
#define ADAPTER "InvertedPictureAdapter<RawYUYVAdapter> VAdapter"
#else
typedef BGRYUVAdapter VAdapter;
#define ADAPTER "RGBYUVAdapter VAdapter"
#endif

#if defined NDEBUG || defined SKIP_SLEEP
#define SLEEPTIME 0
#else
#define SLEEPTIME 1
#endif

#define SLEEP_T(T) sleep(T);
#define SLEEP SLEEP_T(SLEEPTIME)

#define ASSERT_EQ_(expected, actual) ASSERT_EQ(expected, actual)<< "But was:"<<endl<< actual<< endl<<"instead of"<<endl<<expected
#define EXPECT_EQ_(expected, actual) EXPECT_EQ(expected, actual)<< "But was:"<<endl<< actual<< endl<<"instead of"<<endl<<expected

typedef RobotVision RVision;

RVision* vision_ptr = nullptr;
VAdapter* adapter_ptr = nullptr;
char* image_ptr = nullptr;

#ifndef PROJECT_DIR
    #define PROJECT_DIR NotAPath
#endif
#define INDIRECTION(X,Y) Y(X)
#define ROOT_DIR INDIRECTION(PROJECT_DIR, STR)
#define STR(X) #X

static const char* const project_path = ROOT_DIR;
static std::string default_yellow_config_str = std::string(project_path) + "/share/bitbots/vision-color-config/Teheran2014/yellow.png";
static const char*const default_yellow_config = default_yellow_config_str.data();
static std::string default_test_image_str = std::string(project_path) + "/lib/bitbots/vision/test/TorBallTestBild.png";
static const char*const default_test_image = default_test_image_str.data();

static RMatrixXb load_single_color_config(const char* file, int masq) {
    RMatrixXb config = RMatrixXb::Zero(256,768);
    PngImageHolder holder = load_png(file);
    const MapRMatUb& raw_config = holder.get_bw_image();
    for(int x = 0; x < 256; ++x) {
        for(int y = 0; y < 768; ++y) {
            if(raw_config(x, y) != 0) {
                config(x, y) |= masq;
            }
        }
    }
    holder.delete_internal_data();
    return config;
}

template<class Adaper>
Adaper* read_test_image(const char* im){
    PngImageHolder holder = load_png(im);
    const Eigen::MapRMatVec4Ub& image = holder.get_bgra_image();
    L_DEBUG(cout<<im<<" mit "<< ADAPTER<<" geladen"<<endl);
    if(image_ptr != nullptr) delete[] image_ptr;
    image_ptr = (char*)PngImageHolder::bgra_to_rgb(holder.get_bgra_image());
    Eigen::MapRMatb* imm = new Eigen::MapRMatb(image_ptr, image.rows(), image.cols() * 3);
    Adaper* add = new Adaper(*imm);
    assert(add->get_height() == image.rows());
    assert(add->get_width() == image.cols());
    holder.delete_internal_data();
    delete imm;
    return add;
}

void make_adapter(const char* im=nullptr) {
    if(adapter_ptr != NULL && im == nullptr) {
        return;
    }
    delete adapter_ptr;
    const char* image = im == NULL? default_test_image : im;
    adapter_ptr = read_test_image<VAdapter>(image);
}

void del_adapter_and_vision() {
    delete adapter_ptr;
    delete vision_ptr;
    adapter_ptr = nullptr;
    vision_ptr = nullptr;
}

void make_vision() {
    int y = 15, u = 10, v = 10;
    bool dynamic = true;
    if(vision_ptr != NULL) {
        vision_ptr->reset_vision_to_defaults();
        vision_ptr->set_carpet_threshold(y, u, v);
        vision_ptr->set_dynamic_u_threshold(dynamic);
        return;
    }
    vision_ptr = new RVision(y, u, v, dynamic, 1280, 720);
    MatrixXb color_config = MatrixXb::Zero(256,768);
    vision_ptr->set_color_config(color_config);
}

void disable_vision_options() {
    vision_ptr->reset_vision_to_defaults();
    vision_ptr->set_b_w_debug_image(false);
    vision_ptr->set_ball_enabled(false);
    vision_ptr->set_goals_enabled(false);
    vision_ptr->set_pylons_enabled(false);
    vision_ptr->set_shape_vectors_enabled(false);
    vision_ptr->set_team_marker_enabled(false);
    vision_ptr->set_lines_enabled(false);
    vision_ptr->set_rgb_step_factor(3);
}

bool test_ball_info(const vector<BallInfo>& info){
    if(info.size() == 0){
        L_DEBUG(cout<<"Noch kein Ball gefunden"<<endl);
        return false;
    }else{
        L_DEBUG(cout<<"Ball gefunden: "<<info[0].x<<", "<<info[0].y<<" radius: "<<info[0].radius<<" Rating: "<<info[0].rating<<endl);
        return true;
    }
}

bool test_goal_info(const GoalInfo& info){
    if(info.found()) {
        for(const GoalPost& post: info.posts) {
            L_DEBUG(cout<<"Goal Post an "<<post.x<<", "<<post.y <<" gefunden"<<endl);
        }
    } else {
        L_DEBUG(cout<<"Kein Tor gefunden"<<endl);
    }
    return info.found();
}

void do_profiling_test() {
    int iterations,it,sleeptime;
    bool recalibrate_ball = false;
    L_DEBUG(cout<<"Wie oft soll die Vision iterieren?"<<endl);
    cin>>iterations;
    L_DEBUG(cout<<"Wie lange soll zwischen den Iterationen pausiert werden?"<<endl);
    cin>>sleeptime;
    iterations = iterations < 1? (-iterations < 1? 1: -iterations) : iterations;
    make_adapter();
    VAdapter& adapter = *adapter_ptr;

    make_vision();
    RVision& vision = *vision_ptr;

    //Configure the vision
    vision.set_b_w_debug_image(false);
    vision.set_ball_enabled(true);
    Eigen::Matrix<char, Eigen::Dynamic, Eigen::Dynamic> color_config = Eigen::Matrix<char, Eigen::Dynamic, Eigen::Dynamic>::Zero(256,768);
    vision.set_color_config(color_config);

    L_DEBUG(cout<<"Starte "<<iterations<<" Durchläufe"<<endl);
    it = iterations;
    boost::posix_time::ptime b = boost::posix_time::microsec_clock::local_time();
    while(iterations--){
        if(recalibrate_ball){L_DEBUG(cout<<"Forciere Rekalibrierung"<<endl);}
        vision.process(adapter,recalibrate_ball,false);
        test_ball_info(vision.get_ball_info());
        //recalibrate the ball color evry fifth iteration
        recalibrate_ball = (((it - iterations) % 5) == 0)? true: false;
        sleep(sleeptime);
    }
    L_DEBUG(boost::posix_time::ptime e = boost::posix_time::microsec_clock::local_time());
    L_DEBUG(cout<<"Die "<<it<<" Iterationen der Vision benötigten "<<e-b<<" s"<<endl);
}

TEST(Vision, MakeStuff) {
    make_adapter();
    make_vision();

    del_adapter_and_vision();
}

TEST(Vision, ball_found_in_testimage) {
    make_adapter();
    make_vision();
    RVision& vision = * vision_ptr;
    VAdapter& adapter = * adapter_ptr;
    disable_vision_options();
    vision.set_ball_enabled(true);
    for(int i = 0; i < 2; ++i) {
        //waiting for green calibration
        L_DEBUG(cout<<"Next Picture"<<endl);
        vision.process(adapter, false, false);
        SLEEP;
    }
    bool ball_found = false;
    for(int i = 0; i < 5 && ! ball_found; ++i) {
        L_DEBUG(cout<<"Search Ball"<<endl);
        vision.process(adapter, true, false);
        SLEEP;
        L_DEBUG(cout<<"Test Recalibration"<<endl);
        vision.process(adapter, false, false);
        const vector<BallInfo>& ball = vision.get_ball_info();
        SLEEP;
        ball_found = test_ball_info(ball);
    }
    ASSERT_TRUE(ball_found);
    del_adapter_and_vision();
    EXPECT_EQ(vision_ptr, nullptr);
    EXPECT_EQ(adapter_ptr, nullptr);
}

TEST(Vision, goal_found_in_testimage) {
    make_adapter();
    make_vision();
    RVision& vision = * vision_ptr;
    VAdapter& adapter = * adapter_ptr;
    disable_vision_options();
    vision.set_goals_enabled(true);
    RMatrixXb color_config = load_single_color_config(default_yellow_config, COLOR_MASK_TYPE::YELLOW);
    vision.set_color_config(color_config);
    bool goal_found = false;
    L_DEBUG(cout<<"Search Goal"<<endl);
    for(int i = 0; i < 5 && ! goal_found; ++i) {
        //waiting for green calibration
        L_DEBUG(cout<<"Next Picture"<<endl);
        vision.process(adapter, false, false);
        SLEEP;
        const GoalInfo& goal = vision.get_goal_info();
        goal_found = test_goal_info(goal);
        SLEEP;
    }
    ASSERT_TRUE(goal_found);
    del_adapter_and_vision();
    EXPECT_EQ(vision_ptr, nullptr);
    EXPECT_EQ(adapter_ptr, nullptr);
}

TEST(Vision, load_default_color_config) {
    RMatrixXb config = load_single_color_config(default_yellow_config, Vision::COLOR_MASK_TYPE::YELLOW);
    ASSERT_TRUE((config.array() > 0).any());
    config *=4;
    write_png_file("/tmp/conf.png",config.cast<uint8_t>());
}

TEST(Vision, CleanUp) {
    delete vision_ptr;
    delete adapter_ptr;
    delete image_ptr;
    vision_ptr = nullptr;
    adapter_ptr = nullptr;
    image_ptr = nullptr;
}

} //namespace Test

using namespace Test;

int main(int argc, char** argv) {
    #ifdef PROFILING_ONLY
    do_profiling_test();
    return EXIT_SUCCESS;
    #endif
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
