#include "redis_conn_pool.h"

#include <chrono>
#include <thread>
#include <iostream>
#include <cstring>
#include <boost/shared_ptr.hpp>

namespace redis_utils {

std::once_flag RedisConnPool::new_flag_;
std::once_flag RedisConnPool::del_flag_;
std::shared_ptr<RedisConnPool> RedisConnPool::instance_{nullptr};

bool RedisConnPool::InitInstance(const std::string &ip, 
                                 int port/*=6379*/, 
                                 const std::string &password/*=""*/, 
                                 unsigned dbnum/*=0*/, 
                                 unsigned pool_size/*=16*/) {
    std::call_once(new_flag_, [&]() {
                   instance_.reset(new RedisConnPool(ip, 
                                                     port, 
                                                     password, 
                                                     dbnum, 
                                                     pool_size));
                   });
    if (instance_->pool_size_ != instance_->curr_size_) {
        std::cout << "init redis conn pool error" << std::endl;
        return false;
    }
    std::cout << "init redis conn pool success" << std::endl;
    return true;
}

void RedisConnPool::ReleaseInstance() {
    std::call_once(del_flag_, [&]() {
                   instance_.reset();
                   });
    std::cout << "have release instance" << std::endl;
}

RedisConnPool::RedisConnPool(const std::string &ip, 
                             int port, 
                             const std::string &password, 
                             unsigned dbnum, 
                             unsigned pool_size) 
    : pool_size_{pool_size}, ip_{ip}, port_{port}, 
    password_{password}, dbnum_{dbnum} {
    InitConnectionPool();
}

RedisConnPool::~RedisConnPool() {
    ReleaseConnectionPool();
}

void RedisConnPool::InitConnectionPool() {
    std::unique_lock<std::mutex> guard{lock_};
    for (unsigned idx = 0; idx < pool_size_; ++idx) {
        auto conn = OpenConnection();
        if (conn) {
            ++curr_size_;
            conn_pool_.push(conn);
        }
    }
}

void RedisConnPool::ReleaseConnectionPool() {
    std::unique_lock<std::mutex> guard{lock_};
    std::cout << "release connection pool, available_conn_size: " 
        << conn_pool_.size() << std::endl;
    while (!conn_pool_.empty()) {
        auto conn = conn_pool_.front();
        CloseConnection(conn);
        conn_pool_.pop();
        --curr_size_;
    }
    if (curr_size_ > 0) {
        std::cerr << "some connection maybe used: " 
            << curr_size_ << std::endl;
    }
}

std::shared_ptr<RedisConn> RedisConnPool::GetRedisConn(int timeout) {
    if (pool_size_ == 0) {
        std::cerr << "connection pool size is zero" << std::endl;
        return nullptr;
    }
    if (curr_size_ == 0) {
        std::cerr << "no connection in pool" << std::endl;
        return nullptr;
    }

    // TODO：当curr_size_的值小于pool_size_，且conn_pool_为空时应先建立连接
    std::unique_lock<std::mutex> guard{lock_};
    if (conn_pool_.empty()) {
        if (timeout == 0) {
            std::cerr << "no available redis connection" << std::endl;
            return nullptr;
        } else if (timeout < 0) {
            while (conn_pool_.empty()) {
                cond_.wait(guard);
            }
        } else {
            if (!WaitforConnection(guard, timeout)) {
                return nullptr;
            }
        }
    }

    auto conn = conn_pool_.front();
    conn_pool_.pop();

    if (!CheckConnection(conn) && !(conn=OpenConnection())) {
        std::cerr << "get: fail to open a new redis connection" 
            << std::endl;
        return nullptr;
    }

    return conn;
}

bool RedisConnPool::CheckConnection(std::shared_ptr<RedisConn> conn) {
    if (!conn) {
        return false;
    }

    auto ctx = *(*conn);
    if (!ctx || ctx->err) {
        if (ctx) {
            redisFree(ctx);
        }
        return false;
    }

    redisReply *reply = (redisReply*)redisCommand(ctx, "PING");
    if (!reply) {
        return false;
    }
    bool res = true;
    if (reply->type!=REDIS_REPLY_STATUS || 
        strcasecmp(reply->str,"PONG")!=0) {
        res = false;
    }
    freeReplyObject(reply);
    return res;
}

bool RedisConnPool::ReleaseRedisConn(std::shared_ptr<RedisConn> conn) {
    // std::cout << "release a redis conneciton" << std::endl;
    if (!conn) {
        std::cerr << "release a null redis connection" << std::endl;
        // return false;
    }

    // if (!CheckConnection(conn) && !(conn=OpenConnection())) {
    //     std::cerr << "release: fail to open a new redis connection" 
    //         << std::endl;
    //     return false;
    // }

    std::unique_lock<std::mutex> guard{lock_};
    conn_pool_.push(conn);
    cond_.notify_one();
    return true;
}

std::shared_ptr<RedisConn> RedisConnPool::OpenConnection() {
    std::string msg{"success to create redis connection."};
    auto conn = redisConnect(ip_.c_str(), port_);
    do {
        if (!conn || conn->err) {
            msg = conn?conn->errstr:"can't allocate redis context";
            break;
        }

        std::string cmd;
        if (!password_.empty()) {
            cmd = "AUTH " + password_;
            if (!ExecuteCmd(conn, cmd, msg)) {
                break;
            }
        }

        cmd = "SELECT " + std::to_string(dbnum_);
        if (!ExecuteCmd(conn, cmd, msg)) {
            break;
        }

        std::cout << "connect redis success" << std::endl;
        return std::make_shared<RedisConn>(conn, version_);
    } while(false);

    if (!conn) {
        redisFree(conn);
    }
    std::cout << "connect redis error: " << msg << std::endl;

    return nullptr;
}

bool RedisConnPool::ExecuteCmd(redisContext *ctx, 
                               const std::string &cmd, 
                               std::string &msg) {
    bool res = false;
    redisReply *reply = (redisReply *)redisCommand(ctx, cmd.c_str());
    do {
        if (!reply) {
            msg = "execute command '" + cmd + "' error: ";
            msg += ctx->errstr?ctx->errstr:"can't allocate reply object";
            break;
        }
        if (reply->type == REDIS_REPLY_ERROR) {
            msg = "execute command '" + cmd + "' error";
            if (reply->str) {
                msg += ": " + std::string{reply->str};
            }
            break;
        } else if (reply->type == REDIS_REPLY_STATUS) {
            if (reply->str && strcmp(reply->str, "OK")!=0) {
                msg = "execute command '" + cmd + "' error: " + reply->str;
                break;
            }
        }

        res = true;
        msg = "execute command '" + cmd + "' success";
    } while(false);

    if (reply) {
        freeReplyObject(reply);
    }

    return res;
}

bool RedisConnPool::WaitforConnection(std::unique_lock<std::mutex> &guard, 
                                      int timeout) {
    using namespace std::chrono;
    auto wait_time = milliseconds{(int64_t)timeout * 1000};
    int64_t time_span = 0;
    while (conn_pool_.empty()) {
        wait_time = milliseconds(int64_t(wait_time.count())- time_span);
        auto start = system_clock::now();
        auto res = cond_.wait_for(guard, wait_time);
        if (res == std::cv_status::timeout) {
            // std::cerr << "get redis connection timeout " << std::endl;
            return false;
        }
        auto end = system_clock::now();
        auto duration = duration_cast<microseconds>(end - start);
        time_span = int64_t(duration.count()/1000);
    }
    return true;
}

redisReply *RedisClient::ExecuteCmd(const char *cmd, size_t len) {
    if (!cmd || len==0) {
        std::cerr << "invalid command" << std::endl;
        return nullptr;
    }

    if (!conn_) {
        std::cerr << "redis client's connection is null" << std::endl;
        return nullptr;
    }
    auto ctx = *(*conn_);
    if (!ctx) {
        std::cerr << "redis client's context is null" << std::endl;
        return nullptr;
    }
    redisReply *reply = (redisReply*)redisCommand(ctx, cmd, len);
    return reply;
}

redisReply *RedisClient::ExecuteCmdv(int argc, 
                                     const char **argv, 
                                     const size_t *argvlen) {
    if (!conn_) {
        std::cerr << "redis client's connection is null" << std::endl;
        return nullptr;
    }
    auto ctx = *(*conn_);
    if (!ctx) {
        std::cerr << "redis client's context is null" << std::endl;
        return nullptr;
    }
    redisReply *reply = (redisReply*)redisCommandArgv(ctx, 
                                                      argc, 
                                                      argv, 
                                                      argvlen);
    return reply;
}

bool RedisClient::ReplyToString(const redisReply *reply, 
                                std::string &msg) {
    if (!reply) {
        msg = "reply object is null";
        return false;
    }
    if (reply->type == REDIS_REPLY_INTEGER) {
        msg = std::to_string(reply->integer);
        return true;
    } else if(reply->type == REDIS_REPLY_STRING) {
        msg.assign(reply->str, reply->len);
        return true;
    } else if(reply->type == REDIS_REPLY_STATUS) {
        msg.assign(reply->str, reply->len);
        return true;
    } else if(reply->type == REDIS_REPLY_NIL) {
        msg = "";
        return true;
    } else if(reply->type == REDIS_REPLY_ERROR) {
        msg.assign(reply->str, reply->len);
        return false;
    } else if(reply->type == REDIS_REPLY_ARRAY) {
        msg = "not support array result!!!";
        return false;
    } else {
        msg = "undefined reply type";
        return false;
    }
}

}  // namespace: redis_utils
