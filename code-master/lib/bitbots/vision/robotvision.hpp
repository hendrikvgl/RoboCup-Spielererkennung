#ifndef _ROBOTVISION_HPP
#define _ROBOTVISION_HPP

#include <Eigen/Core>
#include <Eigen/Eigenvalues>
#include <Eigen/StdVector>

#include <boost/tuple/tuple.hpp>
#include <boost/format.hpp>

#include <iostream>
#include <math.h>
#include <algorithm>

#include "sample.hpp"
#include "common_type_definitions.hpp"
#include "pointcloud.hpp"
#include "fitcircle.hpp"
#include "simple_vectorizer.hpp"
#include "binariser.hpp"
#include "adapter.hpp"

//There was an error at compiletime with the macro
#define CHANGE_IF_DEBUG_FOR_ROBOTVISION
#include "../debug/debugmacro.h"

#ifndef unlikely
    #define likely(x)       __builtin_expect((x),1)
    #define unlikely(x)     __builtin_expect((x),0)
    #define unlikely_UNDEFINE
#endif


#ifndef VISION_ADAPBER_LIST
    /*It's important that this is a comma separated list with the number of used adapters at the first index. The adapters MUST be in namespace Vision::Adapter*/
    #define VISION_ADAPBER_LIST 6, RawYUYVAdapter, RGBYUVAdapter, IYUVAdapter, BGRYUVAdapter, InvertedPictureAdapter< ::Vision::Adapter::RawYUYVAdapter>, InvertedPictureAdapter< ::Vision::Adapter::RGBYUVAdapter>
    // We use RawYUYVAdapter as default adapter, the BGRYUVAdapter is used when working with test png files, the simulator enforces the RGBYUVAdapter and the IYUVAdapter
    // was targeted to be the new adapter if camera can handle this format. The InvertedPictureAdapter s are for test issues.
#endif

#define VISION_DEFINE_PROCESS_MACROS
#include "robotvision_process_declaration_macro.hpp"
#undef VISION_DEFINE_PROCESS_MACROS

/*
 * Im virtual-env config: share/darwin/config.json
 * Um diheaddee Vorlagen der Linien-, Ballerkennung auszuwählen
 */
namespace Eigen {
    typedef Matrix<char, Dynamic, Dynamic, RowMajor> MatrixXb;
    //typedef Matrix<unsigned char, Dynamic, Dynamic, RowMajor> RMatrixXb;
}


/*
 * ccw Winkelmethode aus der Masterarbeit. Überpüft, ob der von den drei Parametervektoren eingeschlossene Winkel im oder gegen
 * den Uhrzeigersinn läuft. Keine Ahnung ob + oder - für im Uhrzeigersinn steht.
 */
template<class T>
inline T ccw_f(T v_0x, T v_0y, T v_1x, T v_1y, T v_2x, T v_2y)
{
    return (v_1x - v_0x) * (v_2y - v_0y) - (v_2x - v_0x) * (v_1y - v_0y);
}

namespace Vision {
    namespace pa = Debug::Paint;

namespace Info {
/**
    In dieser Struktur werden die Ergebnisse der Ballerkennung gespeichert
*/
struct BallInfo {
    float x, y, radius;
    float rating;

    BallInfo() : rating(-1) {}

    inline Eigen::Vector2f pos() const {
        return Eigen::Vector2f(x,y);
    }
    inline void set_pos(const Eigen::Vector2f pos) {
        x = pos.x();
        y = pos.y();
    }

    #define OPERATOR_DEFINE(OP) \
    friend bool operator OP (const BallInfo& fst, const BallInfo& sec) { \
        return fst.rating OP sec.rating; \
    }
    OPERATOR_DEFINE(<)
    OPERATOR_DEFINE(>)
    OPERATOR_DEFINE(==)
    OPERATOR_DEFINE(!=)
};

/**
    Info über Tore
*/
struct GoalPost {
    float x, y, abs_width, abs_height;
    int px_x, px_y, width, rating, height;
    bool is_foot_point_in_field;

    GoalPost(float x, float y, int px_x, int px_y, int width, int height, bool is_foot_point_in_field, int rating, int abs_width, int abs_height)
        : x(x), y(y), abs_width(abs_width), abs_height(abs_height), px_x(px_x), px_y(px_y), width(width), rating(rating), height(height), is_foot_point_in_field(is_foot_point_in_field) {
    }

    // Sort post, so that posts in the field come before those outside.
    bool operator<(const GoalPost& other) const {
        return is_foot_point_in_field == other.is_foot_point_in_field? rating > other.rating : is_foot_point_in_field;
    }
};

struct GoalInfo {
    std::string color;
    std::vector<GoalPost> posts;

    GoalInfo(const std::string& color = "")
        : color(color) {
    }

    bool found() const { return posts.size() > 0; };
};

struct Obstacle {
    EIGEN_MAKE_ALIGNED_OPERATOR_NEW
    Eigen::Vector2f pos_l, pos_r;
    int diff_l, diff_r;
    Obstacle()
    : pos_l(Eigen::Vector2f::Zero()), pos_r(Eigen::Vector2f::Zero()), diff_l(0), diff_r(0)
    {}
    Obstacle(const Eigen::Vector2f& pos_l, const Eigen::Vector2f& pos_r, int diff_l, int diff_r)
    : pos_l(pos_l), pos_r(pos_r), diff_l(diff_l), diff_r(diff_r)
    {}
};

struct RobotData {
    enum DataType{undefined_obstacle = 0, magenta = 1, much_magenta = 2, cyan = 4, much_cyan = 8, mixed = 16};
    float x,y,w,h;
    int potential_cyan, potential_magenta;
    DataType result;
    RobotData()
    :x(0),y(0),w(0),h(0), potential_cyan(0), potential_magenta(0), result(undefined_obstacle)
    {}

};

struct ImageData{
    int mean_y, mean_u, mean_v;
};

} } // namespace Vision::Info

EIGEN_DEFINE_STL_VECTOR_SPECIALIZATION(Vision::Info::Obstacle)

namespace Vision {

enum COLOR_MASK_TYPE {BALL=0x1, CYAN = 0x2, YELLOW = 0x4, CARPET = 0x8, WHITE = 0x10, MAGENTA = 0x20, IGNORE_COLOR = 0x40, ALL = 0x7F};
/**
    Bilderkennung für den Roboter;
*/
class RobotVision {
public:
    EIGEN_MAKE_ALIGNED_OPERATOR_NEW

    int current_horizon()const {
        return m_current_horizon;
    }

    Eigen::Vector2f get_relative_horizon() const;

private:
    mutable Debug::Scope m_debug;
    std::vector<pa::Shape> m_debug_shapes;
    std::vector<Sample::LineSample> m_line_points;

    bool is_fieldcolor(int v,int v_max,int Tc)const;
    int get_array_max(int hist[]);
    int get_array_max_gewichtet(int hist[]);

    MonteCarlo::PointCloudProvider<Cloud> m_clouds_normal;
    MonteCarlo::PointCloudProvider<Cloud> m_clouds_high;
    MonteCarlo::PointCloudProvider<Cloud> m_clouds_max;

    std::vector<Info::BallInfo> m_ball_info;
    Info::GoalInfo m_yellow_goal_info;
    std::vector<Info::Obstacle> m_obstacles;
    std::vector<Info::RobotData> m_team_marker_data;

    std::list<ObstacleDetection::Pylon> m_pylons;
    std::list<ObstacleDetection::ShapeVector> m_shape_vectors;

    enum Constants{ sample_horizon_offset=25, sample_horizon_skip=51,
                    WHITE_NO_CONFIG_THRESHOLD=125,
                    NUMBER_SCANLINES=26, VERT_SEARCH_INTERV=20,
                    Q_BIN = 4,
    };
    Eigen::MatrixXb m_color_config;
    Eigen::MatrixXb m_orig_color_config;
    bool m_ball_enabled;
    bool m_goals_enabled;
    bool m_lines_enabled;
    bool m_shape_vectors_enabled;
    bool m_pylons_enabled; //only if shape_vectors_enabled
    bool m_incremental_ball_color_config;
    bool m_team_marker_enabled;
    bool m_vision_normal_b_w_debug;
    bool m_ball_pos_is_ball_footpoint;
    int m_debug_skip_frames;
    int m_debug_frame_nr;
    int m_cfv_counter;
    int m_cfv_counter_limit;
    int m_max_y;
    int m_max_u;
    int m_max_v;
    int m_max_v_old;
    int m_threshold_y;
    int m_threshold_u;
    int m_threshold_v;
    int m_threshold_u_original;
    unsigned m_min_intensity;
    unsigned m_max_intensity;
    float m_rgb_step_factor;
    bool m_dynamic_threshod;
    int m_current_horizon;//fields for exporting the horizon
    int m_centered_horizon, m_horizon_estimated_derivate;
    int m_iboundary_points;
    int m_field_boundary_coordinates[2][NUMBER_SCANLINES + 1];
    int m_height, m_width;
    char m_camera_exposure_wish;
    Eigen::Vector2i m_robo_horizon;
    unsigned m_new_ignore_color_mask_hits;

    template <class T>
    inline int get_pixel_type(const Eigen::Matrix<T, 3, 1>& yuv) const;
    inline Eigen::Vector2f transform_image_point_to_relative(const Eigen::Vector2f point, const Eigen::Vector2f& size) const;

    template<class ImageType>
    void find_horizon(const ImageType & input);

    void calculate_horizon(Eigen::Vector2i* erste_feld_Punkte, unsigned int length);

    bool is_point_in_field(const Eigen::Vector2i& point)const;
    bool is_point_in_field(const Eigen::Vector2f& point)const;

    template<class ImageType,class SampleType, bool use_distance>
    void process_ball(const ImageType& input, const Cloud& cloud,
         const std::vector<SampleType>& samples, const std::vector<LineClusteringSampleType>& orange_samples, const bool recalibrate = false);

    template<class ImageType>
    void process_goals(const ImageType& input, Info::GoalInfo& info);

    template<class ImageType>
    void process_lines(const ImageType& input, const Cloud& cloud,
                       const std::vector<LineClusteringSampleType>& samples);

    template<class ImageType>
    Eigen::Vector2f find_yellow_green_border(const ImageType& input, const Eigen::Vector2f& base_point, int width);


    template<class ImageType>
    void process_team_markers(const ImageType& input, const Cloud& cloud,
                              const std::vector<Sample::ColorColorSample>& rest_samples);

    template<class ImageType>
    void process_shape_vectors(const ImageType& image);

    template<class ImageType>
    inline Eigen::Vector3i get_mean_color(const ImageType& input, const Eigen::Vector2i& pos) const;

    inline bool check_color_mask(const Eigen::Vector3i& yuv, int mask) const;

    template<class ImageType, bool ignore_carpet>
    void filter_samples(const ImageType& input, const Cloud& cloud,
            std::vector<Sample::VisionSample>& ball_samples,
            std::vector<Sample::VisionSample>& orange_ball_samples,
            std::vector<LineClusteringSampleType>& line_samples,
            std::vector<Sample::ColorColorSample>& rest_samples,
            const bool recalibrate_ball_color);

    void init(int y, int u, int v, bool dynamic)
    {
        init_cfv_flags(y, u, v, dynamic);

        //Diese Werte werden im normalbetrieb von der Config überschrieben
        m_ball_enabled = true;
        m_goals_enabled = true;
        m_lines_enabled = true;
        m_pylons_enabled = false;
        m_shape_vectors_enabled = false;
        m_team_marker_enabled = true;

        //Range of Image intensity in which the robot will not request an other camera exposure
        m_min_intensity = 80;
        m_max_intensity = 110;

        // Erstmal jedes fünfte Bild senden
        m_debug_skip_frames = 5;
        m_debug_frame_nr = 100;

        m_cfv_counter = -1;
        m_cfv_counter_limit = 8;
        m_current_horizon = 0;
        m_incremental_ball_color_config = false;
        m_vision_normal_b_w_debug = true;
        m_ball_pos_is_ball_footpoint = false;
        m_rgb_step_factor = 2;
        m_robo_horizon = Eigen::Vector2i::Zero();

        // Rausfinden wie oft debug-Bilder gesendet werden sollten
        const char* envvar = getenv("VISION_DEBUG_FRAME_SKIP");
        if (envvar != NULL){
            int skip = atoi(envvar);
            if(skip >= 0) {
                m_debug_skip_frames = skip;
            }
        }

        //rausfinden ob vision spezifisches debug aktiv is
        if(m_debug && !debug_vision) {
            DEBUG_LOG(1, "Um Vision-Debug zu sehen, bitte VISION_DEBUG=1 setzen!");
        }
        for (int i = 0; i <= NUMBER_SCANLINES; ++i)//für die Felderkennung Defaultwerte setzen
        {
            m_field_boundary_coordinates[0][i] = 0;
            m_field_boundary_coordinates[1][i] = 0;
        }
        m_iboundary_points = 0;
        m_camera_exposure_wish = 0;
    }

    void init_cfv_flags(int y, int u, int v, bool dynamic) {
        m_max_intensity = m_max_u = m_max_v = m_max_v_old = m_max_y = 0;
        m_threshold_y = y;
        m_threshold_u = u;
        m_threshold_u_original = u;
        m_threshold_v = v;
        m_dynamic_threshod = dynamic;
    }

    template<class ImageType, class SampleType, class Cluster, bool  use_distance>
    void recalibrate_ball_color_config(const ImageType& input, const Cluster& ball_cluster
    , const float radius, const Eigen::Vector2i& midpoint);

    /**
     * \brief The main routine of image processing.
     *
     * This method is the internal template specialized forward of the process methods.
     * In order to enable the separation of our vision in header and implementation we decided us for this solution.
     * The public vision interface contains several fixed type process methods that this private method.
     * These public interface process methods are organized by the VISION_PROCESS_FOR_HEADER macro and the VISION_ADAPBER_LIST.
     * Please read the docs in robotvision_process_declaration_macro.hpp for further information.
     * This way, all the internal process methods are template based using an "ImageType" as input. This is in fact any adapter from adapter.hpp
     */
    template<class ImageType>
    void process_intern(const ImageType& input, const bool recalibrate_ball_color = false, bool ignore_carpet = false);

    /*
     * This method will be called from implicit defined forward methods to enable the template parameter.
     * This method should gather image information and collect them in a struct. That shall be used to tweak camera parameters.
     */
    template<class ImageType>
    Info::ImageData get_image_data_intern(const ImageType input) const;
    template<class ImageType>
    void find_horizon_obstacles(const ImageType& input, const Eigen::Vector2i* erste_feld_Punkte, unsigned int length);

public:
    RobotVision(int y, int u, int v, bool dynamic, int width, int height);

    RobotVision(int width, int height);

    ~RobotVision();

    void reset_vision_to_defaults() {
        init(m_threshold_y, m_threshold_u_original, m_threshold_v, m_dynamic_threshod);
    }

    void set_carpet_threshold(int y, int u, int v)
    {
        m_threshold_y = y;
        m_threshold_u = u;
        m_threshold_u_original = u;
        m_threshold_v = v;
    }

    template<class Derived>
    void set_color_config(const Eigen::DenseBase<Derived>& color_config) {
        this->m_color_config = color_config;
        this->m_orig_color_config = color_config;
    }

    /**
     * This method returns a colour masq belonging to a given masq
     * \param masq: requested colour masq
     * \return The color masq with values set to 127 or 0
     */
    Eigen::MatrixXb get_color_config(const COLOR_MASK_TYPE masq){
        Eigen::MatrixXb config = Eigen::MatrixXb::Zero(256,768);
        for(int i = 0; i < 256; ++i){
            for(int j = 0; j < 768; ++j){
                config(i,j) = (m_color_config(i,j) & masq)? 127 : 0;
            }
        }
        return config;
    }
    /*
    void add_to_color_config(Eigen::Matrix<char, Eigen::Dynamic, Eigen::Dynamic> color_config) {
        this->color_config += color_config;
    }
    */
    void add_to_color_config(int x, int y, int flag)
    {
        m_color_config(x,y) |= flag;
    }

    /*void reset_color_config() {
        //this->color_config = this->m_orig_color_config;
    }*/

    void remove_color_config(const int masq){
        const int inverse_masq = ~masq;
        //Eigen Matrizen liegen Spaltenweise im Speicher; per Default,
        for(unsigned int i = 0; i < 256; ++i){
            for(unsigned int j = 0; j < 256; ++j){
                //Entfernt die Ballmaske aus der Color Config, indem mit der Bitweise Invertierten Ballmaske verunded wird
                m_color_config(j,i) &= inverse_masq;
                m_color_config(j,i+256) &= inverse_masq;
                m_color_config(j,i+512) &= inverse_masq;
            }
        }
    }

    void set_dynamic_u_threshold(const bool dynamic) {
        m_dynamic_threshod = dynamic;
    }
    void set_ball_enabled(const bool enabled) {
        m_ball_enabled = enabled;
    }
    void set_goals_enabled (const bool enabled) {
        m_goals_enabled = enabled;
    }
    void set_lines_enabled(const bool enabled) {
        m_lines_enabled = enabled;
    }
    void set_pylons_enabled(const bool enabled) {
        m_pylons_enabled = enabled;
    }
    void set_team_marker_enabled(const bool enabled) {
        m_team_marker_enabled = enabled;
    }
    void set_shape_vectors_enabled(const bool enabled) {
        m_shape_vectors_enabled = enabled;
    }
    void set_b_w_debug_image(const bool enabled) {
        m_vision_normal_b_w_debug = enabled;
    }
    void set_ball_pos_is_ball_footpoint(const bool enabled) {
        m_ball_pos_is_ball_footpoint = enabled;
    }
    void set_rgb_step_factor(const float factor) {
        m_rgb_step_factor = factor;
    }
    void set_min_intensity(const int min_intensity){
        m_min_intensity = min_intensity;
    }
    void set_max_intensity(const int max_intensity){
        m_max_intensity = max_intensity;
    }
    void set_incremental_ball_color_config(bool incremental){
        m_incremental_ball_color_config = incremental;
    }
    void set_robo_horizon(const Eigen::Vector2f& horizon) {
        m_robo_horizon = Eigen::Vector2i((int)((((horizon(0) + horizon(1)) * m_width)) + (m_height>>1)),
                                         (int)((((horizon(0) - horizon(1)) * m_width)) + (m_height>>1)));
        L_DEBUG(std::cout<<"Robo horizon"<<std::endl<<(Eigen::Matrix2f()<<m_robo_horizon.cast<float>(), horizon).finished()<<std::endl);
    }

    char get_camera_exposure_whish(){
        char cew = m_camera_exposure_wish;
        m_camera_exposure_wish = 0;
        return cew;
    }

    // in cython I want to use the references or pointer to the internal vision data member, but
    // cythond doesn't really perform with const pointers, so I use an empty define to show my good will
    #define CONST

    CONST std::vector<Info::BallInfo>& get_ball_info() CONST {
        return m_ball_info;
    }

    CONST Info::GoalInfo& get_goal_info() CONST {
        return m_yellow_goal_info;
    }

    CONST std::vector<Info::Obstacle>& get_obstacles() CONST {
        return m_obstacles;
    }

    CONST std::vector<Info::RobotData>& get_team_marker() CONST {
        return m_team_marker_data;
    }

    CONST std::list<ObstacleDetection::Pylon>& get_pylons() CONST {
        return m_pylons;
    }

    CONST std::list<ObstacleDetection::ShapeVector>& get_shape_vectors() CONST {
        return m_shape_vectors;
    }

    CONST std::vector<pa::Shape>& get_debug_shapes() CONST {
        return m_debug_shapes;
    }

    CONST std::vector<Sample::LineSample>& get_line_points() CONST {
        return m_line_points;
    }
    #undef CONST

    int get_ignore_masq_hits() const {
        return m_new_ignore_color_mask_hits;
    }

    /**
     * \brief This is the macro generated process interface for our image processing
     *
     * This is the Macro declaration for the workaround to split the robotvision into two files although the process
     * methods are template based. The macro is in "robotvision_process_declaration_macro.hpp".
     * Now for every template of the process this macro generates a fix type process method.
     * The counter part in robotvision.cpp generates the fix typed implementation forwarding to the template based process method
     */
    VISION_PROCESS_FOR_HEADER
    VISION_GET_IMAGE_DATA_FOR_HEADER
};

// Wieder aufräumen, falls wir die Makros selbst definiert haben.
#ifdef unlikely_UNDEFINE
    #undef unlikely
    #undef likely
#endif

#undef debug_shapes
#undef foreach

// namespace
}

#endif

