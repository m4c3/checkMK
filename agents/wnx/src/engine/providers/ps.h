
// provides basic api to start and stop service

#pragma once
#ifndef ps_h__
#define ps_h__

#include <ctime>
#include <string>

#include "providers/internal.h"
#include "section_header.h"

namespace cma {

namespace provider {

time_t ConvertWmiTimeToHumanTime(const std::string& creation_date) noexcept;

class Ps : public Asynchronous {
public:
    Ps() : Asynchronous(cma::section::kPsName, '\t') {}

    Ps(const std::string& Name, char Separator)
        : Asynchronous(Name, Separator) {}

    virtual void loadConfig();

private:
    virtual std::string makeBody() const override;
    bool use_wmi_;
    bool full_path_;
};

}  // namespace provider

};  // namespace cma

#endif  // ps_h__
