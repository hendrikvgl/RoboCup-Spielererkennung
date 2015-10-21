#include <Eigen/Core>
#include <Eigen/Eigenvalues>

#include <boost/tuple/tuple.hpp>
#include <boost/format.hpp>

#include <utility>
#include <iostream>
#include <math.h>
#include <algorithm>

#include "../util/eigen_util.hpp"
#include "pointcloud.hpp"
#include "robotvision.hpp"

#include "sample.hpp"
#include "dbscan.hpp"
#include "common_type_definitions.hpp"
#include "fitcircle.hpp"
#include "simple_vectorizer.hpp"
#include "binariser.hpp"

//There was an error at compiletime with the macro
#define CHANGE_IF_DEBUG_FOR_ROBOTVISION
#include "../debug/debugmacro.h"

#ifndef unlikely
    #define likely(x)       __builtin_expect((x),1)
    #define unlikely(x)     __builtin_expect((x),0)
    #define unlikely_UNDEFINE
#endif


using namespace Vision;
using namespace Vision::Adapter;
using namespace Vision::Sample;
using namespace Vision::ObstacleDetection;
using namespace Eigen;
using namespace std;

typedef vector<std::reference_wrapper<const ColorSample> > ColorSampleVector;
template<class SampleType, bool use_distance>
using SpartialClusteringType = Scanning::SpatialClustering<Cloud, SampleType, use_distance, false>;
typedef Scanning::SpatialClustering<Cloud, LineClusteringSampleType, line_clustering_uses_distances, true> SpartialLineClusteringType;

#define foreach BOOST_FOREACH

#define __ROBOTVISION_UTILS_HPP
#include "robotvision-utils.hpp"
#undef __ROBOTVISION_UTILS_HPP


/*This is the Macro declaration for the workaround to split the robotvision into two files although the process
 * methods are template based. The macro is in "robotvision_process_declaration_macro.hpp".
 * Now, for every template of the process this macro generates the fix typed implementation forwarding to the template based process method
 * The counter part in robotvision.hpp generates the fix typed implementation forwarding to the template based process method a fix type process method.
 */
VISION_PROCESS_FOR_IMPL
VISION_GET_IMAGE_DATA_FOR_IMPL

RobotVision::RobotVision(int y, int u, int v, bool dynamic, int width, int height)
: m_debug("Vision"),
//m_cyan_team_marker("Cyan"),
//m_magenta_team_marker("Magenta"),
m_clouds_normal(width, height, 3, 0.6, 0.05),//Drei verschiedene Cloudarten um den Genauigkeitsbereich zu variieren
m_clouds_high(width, height, 3, 0.4, 0.05),/* TODO evaluate these cloud parameters*/
m_clouds_max(width, height, 3, 0.2),/* da wir keine Zeit zur evaluation neuer Werte haben*/
m_yellow_goal_info("Yellow"), m_height(height), m_width(width) {
    this->init(y,u,v, dynamic);
    PRINT_DEBUG_INFO;
}

RobotVision::RobotVision(int width, int height)
: RobotVision(70, 20, 30, true, width, height)
{}

//INDEPENDENT TODO
int RobotVision::get_array_max_gewichtet(int hist[])
{
    int max = 0;
    int result = 0;
    int i;
    int tmp;
    for(i=0;i<256/Q_BIN;i++)
    {
        //tmp = hist[i] * MAX(0,128-(i*Q_BIN)); // MAX war plötzlich nicht mehr definiert ...
        tmp = 128-(i*Q_BIN);
        tmp = tmp > 0 ? hist[i] * tmp : 0;
        if (tmp > max)
        {
            max = tmp;
            result = i*Q_BIN + (Q_BIN / 2);
        }
    }
    return result;
}

//INDEPENDENT TODO
int RobotVision::get_array_max(int hist[])
{
    int max = 0;
    int result = 0;
    int i;
    for(i=0;i<256/Q_BIN;i++)
    {
        if (hist[i] > max)
        {
            max = hist[i];
            result = i*Q_BIN + (Q_BIN / 2);
        }
    }
    return result;
}

//INDEPENDENT TODO
bool inline RobotVision::is_fieldcolor(int v,int v_max,int Tc) const
{
    return abs(v-v_max) < Tc;
}

template<class T>
inline int RobotVision::get_pixel_type(const Matrix<T, 3, 1>& yuv) const{
    const int type_yu = m_color_config(yuv(0), yuv(1));
    const int type_yv = m_color_config(yuv(0), 256 + yuv(2));
    const int type_uv = m_color_config(yuv(1), 512 + yuv(2));
    const int type = type_yv & type_yu & type_uv;
    return type;
}

/**
    Filtert Samples nach der gegebenen PointCloud aus der Eingabe und
    packt sie in die entsprechenden Vektoren
*/
template<class ImageType, bool ignore_carpet>
void RobotVision::filter_samples(const ImageType& input, const Cloud& cloud,
        vector<VisionSample>& ball_samples,
        vector<VisionSample>& orange_ball_samples,
        vector<LineClusteringSampleType>& line_samples,
        vector<ColorColorSample>& rest_samples,
        const bool recalibrate_ball_color) {

    m_new_ignore_color_mask_hits = 0;
    ball_samples.reserve(cloud.size()/8);
    line_samples.reserve(cloud.size()/8);
    rest_samples.reserve(cloud.size()/4);

    m_cfv_counter++;
    DEBUG(INFO,"m_cfv_counter", m_cfv_counter);
    if (unlikely(m_cfv_counter > m_cfv_counter_limit)) //cfv alle 30 Frames machen
    {
        m_cfv_counter = 0;
        m_cfv_counter_limit = m_cfv_counter_limit < 100 ? 1.5 * m_cfv_counter_limit : m_cfv_counter_limit;
    }
    int max_u_old, max_y_old;
    int hist_y[(256/Q_BIN)+2]; // /Q_BIN
    int hist_u[(256/Q_BIN)+2]; // /Q_BIN
    int hist_v[(256/Q_BIN)+2]; // /Q_BIN
    if (unlikely(m_cfv_counter < 2))
    {
        for (int i = 0; i< 256/Q_BIN; i++)
        {
          hist_y[i]=0;
          hist_u[i]=0;
          hist_v[i]=0;
        }
    }
    unsigned sum_v = 0, num_skipped_pixel = 0;//TODO test auf durchschnittliche Helligkeitswerte
    const int horinzon_border = max<int>(m_current_horizon - sample_horizon_offset, m_robo_horizon.minCoeff());
    DEBUG_SHAPES(INFO, pa::line(0,m_robo_horizon.x(), m_width, m_robo_horizon.y(), pa::Green));
    bool skip_samples_over_horizon = true;
    DEBUG(INFO, "Max_Green", m_max_v);
    for(int i = 0; i < cloud.size(); i++) {
        const Vector2i& pos = cloud.get_point(i).get_position();
        //DEBUG_SHAPES(3, pa::dot(pos, pa::White));continue;//Nur zur Cloud-Evaluation hier drin

        if(unlikely(pos.x() >= input.get_width() || pos.y() >= input.get_height()))
        {
            // Punkte außerhalb des Bildbereichs ignorieren
            DEBUG_LOG(WARN,"Punkt außerhalb des Bildes x: "<< pos.x() <<"("<<input.get_width()<<")  y: " << pos.y()<<"("<< input.get_height() <<")");
            continue;
        }
        if(skip_samples_over_horizon && pos.y() < horinzon_border) {
                /*&& likely(m_cfv_counter >= 2 ) && likely(!recalibrate_ball_color)){*/
                    //Bei der Ballrecalibrierung nur Feldpunkte beachten
            //TODO evaluieren, ob wir, solange wir noch über dem Horizont liegen, "vorspulen" wollen
            i+=sample_horizon_skip;
            //Ignore Samples over horizon line
            num_skipped_pixel = i;
            continue;
        }
        skip_samples_over_horizon = false;
        const Vector3i yuv = get_mean_color(input, pos);
        sum_v += input(pos)[0];//TODO test auf durchschnittliche Helligkeitswerte

        if (unlikely(m_cfv_counter == 1))
        {
            if (is_fieldcolor(yuv(2),m_max_v,m_threshold_v))
            {
                hist_y[static_cast<int>(yuv(0) / Q_BIN)]++;
                hist_u[static_cast<int>(yuv(1) / Q_BIN)]++;
                //DEBUG_SHAPES(EXPENSIVE, pa::dot(pos, pa::Red));
            }
        }
        if (unlikely(m_cfv_counter == 0))
        {
            // collecte das histogram für green
            hist_v[static_cast<int>(yuv(2) / Q_BIN)]++;
        }

        const int type = get_pixel_type(yuv);

//         if(pos.x() > 450 && pos.x() < 500) {
//             DEBUG_SHAPES(NEW_FEATURE, pa::dot(pos, pa::Green));//Nur zur Cloud-Evaluation hier drin
//         }

        if(!ignore_carpet && likely(type & CARPET))
        {
            continue;
        }
        // This is a rapidly developed feature. The aim of this feature is to calibrate some disturbing colors to ignore them, as the tables in joao pessoa
        if(type & IGNORE_COLOR) {
            ++m_new_ignore_color_mask_hits;
            continue;
        }

        if(likely(m_ball_enabled) && likely(!recalibrate_ball_color) && unlikely(type & WHITE)) {
            orange_ball_samples.emplace_back(pos, i);
            DEBUG_SHAPES(IMPORTANT, pa::point(pos, pa::Yellow));
            continue;
        }

        if(likely(m_ball_enabled) && likely(!recalibrate_ball_color) && unlikely(type & BALL)) {
            ball_samples.emplace_back(pos, i);
            DEBUG_SHAPES(EXPENSIVE, pa::dot(pos, pa::Yellow));
            continue;
        }
        if(unlikely(m_lines_enabled) && input(pos)[0] > 140) {
            line_samples.emplace_back(pos, i);
        }
        //brightness bigger than 127
        if(input(pos)[0] > 200 || type & BALL){
            ball_samples.emplace_back(pos, i);
            DEBUG_SHAPES(EXPENSIVE, pa::dot(pos, pa::Yellow));
            continue;
        }
    }
    DEBUG(INFO, "Average v", sum_v / Cloud::n); //TODO test der durchschnittlichen Hellikkeitswerte
    if (unlikely(m_cfv_counter == 0))
    {
        m_max_v_old = m_max_v;
        m_max_v = get_array_max_gewichtet(hist_v);
        DEBUG_LOG(INFO, "Set max_v neu");
        if(m_dynamic_threshod)
        {
            //ob das so gut geht?
            m_threshold_u = m_threshold_u_original - ((m_max_v-80) * 0.5);
        }
        DEBUG_LOG(INFO, "m_threshold_u " << m_threshold_u << " Dynamic component: " << ((m_max_v-80) * 0.5));
    }
    if (unlikely(m_cfv_counter == 1))
    {
        max_u_old = m_max_u;
        max_y_old = m_max_y;
        m_max_y = get_array_max(hist_y);
        m_max_u = get_array_max(hist_u);
        //reset_color_config();
        remove_color_config(CARPET);
        int i,j;
        bool y, u, u2, v;
        for(i=0;i<256;i++)
        {
            for(j=0;j<256;j++)
            {
                y = is_fieldcolor(i,m_max_y,m_threshold_y);
                u = is_fieldcolor(j,m_max_u,m_threshold_u);
                u2 = is_fieldcolor(i,m_max_u,m_threshold_u);
                v = is_fieldcolor(j,m_max_v,m_threshold_v);
                // Y/U
                if(y && u)
                    add_to_color_config(i,j,CARPET);
                if (y && v) // Y/V
                    add_to_color_config(i,j+256,CARPET);
                if (u2 && v) // U/V
                    add_to_color_config(i,j+512,CARPET);

            }
        }
        if(! (  abs(m_max_v - m_max_v_old) < (m_threshold_v / 2) &&
                abs(m_max_u - max_u_old) < (m_threshold_u / 2)   &&
                abs(m_max_y - max_y_old) < (m_threshold_y / 2)))
        {//cfv_stable prüfen, wenn unstable setzt zurück
            m_cfv_counter_limit = m_cfv_counter_limit < 20 ? m_cfv_counter_limit:10;
        }
        //Noch mal wegen dem CAMERA_EXPOSURE_FEATURE was machen
        char exposure_lower = (sum_v / (Cloud::n - num_skipped_pixel)) < m_min_intensity? -1 : 0;//80 und 100 stattdessen?
        char exposure_higher = (sum_v / (Cloud::n - num_skipped_pixel)) > m_max_intensity? 1 : 0;
        m_camera_exposure_wish = exposure_higher + exposure_lower;
        if (m_camera_exposure_wish != 0)
        {
            // wenn wir exposure ändern wollen wir grün demnächst reevaluieren
            m_cfv_counter_limit = m_cfv_counter_limit < 20 ? m_cfv_counter_limit:10;
        }
    }
}

static inline bool can_add_to_color_config(const int fst, const int sec, const int add){
    if(fst < 0 && fst < 256){
        return false;
    }
    if(sec < 0 + add && sec < 256 + add){
        return false;
    }
    return true;
}

template<class ImageType, class SampleType, class Cluster, bool use_distance>
void RobotVision::recalibrate_ball_color_config(const ImageType& input,const Cluster& ball_cluster
                    , const float radius, const Vector2i& midpoint)
{
    //Ein bisschen darüber Normiert, so dass bei Großen Bällen der Rande eher vernachlässigt wird; 'radius_norm' nimmt Werte von (0,1) an
    //Do we still need this, we use Color distances in yuyv-color-space
    const float radius_norm = use_distance? 0 : (1 / sqrt(1 + radius / 42.0));
    remove_color_config(BALL);
    foreach(const SampleType& sample, ball_cluster)
    {
        //Es geht auch inline ;) Bestimmt im Fall 'use_distance', ob der betrachtete Punkt zu weit von Midpoint entfernt ist
        if(!use_distance && (static_cast<Vector2i>(sample.vector() - midpoint)).cast<float>().norm() > (radius * radius_norm)){
            continue;
        }

        //For every point of the cluster, add a 21*11*11 Cuboid in yuyv-color-space to the "new" color config
        Vector3i yuv = get_mean_color(input, sample);
        for(int i = -10; i <= 10; ++i){
            for(int j = -5; j <= 5; ++j){
                if(can_add_to_color_config(yuv(0) + i, yuv(1) + j, 0))
                    add_to_color_config(yuv(0) + i, yuv(1) + j, BALL);
                if(can_add_to_color_config(yuv(0) + i, 256 + yuv(2) + j, 256))
                    add_to_color_config(yuv(0) + i, 256 + yuv(2) + j, BALL);
                if(i < -5 || i > 5)
                    continue;
                if(can_add_to_color_config(yuv(1) + i, 512 + yuv(2) + j, 512))
                    add_to_color_config(yuv(1) + i, 512 + yuv(2) + j, BALL);
            }
        }
    }
}
static const int process_time_buffer_size = 147 * 3;
static float process_time_buffer[process_time_buffer_size];
static int current_process_time_buffer_idx = 0;
const static Map<Matrix<float, process_time_buffer_size, 1> > time_mean_map(process_time_buffer);
static float global_process_time_max = 0;

RobotVision::~RobotVision()
{
    std::cout<<"Mean Time of last frames: "<<time_mean_map.mean()<<std::endl;
    std::cout<<"Max Time of last frames: "<<time_mean_map.maxCoeff()<<std::endl;
    std::cout<<"Global Max Time of last frames: "<<global_process_time_max<<std::endl;
}

/**
    Verarbeitet einen Frame
*/
template<class ImageType>
void RobotVision::process_intern(const ImageType& input, const bool recalibrate_ball_color, const bool ignore_carpet) {
    static_assert(std::is_base_of<AbstractAdapter, ImageType>::value,"Adapter must be an AbstractAdapter");
    DEBUG_TIMER(2, "Process");
    //TODO Durch versuche Anpassen
    // Punktwolke holen // festlegen, wann zwischen den Clouds gewechselt werden soll
    // Feature Toggle für die neuen gedrehten Kameras
    int cloud_to_get;
    cloud_to_get = current_horizon() > 0.5 * m_height ? 1 :(current_horizon() > 0.375 * m_height ? 2 : 3);
    //string cloud_string = cloud_to_get == 1 ? "m_clouds_normal.get()" :(cloud_to_get == 2 ? "m_clouds_high.get()" : "m_clouds_max.get()");
    const Cloud& cloud = cloud_to_get == 1 ? m_clouds_normal.get() :(cloud_to_get == 2 ? m_clouds_high.get() : m_clouds_max.get());// In Abhängigkeit des Horizontes die Cloud anpassen
    //DEBUG_LOG(IMPORTANT, cloud_string);

    m_debug_shapes.clear();
    m_debug_frame_nr = (m_debug_frame_nr + 1) % (m_debug_skip_frames + 1);

    IF_DEBUG(INFO,{
        const int step = 5;

        //Sending the color config as debug image evry third frame, otherwise send the u or v components
        if (m_debug_frame_nr == 0 /*&& (m_cfv_counter+1) % 3*/)
        {
            if(m_vision_normal_b_w_debug) {
                MatrixHolder<RMatrixXUb> mat(input.get_height()/step, input.get_width()/step);
                for(int y = 0; y < mat.rows(); y++) {
                    for(int x = 0; x < mat.cols(); x++) {
                        //mat(y, x) = input(x*step, y*step)((m_cfv_counter+1) % 3);
                        mat(y, x) = input(x*step, y*step)(0);
                    }
                }
                DEBUG(INFO, "DebugImage.Factor", step);
                DEBUG(INFO, "DebugImage.Type", "bw");
                MatrixHolder<RMatrixXUb>& mat_ref(mat);
                DEBUG(INFO, "DebugImage", mat_ref);
            } else {
                const int local_step = m_rgb_step_factor*step;
                MatrixHolder<RMatrixVec3Ub> mat(input.get_height()/local_step, input.get_width()/local_step);
                for(int y = 0; y < mat.rows(); y++) {
                    for(int x = 0; x < mat.cols(); x++) {
                        //mat(y, x) = input(x*local_step, y*local_step)((m_cfv_counter+1) % 3);
                        Vector3f rgb;
                        Vector3f yuv = input(x*local_step, y*local_step).template cast<float>();
                        yuv.tail<2>().array() -= 128;
                        yuv(1) /= Adapter::uconversion;
                        yuv(2) /= Adapter::vconversion;
                        rgb = Adapter::yuv_to_rgb_conversion * yuv;
                        rgb.array().max(Array3f::Zero()).min(Array3f::Constant(255));
                        mat(y, x) = Vector3Ub(rgb(0),rgb(1),rgb(2));
                    }
                }
                DEBUG(INFO, "DebugImage.Factor", local_step);
                DEBUG(INFO, "DebugImage.Type", "rgb");
                MatrixHolder<RMatrixVec3Ub>& mat_ref(mat);
                DEBUG(INFO, "DebugImage",mat_ref);
            }
        }
    });

    vector<VisionSample> ball_samples, orange_ball_samples;
    vector<ColorColorSample> rest_samples;
    vector<LineClusteringSampleType> line_samples;
    {
        DEBUG_TIMER(2, "Process.Horizont");
        find_horizon(input);
    }
    {
        DEBUG_TIMER(2, "Process.FindSamples");
        if(ignore_carpet){
            filter_samples<ImageType, true>(input, cloud,
                ball_samples, orange_ball_samples, line_samples,
                rest_samples, recalibrate_ball_color);
        } else {
            filter_samples<ImageType, false>(input, cloud,
                ball_samples, orange_ball_samples, line_samples,
                rest_samples, recalibrate_ball_color);
        }
    }

    if(m_goals_enabled) {
        DEBUG_TIMER(2, "Process.Goals");
        process_goals(input, m_yellow_goal_info);

        DEBUG(2, "YellowGoal.Found", m_yellow_goal_info.found() ? "yes" : "no");
    }

    if(likely(m_ball_enabled)) {
        DEBUG_TIMER(2, "Process.Ball");
        if (recalibrate_ball_color)
        {
            DEBUG_LOG(2,"Recalibrate ball color config, if found ball");
            process_ball<ImageType, ColorColorSample, true>(input, cloud, rest_samples, orange_ball_samples, recalibrate_ball_color);
        }
        else
        {
            process_ball<ImageType, VisionSample, false>(input, cloud, ball_samples, orange_ball_samples, recalibrate_ball_color);
        }
    }

    if(likely(m_lines_enabled)) {
        DEBUG_TIMER(2, "Process.Lines");
        process_lines(input, cloud, line_samples);
    }

    if(likely(m_team_marker_enabled)) {
        DEBUG_TIMER(IMPORTANT, "Process.Teammarker");
        process_team_markers(input, cloud, rest_samples);
    }

    if(m_shape_vectors_enabled) {
        DEBUG_TIMER(2, "Process.ShapeVectors");
        process_shape_vectors(input);
    }

    DEBUG(2, "DebugImage.Shapes", m_debug_shapes);
    DEBUG(2, "DebugImage.Draw", true);
    float process_time_mean = time_mean_map.mean();
    float process_time_max = time_mean_map.maxCoeff();
    global_process_time_max = std::max(process_time_max, global_process_time_max);
    m_debug("Process.mean") = process_time_mean;
    m_debug("Process.max") = process_time_max;
    m_debug("Process.globalmax") =  global_process_time_max;
    process_time_buffer[(current_process_time_buffer_idx++)%process_time_buffer_size] = timer.current_time();
}


template<class ImageType>
Info::ImageData RobotVision::get_image_data_intern(const ImageType input) const {
    unsigned long sum_y = 0, sum_u = 0, sum_v = 0;
    for(int i = 0; i < input.get_height(); ++i) {
        for(int j = 0; j < input.get_width(); ++j) {
            Vector3i yuv = input(j, i);
            sum_y += yuv(0);
            sum_u += yuv(1);
            sum_v += yuv(2);
        }
    }
    int num_pixel = (input.get_height() * input.get_width());
    Info::ImageData data;
    data.mean_y = static_cast<int>(sum_y / num_pixel);
    data.mean_u = static_cast<int>(sum_u / num_pixel);
    data.mean_v = static_cast<int>(sum_v / num_pixel);
    return data;
}


//INDEPENDENT TODO
template<class ImageType>
inline Vector3i RobotVision::get_mean_color(const ImageType& input, const Vector2i& pos) const {
    if(pos.x() < 3 or pos.x() >= input.get_width() - 3 or pos.y() < 3 or pos.y() >= input.get_height() - 3)
        return input(pos);

    Vector3i color =
        input(pos) +
        input(pos.x(), pos.y() - 2) +
        input(pos.x() + 2, pos.y()) +
        input(pos.x(), pos.y() + 2) +
        input(pos.x() - 2, pos.y()) ;

    return color / 5;
}

inline
bool RobotVision::check_color_mask(const Vector3i& yuv, int mask) const {
    const int type_yu = m_color_config(yuv(0), yuv(1));
    const int type_yv = m_color_config(yuv(0), 256 + yuv(2));
    const int type_uv = m_color_config(yuv(1), 512 + yuv(2));
    return type_yu & type_yv & type_uv & mask;
}

static inline bool is_point_over_horizon_line(const Eigen::Vector2i l, const unsigned width, const Eigen::Vector2i& pos/*, unsigned offset=0*/) {
    if(pos.y()/* + (int)offset*/ > l.maxCoeff())
        return false;
    if(pos.y()/* + (int)offset*/ < l.minCoeff())
        return true;

    return pos.y() /* + (int)offset*/ <
           l.x() + (static_cast<float>(pos.x())) / width * (l.y() - l.x());
}

template<class ImageType>
void RobotVision::find_horizon(const ImageType & input)
{
    unsigned field_hits = 0;
    const int jmax =  (input.get_height() / (VERT_SEARCH_INTERV) * 0.95 );
    Vector2i *erste_feld_Punkte = new Vector2i[NUMBER_SCANLINES]; //Speichere die zum Feld gehörenden Punkte in einem Array
    for (int i = 0; i < NUMBER_SCANLINES ; i++)
    {
        int j = 0;
        //laufe von oben nach unten // und lasse j mehr Spielraum //-2, da zu viele Randpunkte genommen werden
        for (; j < jmax ; ++j)
        {
            const Vector2i checkpos( (input.get_width() - 1) * i / (NUMBER_SCANLINES - 1), j*VERT_SEARCH_INTERV);
            if(is_point_over_horizon_line(m_robo_horizon, m_width, checkpos))
                continue;
            if (check_color_mask(get_mean_color(input, checkpos),CARPET))
            {
                const Vector2i checkpos2( (input.get_width() - 1) * i / (NUMBER_SCANLINES - 1), (j + 1) * VERT_SEARCH_INTERV);
                const Vector2i checkpos3( (input.get_width() - 1) * i / (NUMBER_SCANLINES - 1), (j + 2) * VERT_SEARCH_INTERV);
                if ( (!(check_color_mask(get_mean_color(input, checkpos2), CARPET)))
                    or (!(check_color_mask(get_mean_color(input, checkpos3), CARPET))))
                {
                    // es geht nicht grün weiter, wir suchen mal weiter
                    DEBUG_SHAPES(EXPENSIVE, pa::point(checkpos2,pa::Blue));
                    DEBUG_SHAPES(EXPENSIVE, pa::point(checkpos3,pa::Blue));
                    continue;
                }
                else
                {
                    DEBUG_SHAPES(EXPENSIVE, pa::point(checkpos2,pa::Pink));
                }
                DEBUG_SHAPES(EXPENSIVE, pa::point(checkpos,pa::Yellow));
                Vector2i checkpos_back;
                int way_back = VERT_SEARCH_INTERV * 0.5;
                do {
                    way_back -= VERT_SEARCH_INTERV * 1;
                    checkpos_back = Vector2i((input.get_width() - 1) * i / (NUMBER_SCANLINES - 1), j*VERT_SEARCH_INTERV + way_back);
                    //Feature Toggle für die nun neu gedrehten Kameras
                    const int border_for_search =  0;
                    if(unlikely((j*VERT_SEARCH_INTERV + way_back) <= border_for_search)) // Verarbeitung sicherer machen; keine Pixel außerhalb prüfen
                    {
                        checkpos_back = Vector2i((input.get_width() - 1) * i / (NUMBER_SCANLINES - 1), 0);
                        break; //Bei maximalem j die Schleife verlassen;
                    }
                    DEBUG_SHAPES(INFO, pa::point(checkpos_back,pa::Red));//Autokorrektur: Felderkennung systematisch 20p erhöhen
                } while(check_color_mask(get_mean_color(input, checkpos_back),CARPET));
                erste_feld_Punkte[field_hits] = checkpos_back;
                field_hits++;
                break; //beim ersten Feldpunkt abbrechen
            } else {
                 DEBUG_SHAPES(EXPENSIVE, pa::point(checkpos,pa::Cyan));
            }
        }
    }
    for(int i = 1; i < static_cast<int>(field_hits) - 1; ++i) {
        if(erste_feld_Punkte[i - 1].y() - erste_feld_Punkte[i].y() > 2 * VERT_SEARCH_INTERV &&
            erste_feld_Punkte[i + 1].y() - erste_feld_Punkte[i].y() > 2 * VERT_SEARCH_INTERV &&
            erste_feld_Punkte[i + 1].x() - erste_feld_Punkte[i - 1].x() < 3 * (input.get_width() - 1) / (NUMBER_SCANLINES - 1)) {
            erste_feld_Punkte[i].y() = (erste_feld_Punkte[i - 1].y() + erste_feld_Punkte[i + 1].y()) * 0.5;
        }
    }
    find_horizon_obstacles(input, erste_feld_Punkte, field_hits);
    calculate_horizon(erste_feld_Punkte, field_hits);
    delete[] erste_feld_Punkte;
}

/**
 * Berechnet aus einem Array aus Punkten der Feldlinien einen möglichen Horizont
 */
void RobotVision::calculate_horizon(Vector2i* erste_feld_Punkte, unsigned length)
{
    m_centered_horizon = (length ? erste_feld_Punkte[length / 2].y(): 0);
    m_horizon_estimated_derivate = (length ? erste_feld_Punkte[2 * length / 3].y() - erste_feld_Punkte[length / 3].y():0);
    if(length < 2)
    {
        m_current_horizon = 0;
        m_cfv_counter_limit = m_cfv_counter_limit > 32 ? m_cfv_counter_limit * 0.5 : m_cfv_counter_limit;
        return;
    }
    for(unsigned i = 0; i < length - 1; ++i)
    {
        DEBUG_SHAPES(EXPENSIVE, pa::line(erste_feld_Punkte[i],erste_feld_Punkte[i+1], pa::White));
    }

    unsigned m = 1;
    for(unsigned i = 2; i < length; ++i)
    {
        while(ccw_f(erste_feld_Punkte[m-1].x() , erste_feld_Punkte[m-1].y(),
            erste_feld_Punkte[m].x(), erste_feld_Punkte[m].y(), erste_feld_Punkte[i].x(),
            erste_feld_Punkte[i].y()) <= 0 && m <= NUMBER_SCANLINES)
        {
            --m;
            if(m == 0) break;
        }
        ++m;
        erste_feld_Punkte[m] = erste_feld_Punkte[i];
    }
    float sum = 0;
    for(unsigned j = 0; j < m; ++j)
    {
        DEBUG_SHAPES(IMPORTANT, pa::line(erste_feld_Punkte[j],erste_feld_Punkte[j + 1], pa::Red));
    }
    int max_height = m_height;
    for(unsigned j = 0; j <= m; ++j)
    {
        sum += erste_feld_Punkte[j].y();
        m_field_boundary_coordinates[0][j] = erste_feld_Punkte[j].x();
        m_field_boundary_coordinates[1][j] = erste_feld_Punkte[j].y();
        //FeatureToggel für die Neuen Kameras => min height ab jetzt
        max_height = m_field_boundary_coordinates[1][j] < max_height ?
        m_field_boundary_coordinates[1][j] : max_height;
    }
    m_iboundary_points = m + 1;
    m_current_horizon = (max_height + m_current_horizon) * 0.5;//Eine 50:50 Gewichtung des aktuelles Wertes mit dem letzten
}

template<class ImageType>
void RobotVision::find_horizon_obstacles(const ImageType& input, const Vector2i* erste_feld_Punkte, unsigned length) {
    m_obstacles.clear();
    const Vector2f size = input.template size<Vector2f>();
    for(unsigned i = 1; i < length; ++i) {
        int l_min;
        if(erste_feld_Punkte[i - 1].y() < erste_feld_Punkte[i].y()) {
            l_min = erste_feld_Punkte[i - 1].y();
            // Going down in the picture to lowpoints of the horizon
            do {
                ++i;
                } while(erste_feld_Punkte[i - 1].y() <= erste_feld_Punkte[i].y() && i < length - 1);
            if(i < length - 1) {
                const Eigen::Vector2i pos = erste_feld_Punkte[i - 1];
                const Eigen::Vector2i* p;
                //Add obstacle
                //DEBUG_SHAPES(EXPENSIVE, pa::circle(pos, 5, pa::Cyan));
                for(unsigned j = i - 1; j; --j) {
                    p = &erste_feld_Punkte[j];
                    if((*p).y() == pos.y()) {
                        DEBUG_SHAPES(EXPENSIVE, pa::circle(*p, 5, pa::Cyan));
                    } else {
                        break;
                    }
                }
                m_obstacles.emplace_back(transform_image_point_to_relative(p->cast<float>(), size), transform_image_point_to_relative(pos.cast<float>(), size), pos.y() - l_min, pos.y() - erste_feld_Punkte[i].y());
            }
        }
    }
}

/**
 * Berechnet mit der CCW-Methode, ob ein Punkt im vermuteten Feld liegt
 */
inline bool RobotVision::is_point_in_field(const Vector2i& point)const
{
    int i = 1;
    while( i < m_iboundary_points && m_field_boundary_coordinates[0][i] < point.x())
    {
        ++i;
    }
    //Feature Toggle für die neuen gedrehten Kameras
    static int horinzon_border = m_height;
    return current_horizon() < horinzon_border
        && ccw_f<const float>(m_field_boundary_coordinates[0][i-1], m_field_boundary_coordinates[1][i-1], m_field_boundary_coordinates[0][i], m_field_boundary_coordinates[1][i], point.x(), point.y()) >= 0;
}
inline bool RobotVision::is_point_in_field(const Vector2f& point)const {
    return is_point_in_field(static_cast<const Vector2i&>(point.cast<int>()));
}

// The idea is, to find at least one pixel which colour differs significantly from the mean colour
template<class ImageType, typename... Args>
bool is_homogeneous_or_dark_cluster(const ImageType input, const std::vector<Args...>& cluster, int diff_type=0) {
    Vector3i mean_color = Vector3i::Zero();
    for(auto sample: cluster) {
        mean_color += input(sample.get().vector());
    }
    mean_color /= static_cast<int>(cluster.size());
    if(mean_color.x() < 100)
        return true;
    for(auto sample: cluster) {
        Vector3i pixel = input(sample.get().vector());
        switch(diff_type) {
            case(0): // complete colour distance
                if((pixel - mean_color).array().abs().sum() > 20)
                    return false;
                break;
            case(1): // chromatic distance
                if((pixel - mean_color).tail<2>().array().abs().sum() > 15)
                    return false;
                break;
            case(2): // y
                if(abs((pixel - mean_color).x()) > 10)
                    return false;
                break;
            case(3): // u
                if(abs((pixel - mean_color).y()) > 10)
                    return false;
                break;
            default: // v
                if(abs((pixel - mean_color).z()) > 10)
                    return false;
                break;
        }
    }
    return true;
}

template<class ImageType,class SampleType, bool use_distance>
void RobotVision::process_ball(const ImageType& input, const Cloud& cloud, const vector<SampleType>& samples, const vector<LineClusteringSampleType>& orange_samples, const bool recalibrate) {
    size_t max_clustering_size = 15000; // Don't cluster too much
    // We use the max distance clustering feature. This may void ball candidates, because of the given clustering limits, explained in sample.hpp
    SpartialClusteringType<SampleType, use_distance> dbscan(cloud, max_clustering_size, samples, 24, 3);
    m_ball_info.clear();
    unsigned horizon_border = m_robo_horizon.maxCoeff();
    int horizon_derivate = m_robo_horizon(1) - m_robo_horizon(0);
    const Vector2f size = input.template size<Vector2f>();

    // TODO consider: competition hacked feature -> ask Robert or delete it
    Vector2i orange_mean(0,0);
    for(const VisionSample& o_sample: orange_samples)
        orange_mean+=o_sample.vector();
    if(orange_samples.size() > 5) {// small threshold
        orange_mean/=static_cast<int>(orange_samples.size());
        // We decided to implement this as a behaviour bypass with a special rating of -2 and approximated radius
        // When we see enough orange feature within the picture we assume it as the ball. For the moment there
        // Can only be orange features on the ball.
        Info::BallInfo info;
        info.rating = -2;
        info.radius = std::min<unsigned>(
                          static_cast<unsigned>(orange_samples.size()), 175) /
                      static_cast<float>(m_width);
        Vector2f tr = transform_image_point_to_relative(orange_mean.cast<float>(), size);
        info.x = tr.x();
        // Here no adjustment of the position according to the m_ball_pos_is_ball_footpoint feature, this will be done later on
        info.y = tr.y();// - info.radius;
        m_ball_info.push_back(info);
        //std::cout<<"###############################################\n"
        //         << orange_mean.transpose() << "\t" << tr.transpose()<<"\n"
        //         <<"###############################################\n"<<std::endl;
    }

    // Alle Cluster durchgehen
    for(unsigned i = 1; i < dbscan.get_clusters().size(); i++) {
        const typename SpartialClusteringType<SampleType, use_distance>::Cluster& cluster = dbscan.get_clusters()[i];

        #if 1
        IF_DEBUG(NEW_FEATURE,{
        foreach(const SampleType& sample, cluster)
            switch(i%7){
                case(0):
                    DEBUG_SHAPES(NEW_FEATURE, pa::dot(sample, pa::Red));
                    break;
                case(1):
                    DEBUG_SHAPES(NEW_FEATURE, pa::dot(sample, pa::Blue));
                    break;
                case(2):
                    DEBUG_SHAPES(NEW_FEATURE, pa::dot(sample, pa::Green));
                    break;
                case(3):
                    DEBUG_SHAPES(NEW_FEATURE, pa::dot(sample, pa::Cyan));
                    break;
                case(4):
                    DEBUG_SHAPES(NEW_FEATURE, pa::dot(sample, pa::Pink));
                    break;
                case(5):
                    DEBUG_SHAPES(NEW_FEATURE, pa::dot(sample, pa::Black));
                    break;
                default:
                    DEBUG_SHAPES(NEW_FEATURE, pa::dot(sample, pa::White));
                    break;
            }
        });
        #endif

        // Center of Gravity des Clusters berechnen
        Vector2i cog(0, 0);
        foreach(const SampleType& sample, cluster)
            cog += sample;
        cog /= static_cast<int>(cluster.size());

        DEBUG_SHAPES(IMPORTANT, pa::point(cog, pa::Blue));//TODO entfernen?

        // If Center of Gravity is over the Horiizont we ignore this
        //Feature Toggle für die neu gedrehten Kameras, erweiterte abfrage, ob der Ball unterhalb des horizontes liegt
        if (!is_point_in_field(cog) ||
            cog.y() < static_cast<int>(horizon_border) ||
            cog.y() < m_robo_horizon.x() +
                          ((static_cast<float>(cog.x())) / m_width) *
                              horizon_derivate) {
            DEBUG_SHAPES(IMPORTANT, pa::point(cog, pa::Yellow).describe("HorizontError"));
            continue;
        }

        // Punkte, die auf dem Kreisrand liegen.
        Array2Xf points(2, 32);

        int count = 0;
        for(int j = 0; j < points.cols(); j++) {
            // Eine zufällige Richtung ermitteln
            //Vector2f dir = Vector2f::Random().normalized();
            const auto angle = static_cast<double>(j)/points.cols() * 2 * 3.1415296;
            const auto dir = Vector2f{std::cos(angle),std::sin(angle)};

            // Lineare Variante
            int found_ball = 0, found_carpet = 0;
            Vector2f last_ball(0, 0), first_carpet(0, 0);

            const int N = std::min<unsigned>(
                100, static_cast<unsigned>(30 + 2 * cluster.size()));
            const Vector2f cogg = cog.cast<float>();
            // The new ball may contain carpet colour, so we must be sure not to stop within the ball while searching for the carpet
            int previous_carpet_hits = 0;
            for(int j = 0; j < N; ++j) {
                const int max_image_ball_radius = std::min<unsigned>(
                    275, static_cast<unsigned>(30 + 2 * cluster.size()));
                const Vector2f mid = cogg + j * dir / N * max_image_ball_radius;
                if(mid.x() < 0 or mid.y() < 0 or mid.x() >= input.get_width() or mid.y() >= input.get_height()) {
                    continue;
                }
                Vector3i yuv = get_mean_color(input, mid.cast<int>());

                // additional check, that the not "assumed black"; low y and low cromaticy
                bool is_ball = not check_color_mask(yuv, CARPET) && not (yuv.x() < 128);// && (yuv.array().tail<2>() - Array2i::Constant(128)).abs().sum() < 42);
                bool is_carpet = check_color_mask(yuv, CARPET);
                if(is_ball and found_carpet == 0) {
                    last_ball = mid;
                    found_ball = j;
                }
                else
                if(is_carpet) {
                    if (! previous_carpet_hits) {
                        first_carpet = mid;
                        found_carpet = j;
                        // We want to be sure that we really found carpet, because the ball can contain green too
                    } else if (previous_carpet_hits > ((j > N / 2 && N > 60)? 3: 7)) {//TODO evaluate values
                        break;
                    }
                    previous_carpet_hits++;
                } else {
                    previous_carpet_hits = 0;
                }
            }

            // Weder Ball noch Fussboden
            if(found_carpet == 0 or found_ball == 0) {
                continue;
            }
            // Abstand prüfen
            if(found_carpet - found_ball > 20) {
                continue;
            }

            Vector2f point = 0.5 * (first_carpet + last_ball);
            points.col(count++).operator=(point);
        }
        // TODO this is a new feature
        auto highest_bit_idx = [] (int num) {int id = 31; while(!(num & (1<<id))){--id;}return id;};

        constexpr size_t MIN_POINTS_ON_CIRCLE = 7;
        if (count < std::max<int>(MIN_POINTS_ON_CIRCLE,
                                  highest_bit_idx(static_cast<int>(cluster.size()))))
        // Zu wenig Punkte, hier gibts nichts zu holen!
        {
            DEBUG_SHAPES(IMPORTANT, pa::point(cog, pa::Blue).describe(std::string("Zu KleinesBallCluster ") + std::to_string(count)));
            continue;
        }

        for(int j = 0; j < count; j++) {
            DEBUG_SHAPES(IMPORTANT, pa::point(points.col(j), pa::Blue));
        }
        float error, radius, point_variance;
        Vector2f midpoint;
        {
            // Kreis anfitten und Werte holen
            Vector3f circle = fit_circle(points.topLeftCorner(2, count));
            midpoint = circle.head(2);
            if(!is_point_in_field(midpoint)) {
                continue;
            }
            radius = circle(2);

            // Mittleren quadratischen Fehler ausrechnen!
            error = ((points.topLeftCorner(2, count).colwise() - midpoint.array()).matrix().colwise().norm().array() - radius).square().mean();
            point_variance = (points.topLeftCorner(2, count).colwise() - points.topLeftCorner(2, count).rowwise().mean())/*.rowwise()*/.square().sum() / count;
        }

        // wirklich unnötig große Bälle rauswerfen
        if(radius > 250) {
            continue;
        }
        // We want to enforce, that the variance is higher than the radius, mathematically it should be the square of the radius.
        if(point_variance < std::max(radius * radius / 16, radius * 4)) {
            continue;
        }
        if(error > 20 && is_homogeneous_or_dark_cluster(input, cluster, 1)) {
            //TODO Further handling and evaluation
            continue;
        }
        #if 1
            // Benötigen wir eigentlich nur, wenn wir direkt
            // am Feldrand Ball-Farbe haben

            // Zählen, wieviele Punkte über/unterhalb bzw links/rechts
            // des Mittelpunkts des Kreises liegen
            int points_above = 0, points_right = 0;
            int points_below = 0, points_left = 0;
            for(int j = 0; j < count; j++) {
                if(points(1, j) > midpoint.y() - radius*0.8)
                    points_above += 1;

                if(points(1, j) < midpoint.y() + radius*0.8)
                    points_below += 1;

                if(points(0, j) > midpoint.x() - radius*0.8)
                    points_right += 1;

                if(points(0, j) < midpoint.x() + radius*0.8)
                    points_left += 1;
            }

            float frac_points_above = points_above / float(count);
            float frac_points_below = points_below / float(count);
            float frac_points_right = points_right / float(count);
            float frac_points_left =  points_left / float(count);

            if(frac_points_below < 0.04 || frac_points_above < 0.04 || frac_points_left < 0.04 || frac_points_right < 0.04) {
                const string msg = (boost::format(
                    "Zu gerade: "
                    "  above: %1.2f |"
                    "  below: %1.2f |"
                    "  right: %1.2f |"
                    "  left:  %1.2f")
                        % frac_points_above
                        % frac_points_below
                        % frac_points_right
                        % frac_points_left).str();

                DEBUG_SHAPES(IMPORTANT, pa::point(midpoint, pa::Green).describe(msg));

                // Verwerfe den Ball, weil zu gerade
                continue;
            }
        #endif

        if(radius < 5) {
            continue;
        }

        bool is_goal_post = false;
        //don't use ball if it is inside the goalpost
        //looks if the midpoint is in respect to x with threshold of 0.5 goal post with and to y axis with one times ball radius
        //inside the goalpost
        //if so it is not added to the ballcandidates
        vector<int> removal_candidates;
        for(unsigned int post_index = 0; post_index < m_yellow_goal_info.posts.size(); post_index++){

            Info::GoalPost current_post = m_yellow_goal_info.posts.at(post_index);
            float post_width = ( (1.0f * current_post.width) / (1.0f * input.get_width()) );
            float normed_radius = ( (1.0f * radius) / (1.0f * input.get_width()) );
            Vector2f normed_midpoint = transform_image_point_to_relative(midpoint, size);

            if(normed_midpoint.x() < current_post.x + post_width && normed_midpoint.x() > current_post.x - post_width){
                if(((normed_midpoint.y() + normed_radius) > current_post.y)){
                    is_goal_post = true;
                    if(m_yellow_goal_info.posts.size() > 1){
                        //Vector<int> removal_candidates;
                        //if there is more than one goal post
                        //check if there are two near goal post detected
                        //that likely lay on a ball
                        //(false positives in goalpost detection)
                        bool removed = false;
                        for(unsigned int local_index = 0; local_index < m_yellow_goal_info.posts.size(); local_index++){
                            if(post_index == local_index){
                                continue;
                            }
                            Info::GoalPost local_post = m_yellow_goal_info.posts.at(local_index);
                            if(abs(current_post.px_x - local_post.px_x) < current_post.width * 2){
                                is_goal_post = false;
                                removal_candidates.emplace_back(local_index);
                                removed = true;
                            }
                        }
                        if(removed){
                            removal_candidates.emplace_back(post_index);
                        }
                    }
                }
            }
        }
        if(removal_candidates.size() > 0){

            std::sort(removal_candidates.begin(), removal_candidates.end());
            auto unique_end = std::unique(removal_candidates.begin(), removal_candidates.end());

            removal_candidates.erase(unique_end, removal_candidates.end());
            for(std::vector<int>::reverse_iterator it = removal_candidates.rbegin(); it != removal_candidates.rend(); it++) {
                m_yellow_goal_info.posts.erase(m_yellow_goal_info.posts.begin() + *it);
            }
        }
        removal_candidates.clear();
        if(is_goal_post){
            continue;
        }

        // Bewerte den Kreis
        error = error / sqrt(radius) * 100 / sqrt(count);

        boost::format fmt("Fehler: %1.2f");

        DEBUG_SHAPES(IMPORTANT, pa::point(midpoint, pa::Green).describe((fmt % error).str()));


        if(error < 200 and error >= 0) {
            if(unlikely(recalibrate) && error < 10)
            {
                recalibrate_ball_color_config<ImageType, SampleType, typename SpartialClusteringType<SampleType, use_distance>::Cluster, use_distance>(input, dbscan.get_clusters()[i], radius, midpoint.cast<int>());
                DEBUG_LOG(IMPORTANT,"Recalibrated Ball Color in Vision");
            }
            DEBUG_SHAPES(IMPORTANT, pa::circle(midpoint, radius, pa::Green));
            DEBUG_LOG(IMPORTANT,"Found Ball");
            //Den Vector anscheinend wie für die Linien im Locator normieren
            if(m_ball_pos_is_ball_footpoint) {
                midpoint.y() += radius;
            }
            const Vector2f pos = transform_image_point_to_relative(midpoint, size);

            // Ballfilter
            // 24.04.15 Magdeburg
            // Olli/Sheepy
            // 19.07.15 China
            // Dennis/Robert
            //entfernt wegen nicht Brazuca Ball
            /*auto carpet_percentage = 0.f;
            auto ball_percentage = 0.f;

            constexpr int SEGMENTS = 9;
            constexpr float RADIUS_FACTOR = 1.f;
            static_assert(SEGMENTS > 0, "Number of segments not positive");

            auto count = 0;
            for (int i = 0; i < SEGMENTS; ++i) {
                for (int j = 0; j < SEGMENTS; ++j) {
                    const auto position = std::make_pair(
                        static_cast<int>(
                            midpoint(0) - RADIUS_FACTOR * radius +
                            (i * RADIUS_FACTOR / SEGMENTS * radius * 2)),
                        static_cast<int>(
                            midpoint(1) - (1 + RADIUS_FACTOR) * radius +
                            (j * RADIUS_FACTOR / SEGMENTS * radius * 2)));

                    if (std::sqrt(
                            std::pow(position.first - midpoint.x(), 2) +
                            std::pow(position.second - midpoint.y() + radius,
                                     2)) < radius) {
                        const auto pixel =
                            input(position.first, position.second);
                        const auto type = get_pixel_type(pixel);

                        if (type & CARPET) {
                            ++carpet_percentage;
                        }
                        if (input(pixel)[0] > 200 || type & BALL) {
                            ++ball_percentage;
                        }
                        ++count;
                    }
                }
            }
            carpet_percentage /= count;
            ball_percentage /= count;

            Info::BallInfo ball_info;
            ball_info.rating = error;
            ball_info.x = pos.x();
            ball_info.y = pos.y();
            ball_info.radius = radius / input.get_width();

            if (!(carpet_percentage <= 0.152047f && ball_percentage > 0 &&
                  ball_percentage <= 0.83432f)) {

                DEBUG_SHAPES(
                    IMPORTANT,
                    pa::point(midpoint.cast<int>() + Vector2i{0, 20 - radius},
                              pa::Green).describe("KeinBall"));
            } else {
                m_ball_info.push_back(ball_info);
            }*/

            Info::BallInfo ball_info;
            ball_info.rating = error;
            ball_info.x = pos.x();
            ball_info.y = pos.y();
            ball_info.radius = radius / input.get_width();
            m_ball_info.push_back(ball_info);
        }
    }
    if(m_ball_info.size() && m_ball_info.begin()->rating == -2) {
        // Fancy stuff
        Vector2f mean_pos = m_ball_info.begin()->pos();
        float mean_radius = m_ball_info.begin()->radius;
        Vector2f start = mean_pos;
        int num = 1;
        for(auto it = m_ball_info.begin() + 1; it < m_ball_info.end(); it++) {
            Vector2f pos = it->pos();
                if(m_ball_pos_is_ball_footpoint)
                        pos.y() += it->radius;
            if((pos - start).norm() < 1.2 * it->radius) {
                num++;
                mean_pos += pos;
                mean_radius += it->radius;
            }
        }
        m_ball_info.begin()->set_pos(mean_pos / num);
        m_ball_info.begin()->radius = mean_radius / num;
        if(m_ball_pos_is_ball_footpoint)
            m_ball_info.begin()->y -=m_ball_info.begin()->radius;
    }
    std::sort(m_ball_info.begin(), m_ball_info.end());
    if(m_ball_info.size()) {
        DEBUG_SHAPES(IMPORTANT, pa::circle(-m_ball_info.begin()->x * 800 + 400, -m_ball_info.begin()->y * 800 + 300-m_ball_info.begin()->radius*800, m_ball_info.begin()->radius * 800, pa::Red));
        if(m_ball_info.size() & (~1)) {
            DEBUG_SHAPES(IMPORTANT, pa::circle(-(m_ball_info.begin() + 1)->x * 800 + 400, -(m_ball_info.begin() + 1)->y * 800 + 300-(m_ball_info.begin() + 1)->radius*800, (m_ball_info.begin() + 1)->radius * 800, pa::Pink));
        }
    }
}

inline Vector2f RobotVision::transform_image_point_to_relative(const Vector2f point,
                                                               const Vector2f& size) const {
    //Den Vector anscheinend wie für die Linien im Locator normieren
    Vector2f pos = point - (size*0.5);
    pos.array() /= size.x();
    pos(1) *= -1;
    pos(0) *= -1;
    return pos;
}

Vector2f RobotVision::get_relative_horizon() const {
    return (Eigen::Vector2f()<< (m_horizon_estimated_derivate <= -50? -1: m_horizon_estimated_derivate >= 50 ? 1: 0),
                transform_image_point_to_relative(Vector2f(m_width/2, m_current_horizon), Vector2f(m_width, m_height)).y()
                ).finished();
}

template<class ImageType>
void RobotVision::process_goals(const ImageType& input, Info::GoalInfo& goal_info) {
    Debug::Scope m_debug(this->m_debug, "Goal." + goal_info.color);
    goal_info.posts.clear();
    int plateau_len = 0;
    int horizon_idx = 1;
    unsigned char min_y_val = 200;
    unsigned char max_y_val = 255;
    static const int x_skip = 2;
    static const int y_skip = 1;
    for(int x = 0; x < input.get_width(); x+=x_skip){
        if(x > m_field_boundary_coordinates[0][horizon_idx]) {
            ++horizon_idx;
            if(horizon_idx > m_iboundary_points)
                break;
        }
        #define bfp m_field_boundary_coordinates
        int y_base = bfp[1][horizon_idx - 1] +
                     ((static_cast<float>(bfp[1][horizon_idx]) -
                       bfp[1][horizon_idx - 1]) /
                      (static_cast<float>(bfp[0][horizon_idx]) -
                       bfp[0][horizon_idx - 1])) *
                         (x - bfp[0][horizon_idx - 1]);
        #undef bfp
        // We mustn't exeed image sizes with y_base, max height - 1 - addition
        y_base = std::min(m_height - 4, std::max(0, y_base));
        y_base +=3;
        if(input(x, y_base)(0) > min_y_val && input(x, y_base)(0) < max_y_val){
            plateau_len += x_skip;
        }
        else{
            if(plateau_len >= 6){
                int plateau_mid = x - (plateau_len / 2);
                int y_position_min = y_base;
                while(y_position_min > 0 &&  input(plateau_mid, y_position_min)(0) > min_y_val && input(plateau_mid, y_position_min)(0) < max_y_val) {
                    y_position_min -= y_skip;
                }
                int y_position_max = y_base;
                while(y_position_max < m_height && input(plateau_mid, y_position_max)(0) > min_y_val && input(plateau_mid, y_position_max)(0) < max_y_val) {
                    y_position_max += y_skip;
                }// Mache eine Fostenbreitensuche am Fußpunkt und suche dann mit dem angepassten schiefen Vektor weiter.
                int additional_goal_white_offset = 1;
                y_position_max -= y_skip;
                if(input(plateau_mid + 2 * x_skip, y_position_max)(0) > min_y_val && input(plateau_mid + 2 * x_skip, y_position_max)(0) < max_y_val) {
                    while(additional_goal_white_offset + plateau_mid < m_width && input(plateau_mid + additional_goal_white_offset, y_position_max)(0) > min_y_val && input(plateau_mid + additional_goal_white_offset, y_position_max)(0) < max_y_val) {
                        additional_goal_white_offset += x_skip;
                    }
                } else {
                    while(additional_goal_white_offset < plateau_mid && input(plateau_mid - additional_goal_white_offset, y_position_max)(0) > min_y_val && input(plateau_mid - additional_goal_white_offset, y_position_max)(0) < max_y_val) {
                        additional_goal_white_offset += x_skip;
                    }
                }
                if(std::abs(additional_goal_white_offset) > 1 && y_position_max != y_base) {
                    float x_diff = additional_goal_white_offset /
                                   static_cast<float>(y_position_max - y_base);
                    float x_pos = plateau_mid + (y_position_max - y_base) * x_diff / 2;
                    while(y_position_max < m_height && input(x_pos, y_position_max)(0) > min_y_val && input(x_pos, y_position_max)(0) < max_y_val) {
                        y_position_max += y_skip;
                        x_pos += x_diff * y_skip;
                    }
                }
                if(y_position_max - y_position_min > 10) {
                    Eigen::Vector2f pos = transform_image_point_to_relative(Vector2f(plateau_mid, y_position_max), input.template size<Vector2f>());
                    int rating = y_position_max - y_base;
                    if(rating < (plateau_len / x_skip)) {
                        DEBUG_SHAPES(IMPORTANT, pa::rect(plateau_mid, y_position_min, plateau_len, y_position_max - y_position_min, pa::Red));
                    } else {
                        // TODO Maybe search for green in the area around the footpoint
                        float abs_width = ( (1.0f * plateau_len) / (1.0f * input.get_width()) );
                        float abs_height = ( (1.0f * (y_position_max - y_position_min)) / (1.0f * input.get_height()) );
                        goal_info.posts.emplace_back(pos.x(), pos.y(), plateau_mid, y_position_max, plateau_len, y_position_max - y_position_min, is_point_in_field(Vector2i(plateau_mid, y_position_max)), rating, abs_width, abs_height);
                        DEBUG_SHAPES(IMPORTANT, pa::rect(plateau_mid - plateau_len / 2, y_position_min, plateau_len, y_position_max - y_position_min, pa::Yellow));
                    }
                }
            }
            plateau_len = 0;
        }
    }
    std::sort(goal_info.posts.begin(), goal_info.posts.end());
    DEBUG(IMPORTANT, "Goal.Posts", goal_info.posts.size());
}

template<class ImageType>
inline
void RobotVision::process_team_markers(const ImageType& input, const Cloud& cloud,
                                       const vector<ColorColorSample>& rest_samples){
    typedef Scanning::SpatialClustering<Cloud, ColorColorSample, false, false> TeamScanner;
    typedef typename TeamScanner::Cluster Cluster;
    typedef Info::RobotData RobotData;
    TeamScanner dbscan(cloud, rest_samples);
    m_team_marker_data.clear();
    const Vector2i size = input.template size<Vector2i>();
    foreach(const Cluster& cluster, dbscan.get_clusters()) {
        // skip small cluster
        if(cluster.size() < 100) {
            if(cluster.size() == 0) continue;
            DEBUG_SHAPES(NEW_FEATURE,pa::text(cluster[0].get().vector().x(), cluster[0].get().vector().y(), "Zu kleines Restcluster", pa::Green));
            continue;
        }
        m_team_marker_data.emplace_back();
        RobotData& data = m_team_marker_data[m_team_marker_data.size() - 1];
        Vector2i left_upper = Vector2i::Constant(99999);
        Vector2i right_lower = Vector2i::Zero();
        Vector2i sum = Vector2i::Zero();

        foreach(const ColorColorSample& sample, cluster) {

            // Determine Bounding Box of this cluster along the way
            if(unlikely(sample.y() < left_upper.y())) {
                left_upper[1] = sample.y();
            }
            if(unlikely(sample.x() < left_upper.x())) {
                left_upper[0] = sample.x();
            }
            if(unlikely(sample.y() > right_lower.y())) {
                right_lower[1] = sample.y();
            }
            if(unlikely(sample.x() > right_lower.x())) {
                right_lower[0] = sample.x();
            }

            sum += sample.vector();
            const Vector3Ub& yuv = sample.get_masq();
            int u = yuv(1);
            int v = yuv(2);

            //In yuv color space magenta is in the upper right square of the uv, color matrix, cyan in the lower right square
            //Giving a little threshold on u axis
            //100 seems to be a pretty fair value
            if(u < 100) {
                continue;
            }
            // v value above magenta threshold
            if(v > 142 || get_pixel_type(sample.get_masq()) & COLOR_MASK_TYPE::MAGENTA) {
                ++data.potential_magenta;
                DEBUG_SHAPES(NEW_FEATURE, pa::point(sample.vector(), pa::Pink));
            }
            // v value below cyan_threshold
            else if (v < 100 || get_pixel_type(sample.get_masq()) & COLOR_MASK_TYPE::CYAN) {
                ++data.potential_cyan;
                DEBUG_SHAPES(NEW_FEATURE, pa::point(sample.vector(), pa::Cyan));
            }
        }
        Vector2i cog = sum / static_cast<int>(cluster.size());
        if(!is_point_in_field(cog)) {
            // over horizon
            m_team_marker_data.pop_back();
            continue;
        }

        // determine dimensions of the Object
        data.x = (right_lower.x() - left_upper.x() / 2); // center floor-point x
        data.y = (right_lower.y() - left_upper.y() / 2); // center floor-point y
        data.w = right_lower.x() - left_upper.x();       // Object height
        data.h = right_lower.y() - left_upper.y();       // Object width

        const unsigned color_count = max(data.potential_cyan, data.potential_magenta);
        // Discard objects that appear to be too large
        if (unlikely((data.w + data.h) > ((size.x() + size.y()) * 0.8)))
        {
            m_team_marker_data.pop_back();
            continue;
        }
        // Too much color => not a Robot (but an obstacle)
        if (unlikely(color_count > (cluster.size() / 3) || color_count < (cluster.size() / 100)))
        {
            // set result in colors
            DEBUG_SHAPES(NEW_FEATURE, pa::rect(left_upper.x(), left_upper.y(), data.w, data.h, pa::Yellow));
            if (data.potential_cyan > (data.potential_magenta * 2))
            {
                data.result = RobotData::DataType::much_cyan;
            }
            else if (data.potential_magenta > (data.potential_cyan * 2))
            {
                data.result = RobotData::DataType::much_magenta;
            }
            // similar amount of both colors => cant decide (probably overlapping robots)
            else
            {
                data.result = RobotData::DataType::mixed;
            }
            continue;
        }
        // more than twice as much cyan than magenta => cyan robot
        else if (data.potential_cyan > (data.potential_magenta * 2))
        {
            DEBUG_SHAPES(NEW_FEATURE, pa::rect(left_upper.x(), left_upper.y(), data.w, data.h, pa::Cyan));
            data.result = RobotData::DataType::cyan;
        }
        // more than twice as much magenta than cyan => magenta robot
        else if (data.potential_magenta > (data.potential_cyan * 2))
        {
            DEBUG_SHAPES(NEW_FEATURE, pa::rect(left_upper.x(), left_upper.y(), data.w, data.h, pa::Pink));
            data.result = RobotData::DataType::magenta;
        }
        // similar amount of both colors => cant decide (probably overlapping robots)
        else
        {
            DEBUG_SHAPES(NEW_FEATURE, pa::rect(left_upper.x(), left_upper.y(), data.w, data.h, pa::Green));
            data.result = RobotData::DataType::undefined_obstacle;
        }
    }
}

//@author Robert

template<class ImageType>
void RobotVision::process_lines(const ImageType& input, const Cloud& cloud, const vector<LineClusteringSampleType>& samples) {//Structure Based fixup
    using std::cref;
    using std::reference_wrapper;

    float radius = 100;
    SpartialLineClusteringType line_scan(cloud, samples, radius, 1, 0.45);
    m_line_points.clear();

    int dx[] = {-9, -7, 0, 7, 9, 7, 0, -7};
    int dy[] = {0, -7, -9, -7, 0, 7, 9, 7};

    int number_deleted_points = 0;//Important for keeping parent structure stable
    Vector2f size = input.template size<Vector2f>();//Zum Normieren der Bildpunkte
    for(unsigned i = 1; i < line_scan.get_clusters().size(); i++)//There is no noise cluster 0 any more
    {//Mache Linienverarbeitung
        const SpartialLineClusteringType::Cluster& cluster = line_scan.get_clusters()[i];
        //try some magic ;-)
        bool valid = false;
        //When all cluster points are in field, but not surrounded by any green count_... ist size()
        // otherwise it's overridden.
        int count_invalid_points = static_cast<int>(cluster.size());
        for(unsigned k = 0; k < cluster.size(); ++k)
        {
            const VisionLineSample& pos = cluster[k];

            if(unlikely(!is_point_in_field(pos.vector())))
            {
                count_invalid_points = k;
                valid = false;
                break;
            }

            if((!valid) && pos.x() >= 10 && pos.x() < input.get_width()-10 && pos.y() >= 10 && pos.y() < input.get_height()-10)//While the cluster is not bounded by any green point or the given point is to close to the border of the image
            {
                // There must be a green Point around the Cluster
                for(int j = 0; j < 8; j++) {
                    const Vector2i p(pos + Vector2i(dx[j], dy[j]));
                    if(check_color_mask(input(p), CARPET)) {
                        valid = true;
                        break;
                    }
                }
            }

            switch(i % 5){// Some funny color in debug, not necesary when working correct
                case 0: {DEBUG_SHAPES(EXPENSIVE, pa::point(pos, pa::Green)); break;
            }   case 1: {DEBUG_SHAPES(EXPENSIVE, pa::point(pos, pa::Red)); break;
            }   case 2: {DEBUG_SHAPES(EXPENSIVE, pa::point(pos, pa::Black)); break;
            }   case 3: {DEBUG_SHAPES(EXPENSIVE, pa::point(pos, pa::White)); break;
            }   case 4: {DEBUG_SHAPES(EXPENSIVE, pa::point(pos, pa::Blue)); break;
            }
            }

            // Den Punkt so normieren, dass die Winkel bei einer Entfernung von
            // einer Einheit vor der Kamera erhalten bleiben
            //Vector2f size = input.template size<Vector2f>();Vor der Forschleife deklariert und initialisiert
            LineSample result(ColorSample((pos.cast<float>() - 0.5*size) / input.get_width()
                , pos.get_index()), pos.get_parent() - number_deleted_points);//Norm the Vector as discribed and save its parent, the way the line_clustering does
            result(1) *= 1;
            m_line_points.push_back(result);
        }
        if(!valid)
        {
            number_deleted_points += cluster.size();
            for(int l = 0; l < count_invalid_points; ++l)
            {
                m_line_points.pop_back();
            }
        }
    }

    DEBUG(INFO, "LinePointsInVision", m_line_points.size());
}



/** @author Timon
 *
 * calculate shape-describing vectors from the image
 * theese vectors can be used to find obstacles.
 */
static const int V_THRESHOLD = 100; //Values below this are Features
static const int SKIP = 5; //Consider only each nth pixel
template<class ImageType>
void RobotVision::process_shape_vectors(const ImageType& input)
{
    list<figVec> vectors;

    // Get the pixels we want and binarise them.
    // Picture scaled down by factor SKIP
    MatrixHolder<RMatrixXUb> mat(input.get_height()/SKIP, input.get_width()/SKIP);
    for(int i = 0; i < mat.rows(); i++) {
         for(int j = 0; j < mat.cols(); j++) {
            //if (input(j*SKIP,i*SKIP)[2] > V_THRESHOLD) // hsv bekommen
            if (input(j*SKIP,i*SKIP)[0] > V_THRESHOLD) //v allein
            {
                mat(i,j) = 255;
            }
            else
            {
                mat(i,j) = 0;
            }
        }
    }
    MatrixHolder<RMatrixXUb>& mat_ref(mat);
    DEBUG(INFO, "BinaryImage", mat_ref);
    DEBUG(INFO, "BinaryImage.Draw", true);

    //Generate Vectors using the uchar binary image
    vectorize(mat,vectors);
    list<figVec>::iterator vit;
    DEBUG(INFO, "Vectors", vectors.size()); //Debug

    //Iterate found vectors, rescale them to original size.
    //Save them for later use
    /*
    for (vit = vectors.begin(); vit != vectors.end(); vit ++)
    {
        sv.sx = vit->sx*SKIP;
        sv.sy = vit->sy*SKIP;
        sv.ex = vit->ex*SKIP;
        sv.ey = vit->ey*SKIP;
        sv.weight = vit->weight*SKIP;
        shape_vectors.push_back(sv);

        //Debug output to show vector
        DEBUG_SHAPES(EXPENSIVE, pa::line(sv.sx,sv.sy,

        sv.ex,sv.ey,pa::Blue));
    }*/

    //generate a Graph from the vectors
    ShapeGraph sg;
    sg = makeShapeGraph(vectors);
    //refineGraph(sg);

    //Iterate Edges of the Graph to show debug data
    pair<edge_iterator,edge_iterator> ep = boost::edges(sg);
    edge_iterator ei;
    edge_descriptor ed;
    for (ei = ep.first; ei != ep.second; ei ++)
    {
      ed = *ei;
      DEBUG_SHAPES(EXPENSIVE, pa::line(
            sg[source(ed,sg)].x*SKIP, sg[source(ed,sg)].y*SKIP,
            sg[target(ed,sg)].x*SKIP, sg[target(ed,sg)].y*SKIP,
            pa::Yellow));
    }
    //get obstacles and draw to debug
    vector<Obstacle> ov = getObstacles(sg);
    Obstacle ob;
    for (unsigned i = 0; i != ov.size(); i++)
    {
      ob = ov[i];
      DEBUG_SHAPES(EXPENSIVE, pa::rect(
            ob.u*SKIP,
            ob.v*SKIP,
            (ob.x-ob.u)*SKIP, //width
            (ob.y-ob.v)*SKIP, //height
            pa::Pink));
    }

    if (m_pylons_enabled)
    {
        //Search pylons
        m_pylons.clear();
        list<Pylon> small_pylons = findPylons(vectors);
        list<Pylon>::iterator pit;
        Pylon p;
        //rescale and store found pylons:
        for (pit = small_pylons.begin(); pit != small_pylons.end(); pit++)
        {
            p.x = pit->x * SKIP;
            p.y = pit->y * SKIP;
            p.radius = pit->radius * SKIP;
            m_pylons.push_back(p);
        }

        //Debug output
        DEBUG(INFO, "Pylons found", m_pylons.size());
        for (pit = m_pylons.begin(); pit != m_pylons.end(); pit ++)
        {
            DEBUG_SHAPES(EXPENSIVE, pa::line(pit->x-pit->radius,pit->y,pit->x+pit->radius,pit->y,pa::Red).describe("Pylon"));
        }
    }

}
