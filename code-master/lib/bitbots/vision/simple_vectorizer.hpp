#ifndef _SIMPLE_VECTORIZER_HPP
#define _SIMPLE_VECTORIZER_HPP

#include <stdio.h>
#include <iostream>
#include <list>
#include <assert.h>
#include <boost/config.hpp>
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/graphviz.hpp>
#include <boost/graph/graph_traits.hpp>
#include <boost/graph/connected_components.hpp>
#include <sstream>
#include "../debug/debug.hpp"
#include "../util/eigen_util.hpp"

namespace Vision{
namespace ObstacleDetection {

// Describes a detected pylon
// (no height, because they are modeld as infinit high)
struct Pylon {
  int x;     //base center  y-position
  int y;     //base center x-position
  int radius; //half of the percepted width of the pylon
};

// Describes detected something
// So it can be recognised as an obstacle
struct ShapeVector {
  int sx;
  int sy;
  int ex;
  int ey;
  int weight;
};

/*Start of a ShapeVector in Graph representation
 * */
struct ShapePoint{
  int x;
  int y;
  int w;
};
struct ShapeEdge{
  int w;
};

/* Obstacle with bounding box and weight
 */
struct Obstacle{
  unsigned int u;
  unsigned int v;
  unsigned int x;
  unsigned int y;
  unsigned int weight;
};

/*ShapeGraph*/
typedef boost::adjacency_list<
  boost::vecS,
  boost::vecS,
  boost::directedS,
  ShapePoint,
  ShapeEdge> ShapeGraph;

//simplicity definitions for boost
typedef boost::graph_traits<ShapeGraph>::vertex_descriptor vertex_descriptor;
typedef boost::graph_traits<ShapeGraph>::vertex_iterator vertex_iterator;
typedef boost::graph_traits<ShapeGraph>::edge_descriptor edge_descriptor;
typedef boost::graph_traits<ShapeGraph>::edge_iterator edge_iterator;
typedef boost::graph_traits<ShapeGraph>::adjacency_iterator adjacency_iterator;
struct figVec { // representation of figure parts as a vector
      int sx;// from startx
      int sy;// starty
      int ex;// to endx
      int ey;// endy
      int weight;// # of pixels it represents
      double penalty;// how much the vector is "bend" already (may be negative)
      double slope; //the current slope of this vector
      int lsx, lex; //last segment end/start
      int sw, ew; //weight of the first/last line
    };

void vectorize(Eigen::MatrixHolder<Eigen::RMatrixXUb>& I, std::list<figVec>& finished);
std::list<Pylon> findPylons(std::list<figVec>&);
ShapeGraph makeShapeGraph(std::list<figVec>&);
void refineGraph(ShapeGraph& sg);
std::vector<Obstacle> getObstacles(ShapeGraph& sg);

} } //namespace
#endif
