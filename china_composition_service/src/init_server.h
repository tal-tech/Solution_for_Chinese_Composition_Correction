#pragma once

#include "breakpad/src/client/linux/handler/exception_handler.h"
#include "base/logging.h"
#include "base/command_line.h"
#include "crow_all.h"

#include <string>
#include <vector>
#include <functional>

using namespace base;
using namespace logging;

// 服务当前运行的环境：LOCAL TEST PRE PROD
enum class CURRENT_ENV{LOCAL, TEST, PRE, PROD};
extern CURRENT_ENV g_current_env;

// 注册到Eureka注册中心，取消注册会在ReleaseService中自动进行
void ConnectEureka();

/**
 * 1.InitService和ReleaseService成对出现；
 * 2.InitService用于服务基础功能的初始化，提供服务能够在PaaS上运行的最低保证
 * 3.每个服务特色的初始化逻辑，需要单独完成
 * 4.需要配置的环境变量：
 *   CURRENT_ENV - 用于标识当前的运行环境
 *   APOLLO_HOST - apollo配置中心地址
 *   APOLLO_APP_ID - 该服务在apollo配置中心的AppId
 *   SERVICE_TYPE - 服务类型：image speech text other
 *   NOTE：为了方便本地多个不同服务测试，LOCAL环境依然读取config/config.ini中
 *         的apollo地址和AppId
 */
void InitService();
void ReleaseService();

enum class HTTP_METHOD{POST, PUT, GET, UPDATE};
using ListenURL = std::pair<const std::string, HTTP_METHOD>;
using EventFunc = std::function<void(const crow::request &, 
                                     std::string&)>;
// 结构：<<url, http_method>, request_callback>
using RequestEvents = std::vector<std::pair<ListenURL, EventFunc>>;
// 开始监听请求
void Listen(RequestEvents &events);
