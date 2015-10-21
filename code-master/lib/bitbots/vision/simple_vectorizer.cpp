/*@author Timon Giese
 * Funktionen zum umwandeln von binärbildern in vektoren nach bestimmten Regeln.
 * Außerdem Untersuchung der vektoren auf mögliche Pylonen
 *
 * WARNING: Code ist noch nicht wartbar gemacht.
 * Der Versuch es trotzdem zu tun kostet unnötig Zeit.
 * */
#include "simple_vectorizer.hpp"
#include "../debug/debugmacro.h"
#include "../util/eigen_util.hpp"

using namespace std;
using namespace Vision::ObstacleDetection;
typedef unsigned char uchar;

// #### Parameter zum kaputtspielen: ####
double MAX_PENALTY = 1.2; //maximum change of vector-slope
int MAX_DIST = 2; //max # of pixels distance for vector ends to extend
int MIN_RELEVANCE = 0; // vectors representing less pixels are deleted


/*Segment binari 8-bit image into vectors describing
 * figure-parts (O(n))
 * */
void Vision::ObstacleDetection::vectorize(Eigen::MatrixHolder<Eigen::RMatrixXUb>& I, list<figVec>& finished)
{
    // accept only char type matrices
    //CV_Assert(I.depth() != sizeof(uchar));
    //CV_Assert(I.channels() == 1);

    int channels = 1;
    int nRows = static_cast<int>(I.cols() * channels);
    int nCols = static_cast<int>(I.rows());
    int c,r, startx, center, divident, dist, newdist, lineweight;
    uchar* cptr;
    bool hit=false;
    figVec vec;
    list <figVec> extend, nextExtend;
    list<figVec>::iterator lit, lit2, rem;
    double slope,penalty;

    /* Iterate over the lines of the picture */
    for (c = 0; c < nCols; ++c)
    {
      cptr = const_cast<unsigned char*>(I.ptr(c)); //set pointer to this line

      // move all vectors that should have been extended already O(c)
      for (lit = extend.begin(); lit != extend.end(); lit++)
      {
        if (!(lit->weight < MIN_RELEVANCE))
        {
          finished.push_back(*lit);
        }
      }
      extend = list<figVec>();
      //finished.splice(finished.end(),extend);


      // init extend-list for next run O(c)
      extend.splice(extend.end(), nextExtend);

      /* Iterate over the pixels of each row */
      for(r=0; r < nRows; r++)
      {
          //In a feature section
          if (hit)
          {
            // Leave a feature section
            if (cptr[r] > 0)
            {
              processSegment:
              //Find the center point
              divident = r+startx;
              if (divident & 1 ) divident--; //correct uneven values
              center = (divident)/2;
              lineweight = r - startx;

              //search vector to extend
              if (!extend.empty())
              {
                lit = extend.begin();
                rem = lit;
                vec = *lit;
                dist = abs(vec.ex - center); //set distance to minimize
                lit++;
                for (; lit != extend.end(); lit++)
                {
                  newdist = abs(lit->ex - center);
                  if (newdist  < dist)
                  {
                    dist = newdist; //new minimal distance
                    vec = *lit;     //new closest vector
                    rem = lit;      //remember for potential removal
                  }
                }
                // try to extend the nearest vector end
                // (In case it is not too far away)
                if (dist <= MAX_DIST)
                  {
                  assert(c-vec.sy != 0);
                  slope=(center-vec.sx)/double(c-vec.sy);
                  // if the vector is new, don't increase the penalty
                  // <+CHECK+> maybe it is not new? what happens then?
                  if (vec.penalty == 0 && vec.slope ==0)
                  {
                    penalty = 0;
                  }
                  else
                  {
                    penalty = vec.penalty + slope - vec.slope;
                  }
                  // if we dont exceed the maximum penalty
                  // Extend it
                  if (abs(penalty) <= MAX_PENALTY)
                  {
                    vec.ex = center;
                    vec.ey = c;
                    vec.penalty = penalty;
                    vec.slope = slope;
                    vec.weight += lineweight;
                    vec.lsx = startx;
                    vec.lex = r;
                    vec.ew = lineweight;
                    // remove this vector from the current run
                    nextExtend.push_back(vec);
                    extend.erase(rem);
                  }
                  else //if the vector could not be extended start a new Vector
                  {
                    //make new Vec
                    makeNewVec:
                    vec.sx = center;
                    vec.sy = c;
                    vec.ex = center ;
                    vec.ey = c;
                    vec.weight = lineweight;
                    vec.penalty = 0;
                    vec.slope = 0;
                    vec.lsx = startx;
                    vec.lex = r;
                    vec.sw = lineweight;
                    vec.ew = lineweight;

                    nextExtend.push_back(vec); //new vec will be avaliable next run
                    //cout << "made new Vec: " << center << "," << c << endl;
                  }
                }
                else //no vector could be extended => make one
                {
                  //<+CHECK+> Find elegant way to avoid goto
                  //cout << "distance " << dist << " too far, making new." << endl;
                  goto makeNewVec;
                }
              }
              else //no extendable vectors => make one
              {
                //<+CHECK+> Find elegant way to avoid goto
                //cout << "extend is empty, making new." << endl;
                goto makeNewVec;
              }
              hit = false;
            }
          }
          //Not in a feature section
          else
          {
            //Enter a feature section
            if (cptr[r] <= 0)
            {
              hit = true;
              startx = r;
            }
          }
      }
      //end of line forces leave feature section
      // <+CHECK+> Find a elegant way to avoid goto
      // Possibility: make a border around picture
      if (hit)
      {
        goto processSegment;
        hit=false;
      }
    }
    // all remaining vectors are considered to be finished.
    finished.splice(finished.end(),nextExtend);
}

// #### Parameters to play with for the pylon-search ####
double FACTOR = 3; //segment must be FACTOR times longer than wide.
double MAX_SLOPE = 0.08; //maximum slope of Pylons
double MIN_SLOPE = -0.08; //minimum slope of Pylons
int MIN_LENGTH = 5; //minimum length of a pylon (pixel)
int MIN_WIDTH= 5; //minimum width of a pylon (pixel)
// should be percepted pixel width of a maximum distant pylon

/* Try to find segments that could be a pylon
 * @return list of matches
 * */
list<Pylon> Vision::ObstacleDetection::findPylons(list<figVec>& veclist)
{
  list<figVec>::iterator lit;
  list<Pylon> result;
  int width, x, y;
  double length;
  for (lit=veclist.begin();lit !=veclist.end();lit++)
  {
    x = lit->sx - lit->ex;
    y = lit->sy - lit->ey;
    length = sqrt(x*x + y*y);
    if (length < MIN_LENGTH) continue;
    width = lit->weight/length;
    if (width < MIN_WIDTH) continue;
    if (length/width < FACTOR) continue;
    if (lit->slope > MAX_SLOPE) continue;
    if (lit->slope < MIN_SLOPE) continue;

    struct Pylon match;
    match.x = lit->ex;
    match.y = lit->ey;
    match.radius= width/2;

    result.push_back(match);
  }
#ifdef VERBOSE
  cout << "Pylons found: " << result.size() << endl;
#endif
  return result;
}

/* process figVectors into a Graph
 * */
ShapeGraph Vision::ObstacleDetection::makeShapeGraph(std::list<figVec>& vectors)
{
  list<figVec>::iterator a, b;
  ShapeGraph sg(0);
  vertex_descriptor va,vb;
  vertex_iterator via, vib;
  // first put all vectors alone in the graph
  for (a = vectors.begin(); a != vectors.end(); a++)
  {
    va = boost::add_vertex(sg);
    sg[va].x = a->sx;
    sg[va].y = a->sy;
    sg[va].w = a->sw/2; //weight of the start-line only

    vb = boost::add_vertex(sg);
    sg[vb].x = a->ex;
    sg[vb].y = a->ey;
    sg[vb].w = a->ew/2; //weight of the end-line only

    boost::add_edge(va,vb,sg);
  }

  // now link all points that should be linked

  std::pair<vertex_iterator,vertex_iterator> vpa = boost::vertices(sg);
  via = vpa.first;
  while (via != vpa.second)
  {
    va = *via;
    std::pair<vertex_iterator,vertex_iterator> vpb = boost::vertices(sg);
    vib = vpb.first;
    while (vib != vpb.second)
    {
      vb = *vib;
      //Secret and strange formular to calculate
      //if two points should be linked ;)

      //via being the "upper" one with one line difference
      if ((sg[va].y - sg[vb].y == -1))
      {
        //int dista = abs(sg[va].x - sg[va].w); //Point A rim distance
        //int distb = abs(sg[vb].x - sg[vb].w); //Point B rim distance
        int dista = sg[va].w;
        int distb = sg[vb].w;
        //The combined rim-distances are equal or bigger to the point distance
        if (abs(sg[va].x - sg[vb].x) <= dista+distb)
        {
           //we can add an edge now
           boost::add_edge(va,vb,sg);
        }
      }
      vib++;
    }
    via++;
  }

  Debug::Scope m_debug("ShapeGraph");
  std::ostringstream outstr(std::ostringstream::out);
  boost::write_graphviz(outstr,sg);
  DEBUG(3,"Dot", outstr.str());

  return sg;
}

/*refine a given ShapeGraph by reducing the edges
 * FIXME: Not working properly
 */
void Vision::ObstacleDetection::refineGraph(ShapeGraph& sg)
{
  bool go_on = true;
  std::pair<vertex_iterator,vertex_iterator> vp;
  vertex_descriptor v1, v2, v3;
  vertex_iterator vi1;
  adjacency_iterator ai1, ai2;

  //Searching for all collapsable vertices
  while (go_on)
  {
    go_on = false;
    vp = boost::vertices(sg);
    vi1 = vp.first;
    std::pair<adjacency_iterator,adjacency_iterator> ap1, ap2;
    //we have still vertices to check
    while (vi1 != vp.second)
    {
      v1 = *vi1;
      // Note: Due to a bug only out_degree does work
      // in_degree is not working.
      if (boost::out_degree(v1,sg) == 1 ) {
          ap1 = boost::adjacent_vertices(v1,sg);
          ai1 = ap1.first;
          v2 = *ai1;
          if (boost::out_degree(v2,sg) == 1)
          {
            ap2 = boost::adjacent_vertices(v2,sg);
            ai2 = ap2.first;
            v3 = *ai2;
            remove_edge(v1,v2,sg);
            remove_edge(v2,v3,sg);
            add_edge(v1,v3,sg);
            go_on = true;
            continue;
          }
      }
      ++vi1;
    }
  }
}

/* Returns all Subgraphs being disjunct connected components
 * */
std::vector<Obstacle> Vision::ObstacleDetection::getObstacles(ShapeGraph& sg)
{
  std::vector<int> component(boost::num_vertices(sg));
  //find the connected components of this graph
  //int num = boost::connected_components<ShapeGraph , std::vector<int> >(sg, component);
  int num = boost::connected_components(sg, &component[0]);
  std::vector<Obstacle> vec(num);
  for (int i=0; i < num; i++)
  {
    vec[i].u = 0-1; //max
    vec[i].v = 0-1; //max
    vec[i].x = 0; //min
    vec[i].y = 0; //min
  }
  std::pair<vertex_iterator,vertex_iterator> vp;
  vertex_iterator vi;
  vertex_descriptor vd;
  Obstacle ob;
  vp = boost::vertices(sg);
  int j = 0;
  unsigned int u,v,x,y;
  for (vi=vp.first; vi!=vp.second ; vi++, j++)
  {
    vd =*vi;
    ob = vec[component[j]];
    //Point positions
    u = sg[vd].x-sg[vd].w; //upper left x
    x = sg[vd].x+sg[vd].w; //lower right x
    v = sg[vd].y;          //upper left y
    y = sg[vd].y;          //lower right y
    if (u < ob.u) ob.u = u; //move u left to minimum
    if (v < ob.v) ob.v = v; //move v up to minimum
    if (x > ob.x) ob.x = x; //move x right to maximum
    if (y > ob.y) ob.y = y; //move y down to maximum
    vec[component[j]]=ob;
  }
  return vec;
}


