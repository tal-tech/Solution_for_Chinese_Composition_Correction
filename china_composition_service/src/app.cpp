#include "app.h"
#include "base/base64.h"
#include "base/logging.h"
#include "base/time/time.h"
#include "curl/curl.h"
#include "json/json.h"
#include "conf_param.h"
#include <apollo_conf.h>
#include <future>
#include <tuple>
#include <image_operation.h>
#include "url_request.hpp"
#include "composion.hpp"

static size_t OnWriteData(void *buffer, 
                          size_t size, 
                          size_t nmemb, 
                          void *lp_void) {
    std::string *str = reinterpret_cast<std::string*>(lp_void);
    if (nullptr == str || nullptr == buffer) {
        return 0;
    }
    str->append((char*)buffer, size * nmemb);
    return size * nmemb;
}

/**
 * 此处对HandleRequest包装一层的目的：防止当前HandleRequest不能很好的
 * 满足后续的需求；若能满足，也可以直接在service_main.cpp的Listen中直
 * 接调用HandleRequest方法
 */
void MicroserviceDemo::ProcessRequest(std::string &response) {
    HandleRequest(response);
}

TALError MicroserviceDemo::handler(Json::Value &result) {
    TALError res;

    if (!Composion::instance()->parse_task(m_details, m_precision, request_id_, cv_image_, result)) {
    	return SERVICE_ERROR.E_INTERNAL_ERROR;
    }

    return SERVICE_ERROR.E_OK;
}
