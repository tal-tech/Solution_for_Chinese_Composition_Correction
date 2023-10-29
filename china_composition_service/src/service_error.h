#pragma once

#include "base_error.h"


struct ServiceError : public ImageCommonError {
    ServiceError() = delete;
    ServiceError(const long _sub_code) : 
        ImageCommonError{_sub_code} {}

    /**
     * 增加和服务相关的业务错误码：最后三位起始值为501，举例说明：
     * TALError E_INVOCATION_SERVICE{service_code+501, 
     *      "invocation service failed"};
     */
};

// NOTE：也可以直接使用CommonTechError
struct TechnicalError: public CommonTechError {
    TechnicalError() = delete;
    TechnicalError(const long _sub_code) :
        CommonTechError{_sub_code} {}

    /**
     * 增加和服务相关的技术错误码：最后三位起始值为501，举例说明：
     * TALError E_INVOCATION_SERVICE{tech_service_code+501, 
     *      "call algorithm failed"};
     */
};

// 每个具体的服务，此值可能是不同的，根据实际情况修改
const long sub_code = 53;
const ServiceError SERVICE_ERROR{sub_code};
const TechnicalError TECHNICAL_ERROR{sub_code};
