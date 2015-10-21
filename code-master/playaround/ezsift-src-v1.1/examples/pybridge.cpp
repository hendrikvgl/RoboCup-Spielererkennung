#include <boost/python.hpp>
#include <iostream>
#include <vector>
#include <cstdint>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <map>
#include <cassert>
#include <sstream>
#include <time.h>

#include "../ezsift.h"

using namespace boost::python;


struct ImageMatcher
{
    std::map <std::string, std::list<SiftKeypoint> > key_point_mapping;


    void add_image(std::string identifier, boost::python::list& img, int img_w, int img_h) {
        std::list<SiftKeypoint> siftKeys = this->generate_keypoints(img, img_w, img_h);
        this->key_point_mapping[identifier] = siftKeys;
        std::cout << "Adding Image with Key: " <<  identifier << std::endl;
    }

    boost::python::list get_images(){
        boost::python::list result;
        for(auto const &it1 : key_point_mapping) {
            result.append(it1.first);
            result.append(it1.second.size());
        }
        return result;
    }

    boost::python::list get_keypoint_confusion(){
        boost::python::list confusion;
        for(auto const &kp1 : key_point_mapping) {
            boost::python::list row;
            for(auto const &kp2 : key_point_mapping) {
                std::list<SiftKeypoint> a1 = kp1.second;
                std::list<SiftKeypoint> a2 = kp2.second;
                std::list<MatchPair> match_list;
                match_keypoints(a1, a2, match_list);
                row.append(match_list.size());
            }
            confusion.append(row);
        }
        return confusion;
    }

    std::list<SiftKeypoint> generate_keypoints(boost::python::list& img, int img_w, int img_h){
        ImageObj<uchar> image = get_image_from_python_data(img, img_w, img_h);
        return compute_keypoints(image);
    }

    boost::python::list compute_and_return_keypoints(boost::python::list& img, int img_w, int img_h) {
        ImageObj<uchar> image = get_image_from_python_data(img, img_w, img_h);
        std::list<SiftKeypoint> key_points = compute_keypoints(image);

        boost::python::list result;
        for (SiftKeypoint kp: key_points){
            boost::python::list pykp;
            pykp.append(kp.octave);
            pykp.append(kp.layer);
            pykp.append(kp.rlayer);
            pykp.append(kp.r);
            pykp.append(kp.c);
            pykp.append(kp.scale);

            pykp.append(kp.ri);
            pykp.append(kp.ci);
            pykp.append(kp.layer_scale);

            pykp.append(kp.ori);
            pykp.append(kp.mag);

            result.append(pykp);
        }

        return result;
    }

    boost::python::list match_with_identifier(std::string identifier, boost::python::list& img, int img_w, int img_h) {
        // Get the Image from the python data and the computed SIFT Feature Points
        ImageObj<uchar> image = get_image_from_python_data(img, img_w, img_h);
        std::list<SiftKeypoint> key_points = compute_keypoints(image);

        // Get the SIFT Keypoints by the identifier
        boost::python::list result;

        if (key_point_mapping.count(identifier) > 0){
            std::list<SiftKeypoint> reference_keypoints = this->key_point_mapping[identifier];
            std::list<MatchPair> match_list;
            match_keypoints(reference_keypoints, key_points, match_list);
            result.append(match_list.size());
        } else {
            std::cout << "Could not find Image Key" << std::endl;

        }
        return result;
    }

    std::list<SiftKeypoint> compute_keypoints(ImageObj<uchar>& image){
        bool bExtractDescriptor = true;
        std::list<SiftKeypoint> keypoint_list;

        // Double the original image as the first octive.
        //double_original_image(true);

        printf("Start SIFT detection ...\n");
        sift_cpu(image, keypoint_list, bExtractDescriptor);
        return keypoint_list;
    }

    ImageObj<uchar> get_image_from_python_data(boost::python::list& img, int img_w, int img_h){
        std::vector<uchar> image_data1;
        for (int i = 0; i < len(img); ++i)
        {
            image_data1.push_back(boost::python::extract<uchar>(img[i]));
        }
        ImageObj<uchar> image1(image_data1.data(), img_w, img_h);
        return image1;
    }

    boost::python::list match_with_all(boost::python::list& img, int img_w, int img_h) {
        // Get the Image from the python data and the computed SIFT Feature Points
        double time_s = clock();
        ImageObj<uchar> image = get_image_from_python_data(img, img_w, img_h);
        double time_e = clock();
        std::cout << "Time for transform:" << (time_e - time_s)/CLOCKS_PER_SEC << std::endl;

        time_s = clock();
        std::list<SiftKeypoint> key_points = compute_keypoints(image);
        time_e = clock();
        std::cout << "Time for keypoints:" << (time_e - time_s)/CLOCKS_PER_SEC << std::endl;


        // Get the SIFT Keypoints by the identifier
        boost::python::list complete_result;

        time_s = clock();
        for(auto const &it1 : key_point_mapping) {
            std::string image_key = it1.first;
            std::list<SiftKeypoint> reference_keypoints = it1.second;
            std::list<MatchPair> match_list;
            match_keypoints(reference_keypoints, key_points, match_list);
            boost::python::list inner_result;

            inner_result.append(image_key);
            inner_result.append(match_list.size());
            for( MatchPair mp : match_list){
                inner_result.append(mp.c1);
                inner_result.append(mp.r1);
                inner_result.append(mp.c2);
                inner_result.append(mp.r2);
            }
            complete_result.append(inner_result);
        }
        time_e = clock();
        std::cout << "Time for match:" << (time_e - time_s)/CLOCKS_PER_SEC << std::endl;

        return complete_result;
    }
};

BOOST_PYTHON_MODULE(pybridge)
{
    class_<ImageMatcher>("ImageMatcher")
        .def("add_image", &ImageMatcher::add_image)
        .def("get_images", &ImageMatcher::get_images)
        .def("get_keypoint_confusion", &ImageMatcher::get_keypoint_confusion)
        .def("match_with_identifier", &ImageMatcher::match_with_identifier)
        .def("match_with_all", &ImageMatcher::match_with_all)
        .def("compute_and_return_keypoints", &ImageMatcher::compute_and_return_keypoints)
    ;
}