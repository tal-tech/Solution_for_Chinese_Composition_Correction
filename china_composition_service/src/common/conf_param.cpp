#include "conf_param.h"
#include "base/strings/string_split.h"
#include "base/strings/string_number_conversions.h"

#include <fstream>

using namespace base;

ConfParam::TConfParam ConfParam::params_;

int ConfParam::ParseParam(const std::string &params) {
    StringPairs conf_pairs;
    if (!SplitStringIntoKeyValuePairs(params, '=', '\n', &conf_pairs)) {
        return -1;
    }
    for (unsigned i=0; i<conf_pairs.size(); ++i) {
        params_[conf_pairs.at(i).first] = conf_pairs.at(i).second;
    }
    return 0;
}

int ConfParam::WriteParams(const std::string &config_file) {
    if (config_file.empty()) {
        return -1;
    }

    std::ofstream out{config_file, std::ios::trunc};
    for (auto &param : params_) {
        out << param.first << "=" << param.second << std::endl;
    }
    out.close();
    return 0;
}
