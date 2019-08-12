#ifndef FANN_FANN_UTILS_H_
#define FANN_FANN_UTILS_H_


#include <rt/rt_api.h>

void dot_prod_entry(void * S);
void compute_per_layer_parallel(int32_t * pSrcA, int32_t * pSrcB, uint32_t blockSize, uint32_t deciPoint, uint32_t nPE, int32_t * resBuffer);

#endif //FANN_FANN_UTILS_H_
