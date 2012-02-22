#ifndef BPOOP_MINI_CHROMIUM_BUILD_BUILD_CONFIG_H_
#define BPOOP_MINI_CHROMIUM_BUILD_BUILD_CONFIG_H_
#pragma once

#if defined(__APPLE__)
#define OS_MACOSX 1
#else
#error Please add support for your platform in build/build_config.h
#endif

#if defined(OS_MACOSX)
#define OS_POSIX 1
#endif

// Compiler detection.
#if defined(__GNUC__)
#define COMPILER_GCC 1
#else
#error Please add support for your compiler in build/build_config.h
#endif

#if defined(__x86_64__)
#define ARCH_CPU_X86_FAMILY 1
#define ARCH_CPU_X86_64 1
#define ARCH_CPU_64_BITS 1
#define ARCH_CPU_LITTLE_ENDIAN 1
#elif defined(__i386__)
#define ARCH_CPU_X86_FAMILY 1
#define ARCH_CPU_X86 1
#define ARCH_CPU_32_BITS 1
#define ARCH_CPU_LITTLE_ENDIAN 1
#else
#error Please add support for your architecture in build/build_config.h
#endif

#if defined(OS_POSIX) && defined(COMPILER_GCC) && \
    defined(__WCHAR_MAX__) && \
    (__WCHAR_MAX__ == 0x7fffffff || __WCHAR_MAX__ == 0xffffffff)
#define WCHAR_T_IS_UTF32
#else
#error Please add support for your compiler in build/build_config.h
#endif

#endif  // BPOOP_MINI_CHROMIUM_BUILD_BUILD_CONFIG_H_
