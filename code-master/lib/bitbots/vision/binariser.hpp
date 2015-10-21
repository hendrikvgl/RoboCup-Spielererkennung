// @author Timon
// TODO: python-bindings fehlen für die zweite methode glaube ich
#include <list>
#include "../util/eigen_util.hpp"

/*Convert 8Bit-BGR picture into 8bit binary
 * the output Matrix has to be provided by the caller. */
void binarize_RGB(Eigen::RMatrixVec3Ub& input, Eigen::RMatrixXUb& output);
void binarize_V(Eigen::RMatrixXUb&&input, Eigen::RMatrixXUb&& output);
