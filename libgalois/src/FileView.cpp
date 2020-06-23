#include <cstdio>
#include <cassert>
#include <string>
#include <iostream>

#include <unistd.h>
#include <sys/mman.h>

#include "galois/FileView.h"
#include "tsuba/tsuba.h"

namespace galois {

FileView::~FileView() { Unbind(); }

void FileView::Unbind() {
  if (valid_) {
    tsuba::Munmap(map_start_);
    valid_ = false;
  }
}

int FileView::Bind(const std::string& filename) {
  tsuba::StatBuf buf;
  int err = tsuba::Stat(filename, &buf);
  if (err) {
    return err;
  }

  return Bind(filename, 0, tsuba::RoundUpToBlock(buf.size));
}

int FileView::Bind(const std::string& filename, uint64_t begin, uint64_t end) {
  assert(begin < end);
  uint64_t file_off    = tsuba::RoundDownToBlock(begin);
  uint64_t map_size    = tsuba::RoundUpToBlock(end - file_off);
  uint64_t region_size = end - begin;

  uint8_t* ptr = tsuba::Mmap(filename, file_off, map_size);
  if (!ptr) {
    return -1;
  }
  Unbind();
  map_size_     = map_size;
  region_size_  = region_size;
  map_start_    = ptr;
  region_start_ = ptr + (begin & tsuba::kBlockOffsetMask); /* NOLINT */
  valid_        = true;
  return 0;
}

} /* namespace galois */
