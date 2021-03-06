//
// THIS is pre-compiled header for Engine Project
//
#pragma once
#ifndef ENGINE_STDAFX_H__
#define ENGINE_STDAFX_H__

#include "stdafx_defines.h"  // shared use, watest!

// settings for the LWA
#define _SILENCE_CXX17_CODECVT_HEADER_DEPRECATION_WARNING
#define SI_SUPPORT_IOSTREAMS

#include "common/version.h"

#include "asio.h"

#include "tools/_raii.h"  // ON_OUT_OF_SCOPE
#include "tools/_xlog.h"  // internal tracing and dumping

#include "common/cfg_info.h"  // internal tracing and dumping

#include "logger.h"

#endif  // ENGINE_STDAFX_H__
