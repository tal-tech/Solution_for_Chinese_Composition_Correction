#pragma once

#include <unordered_map>
#include <string>
#include <typeinfo>
#include <iostream>

class ConfParam {
    using TConfParam = std::unordered_map<std::string, std::string>;

private:
    static TConfParam params_;

public:
    explicit ConfParam() = default;

    static int ParseParam(const std::string &params);
    static int WriteParams(const std::string &config_file);

    static inline 
    int SetValue(const std::string &key, const std::string &value);
    template<class TValue> static inline
    int SetValue(const std::string &key, const TValue &value);

    static inline 
    const std::string &GetValue(const std::string &key, 
                                const std::string &def_val);
    static inline 
    int GetValue(const std::string &key, const int def_value);
    static inline 
    double GetValue(const std::string &key, const double def_val);
};

int ConfParam::SetValue(const std::string &key, 
                        const std::string &value) {
    if (key.empty() || value.empty()) {
        return -1;
    }
    params_[key] = value;
    return 0;
}

template<class TValue> 
int ConfParam::SetValue(const std::string &key, const TValue &value) {
    if (key.empty()) {
        return -1;
    }
    params_[key] = std::to_string(value);
    return 0;
}

const std::string &ConfParam::GetValue(const std::string &key, 
                                       const std::string &def_val) {
    auto it = params_.find(key);
    return it==params_.end()?def_val:it->second;
}

int ConfParam::GetValue(const std::string &key, const int def_val) {
    auto it = params_.find(key);
    return it==params_.end()?def_val:std::stoi(it->second);
}

double ConfParam::GetValue(const std::string &key, const double def_val) {
    auto it = params_.find(key);
    return it==params_.end()?def_val:std::stod(it->second);
}
