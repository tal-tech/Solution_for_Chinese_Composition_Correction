#pragma once

#include "hiredis/hiredis.h"

#include <string>
#include <memory>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <iostream>

namespace redis_utils {

class RedisConn {
private:
    redisContext *raw_ctx_{nullptr};
    unsigned version_{0};

public:
    explicit RedisConn(redisContext *ctx, unsigned version=0)
        : raw_ctx_{ctx}, version_{version} {}

    ~RedisConn() {
        std::cout << "destroy a redis conn object" << std::endl;
    }

public:
    inline redisContext *operator*() {
        return raw_ctx_;
    }
};

class RedisConnPool {
private:
    static std::once_flag new_flag_;
    static std::once_flag del_flag_;
    static std::shared_ptr<RedisConnPool> instance_;

    unsigned pool_size_{0};
    unsigned curr_size_{0};
    std::queue<std::shared_ptr<RedisConn>> conn_pool_;
    std::mutex lock_;
    std::condition_variable cond_;
    unsigned version_{0};

    std::string ip_{"127.0.0.1"};
    int port_{6369};
    std::string password_;
    unsigned dbnum_{0};

public:
    static bool InitInstance(const std::string &ip, 
                             int port=6379, 
                             const std::string &password="", 
                             unsigned dbnum=0, 
                             unsigned pool_size=0);
    static void ReleaseInstance();
    static inline std::shared_ptr<RedisConnPool> GetInstance();

    /**
     * @func: to get a redis connection context.
     *
     * @param timeout: maximum wait for seconds to get a redis client
     *  > 0 : block until timeout seconds expired
     *  = 0 : nonblock, return immediately
     *  < 0 : block forever until have get a redis client.
     *
     * @return: a client with connection context when success, 
     *  otherwise nullptr.
     */
    std::shared_ptr<RedisConn> GetRedisConn(int timeout=30);
    bool ReleaseRedisConn(std::shared_ptr<RedisConn> conn);

    ~RedisConnPool();

private:
    explicit RedisConnPool(const std::string &ip, 
                           int port, 
                           const std::string &password, 
                           unsigned dbnum, 
                           unsigned pool_size);

    void InitConnectionPool();
    void ReleaseConnectionPool();

    std::shared_ptr<RedisConn> OpenConnection();
    void CloseConnection(std::shared_ptr<RedisConn> conn) {
        if (!conn) {
            return;
        }
        std::cout << "close a redis connection" << std::endl;
        redisFree(*(*conn));
    }

    bool ExecuteCmd(redisContext *ctx, const std::string &cmd, 
                    std::string &msg);

    bool WaitforConnection(std::unique_lock<std::mutex> &guard, 
                           int timeout);

    bool CheckConnection(std::shared_ptr<RedisConn> conn);
};

std::shared_ptr<RedisConnPool> RedisConnPool::GetInstance() {
    return instance_;
}

class RedisClient {
public:
    std::shared_ptr<RedisConn> conn_{nullptr};

public:
    explicit RedisClient(int timeout=30) 
        : conn_{RedisConnPool::GetInstance()->GetRedisConn(timeout)} {
            // std::cout << "to get a redis client" << std::endl;
    }

    ~RedisClient() {
        ReleaseRedisConn();
    }

    RedisClient(const RedisClient &) = default;
    RedisClient &operator=(const RedisClient &) = default;
    RedisClient(RedisClient &&) = default;
    RedisClient &operator=(RedisClient &&) = default;

public:
    bool ReleaseRedisConn() {
        bool res = false;
        if (conn_) {
            res = RedisConnPool::GetInstance()->ReleaseRedisConn(conn_);
            conn_.reset();
        }
        // std::cout << "release a redis client" << std::endl;
        return res;
    }

    redisContext *operator*() {
        return conn_?*(*conn_):nullptr;
    }

public:
    redisReply *ExecuteCmd(const char *cmd, size_t len);
    redisReply *ExecuteCmdv(int argc, const char **argv, const size_t *argvlen);

    bool ExecuteCmd(const char *cmd, size_t len, std::string &msg) {
        redisReply *reply = ExecuteCmd(cmd, len);
        if (!reply) {
            return false;
        }
        bool res = ReplyToString(reply, msg);
        freeReplyObject(reply);
        return res;
    }

    bool ExecuteCmdv(int argc, const char **argv, const size_t *argvlen, 
                     std::string &msg) {
        redisReply *reply = ExecuteCmdv(argc, argv, argvlen);
        if (!reply) {
            return false;
        }
        bool res = ReplyToString(reply, msg);
        freeReplyObject(reply);
        return res;
    }

    redisReply *ExecuteCmd(const std::string &cmd) {
        return ExecuteCmd(cmd.c_str(), cmd.size());
    }

    bool ExecuteCmd(const std::string &cmd, std::string &msg) {
        return ExecuteCmd(cmd.c_str(), cmd.size(), msg);
    }

private:
    bool ReplyToString(const redisReply *reply, std::string &msg);
};

}
