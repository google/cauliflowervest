#include "base/safe_strerror_posix.h"

#include <stdio.h>
#include <string.h>

#include "base/basictypes.h"

// The Chromium implementation of this file is concerned with two distinct
// interfaces to strerror_r, and in the case of the POSIX interface,
// ambiguities regarding null-termination and error handling. Mac OS X only
// implements the POSIX strerror_r interface, and its behaves consistently in
// areas where the specification may be ambiguous. This implementation has
// been simplified compared to the Chromium one, but may only be suitable for
// use on Mac OS X.

void safe_strerror_r(int err, char* buf, size_t len) {
  if (buf == NULL || len <= 0) {
    return;
  }

  int result = strerror_r(err, buf, len);
  if (result != 0) {
    snprintf(buf, len, "Error %d while retrieving error %d", result, err);
  }
}

std::string safe_strerror(int err) {
  char buf[256];
  safe_strerror_r(err, buf, arraysize(buf));
  return std::string(buf);
}
