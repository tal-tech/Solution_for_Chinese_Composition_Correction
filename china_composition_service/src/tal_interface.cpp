#include "tal_interface.h"
#include "base/base64.h"
#include "base/logging.h"
#include "base/time/time.h"

#include <exception>


std::string TALInterface::app_name_{"UNDEFINED"};
std::atomic_int TALInterface::trim_count_{0};

TALError TALInterface::ParseRequestBody() {
    try {
        Json::Reader reader;
        if (!reader.parse(request_body_, request_body_json_)) {
            return SERVICE_ERROR.E_UNKNOWN_REQ;
        }
        if (!request_body_json_.isObject()) {
            return SERVICE_ERROR.E_UNKNOWN_REQ;
        }
    } catch (std::exception &e) {
        return SERVICE_ERROR.E_UNKNOWN_REQ;
    }
    return SERVICE_ERROR.E_OK;
}
