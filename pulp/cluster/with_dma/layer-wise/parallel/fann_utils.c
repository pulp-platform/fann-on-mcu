//Copyright (c) 2018 ETH Zurich, Xiaying Wang, Ferdinand von Hagen, Lukas Cavigelli, Michele Magno

#include "fann_conf.h"
#include "fann_utils.h"
#include "rt/rt_api.h"
#include "plp_math.h"


// The PULP-DSP is not open-sourced yet, so I'm copying the dsp functions here before fann_run.
void plp_dot_prod_q32s_xpulpv2(
                               const int32_t * __restrict__ pSrcA,
                               const int32_t * __restrict__ pSrcB,
                               uint32_t blockSize,
                               uint32_t deciPoint,
                               int32_t * __restrict__ pRes){
  uint32_t blkCnt, tmpBS;                   /* Loop counter, temporal BlockSize */
        int32_t sum = 0; //, sum1 =0;                          /* Temporary return variable */

#if defined(PLP_MATH_LOOPUNROLL)

        tmpBS = (blockSize>>1);

        for (blkCnt=0; blkCnt<tmpBS; blkCnt++){

	sum += (*pSrcA++) * (*pSrcB++) >> deciPoint;
	sum += (*pSrcA++) * (*pSrcB++) >> deciPoint;

        }

        for (blkCnt=0; blkCnt<(blockSize%2U); blkCnt++){
          sum += (*pSrcA++) * (*pSrcB++) >> deciPoint;
        }

#else // PLP_MATH_LOOPUNROLL

        for (blkCnt=0; blkCnt<blockSize; blkCnt++){
          sum += (*pSrcA++) * (*pSrcB++) >> deciPoint;
        }

#endif // PLP_MATH_LOOPUNROLL

        * pRes = sum; // + sum1;

}



void dot_prod_entry(void * S){

  //uint32_t nPE = ((plp_dot_prod_instance_q32 *)S)->nPE;
  uint32_t blkSizePE = ((plp_dot_prod_instance_q32 *)S)->blkSizePE;
  int core_id = rt_core_id();
  int32_t * pSrcA = (int32_t*)(((plp_dot_prod_instance_q32 *)S)->pSrcA) + blkSizePE * core_id;
  int32_t * pSrcB = (int32_t*)(((plp_dot_prod_instance_q32 *)S)->pSrcB); // + blkSizePE * core_id;
  
  uint32_t deciPoint = ((plp_dot_prod_instance_q32 *)S)->deciPoint;
  
  int32_t * resBufferPE = &(((plp_dot_prod_instance_q32 *)S)->resBuffer[core_id]);


  //rt_team_barrier();

  plp_dot_prod_q32s_xpulpv2(pSrcA, pSrcB, blkSizePE, deciPoint, resBufferPE);


}

void compute_per_layer_parallel(int32_t * pSrcA, int32_t * pSrcB, uint32_t blockSize, uint32_t deciPoint, uint32_t nPE, int32_t * resBuffer){

  plp_dot_prod_instance_q32 S;
  S.pSrcA = pSrcA;
  S.pSrcB = pSrcB;
  S.blkSizePE = blockSize;
  S.deciPoint = deciPoint;
  //S.nPE = nPE;
  S.resBuffer = resBuffer;

  rt_team_fork(nPE, dot_prod_entry, (void *) &S);

  //rt_team_barrier();
}

