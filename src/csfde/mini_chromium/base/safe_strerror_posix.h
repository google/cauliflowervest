#ifndef BPOOP_MINI_CHROMIUM_BASE_SAFE_STRERROR_POSIX_H_
#define BPOOP_MINI_CHROMIUM_BASE_SAFE_STRERROR_POSIX_H_
#pragma once

#include <string>

void safe_strerror_r(int err, char *buf, size_t len);
std::string safe_strerror(int err);

#endif  // BPOOP_MINI_CHROMIUM_BASE_SAFE_STRERROR_POSIX_H_
