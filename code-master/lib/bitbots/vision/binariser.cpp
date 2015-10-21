#include  "binariser.hpp"
/* @author Timon Giese
 * contains binarising functions to convert pictures to 8bit binary
 * */
int MAX_GREEN = 100;
int MAX_VALUE = 200; //value for HSV

/**
 * Convert 8Bit-BGR picture into 8bit binary
 * the output Matrix has to be provided by the caller.
 */
void binarize_RGB(Eigen::RMatrixVec3Ub& input, Eigen::RMatrixXUb&& output)
{
  for (int r=0; r < input.rows(); r++)
  {
    uchar * inPtr = const_cast<uchar*>(input.ptr(r));
    uchar * outPtr = const_cast<uchar*>(output.ptr(r));
    for (int ic=1, oc=0; ic < input.cols()*3; ic+=3, oc++)
    {
      if (inPtr[ic] > MAX_GREEN)
      {
        outPtr[oc] = 255;
      }
      else outPtr[oc] = 0;
    }
  }
}

/**
 * Convert a single unsigned Character (HS)V Type to binary
 * TODO: Check what we really get here (*tired*)
 */
void binarize_V(Eigen::RMatrixXUb&&input, Eigen::RMatrixXUb&& output)
{
  for (int r=0; r < input.cols(); r++)
  {
    uchar * inPtr = const_cast<uchar*>(input.ptr(r));
    uchar * outPtr = const_cast<uchar*>(output.ptr<uchar>(r));
    for (int ic=0; ic < input.rows(); ic++)
    {
      if (inPtr[ic] > MAX_VALUE)
      {
        outPtr[ic] = 255;
      }
      else outPtr[ic] = 0;
    }
  }
}
