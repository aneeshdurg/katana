#include "galois/runtime/SyncStructures.h"

GALOIS_SYNC_STRUCTURE_BROADCAST(comp_current, unsigned long long);
GALOIS_SYNC_STRUCTURE_REDUCE_SET(comp_current, unsigned long long);
GALOIS_SYNC_STRUCTURE_REDUCE_MIN(comp_current, unsigned long long);

#if __OPT_VERSION__ >= 3
GALOIS_SYNC_STRUCTURE_BITSET(comp_current);
#endif

#if __OPT_VERSION__ == 5
FieldFlags Flags_comp_current;
#endif