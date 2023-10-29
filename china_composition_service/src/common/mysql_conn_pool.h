/**
 * mysql_conn_pool: implement mysql connection pool by using c++.
 * 
 * dependencies: mysql_connector v1.1
 *
 * author: stephen
 * date  : 2019-09-20
 *
 * TODO:
 *   1.将每次获取连接时判断连接是否正常的逻辑调整为通过监控线程来实现，
 *     具体策略：定时检测当前连接池中的1/3个连接是否正常：若存在连接异
 *     常，则检测全部连接并修复异常连接，若修复失败则缩短检测时间继续尝
 *     试修复，直至全部修复成功后恢复原来的检测时间间隔；若不存在异常连
 *     接则退出本次检测，等待下一个检测周期
 *   2.连接池中可用连接数动态检测：监控线程同时检测当前连接池中可用（
 *     conn_pool_.size）连接数，若超过curr_pool_size_的1/3，则关闭1/3连
 *     接；若少于curr_pool_size_的1/3，则新打开1/3连接
 */

#pragma once

#include "mysql_connector/include/mysql_connection.h"
#include "mysql_connector/include/mysql_driver.h"
#include "mysql_connector/include/cppconn/statement.h"

#include <string>
#include <queue>
#include <memory>
#include <mutex>
#include <condition_variable>
#include <vector>
#include <thread>

namespace sql_utils {
namespace mysql {

class ConnectionNull {
public:
    explicit ConnectionNull() = default;

    std::string what() const {
        return std::string{"conn_exception: connection is null"};
    }
};

class MySQLConnection {
public:
    std::shared_ptr<sql::Connection> raw_conn_{nullptr};
    unsigned version_{0};
    bool auto_commit_{true};

public:
    explicit MySQLConnection(std::shared_ptr<sql::Connection> conn, 
                             unsigned version, bool auto_commit=true) 
        : raw_conn_{conn}, version_{version}, auto_commit_{auto_commit} {
    }

    std::shared_ptr<sql::Connection> operator->() {
        if (!raw_conn_) {
            throw ConnectionNull();
        }
        return raw_conn_;
    }
};

class MySQLConnPool {
private:
    sql::ConnectOptionsMap conn_properties_;

    static std::once_flag new_flag_;
    static std::once_flag del_flag_;
    static std::shared_ptr<MySQLConnPool> instance_;

    sql::mysql::MySQL_Driver *driver_{nullptr};

    unsigned pool_size_{16};
    unsigned curr_pool_size_{0};
    std::queue<std::shared_ptr<MySQLConnection>> conn_pool_;
    std::mutex lock_;
    std::condition_variable cond_;

    static std::thread *monitor_;
    static bool monitor_flag_;

public:
    static unsigned int version_;

public:
    /**
     * @param port: 0 - use default mysql's port number
     */
    static void InitInstance(const std::string &host_name,
                             const std::string &user_name,
                             const std::string &password,
                             const std::string &db_name,
                             const unsigned pool_size=16,
                             const int port=0);
    static void ReleaseInstance();
    static inline std::shared_ptr<MySQLConnPool> GetInstance();

    /**
     * @param timeout: maximum wait for seconds when block is false,
     *  it will block forever if timeout is no more than zero.
     */
    std::shared_ptr<MySQLConnection> GetConnection(bool auto_commit=true,
                                                   bool block=true,
                                                   int timeout=30);

    void ReleaseConnection(std::shared_ptr<MySQLConnection> conn);
    inline const unsigned GetCurrentPoolSize() const;
    inline const unsigned GetAvailablePoolSize() const;

    void UpdateConfig(const std::string &host_name,
                      const std::string &user_name,
                      const std::string &password,
                      const std::string &db_name);

    ~MySQLConnPool();

private:
    MySQLConnPool(const std::string &host,
                  const std::string &user_name,
                  const std::string &password,
                  const std::string &db_name,
                  const unsigned pool_size,
                  const int port);

    void InitConnectionPool(const unsigned pool_size);
    void ReleaseConnectionPool();

    std::shared_ptr<MySQLConnection> _GetConnection(bool auto_commit);
    std::shared_ptr<MySQLConnection> _GetConnection(std::unique_lock<std::mutex> &guard,
                                                    bool auto_commit,
                                                    int timeout);

    std::shared_ptr<sql::Connection> OpenConnection();
    bool Reconnect(std::shared_ptr<sql::Connection> conn);
    void CloseConnection(std::shared_ptr<sql::Connection> conn);

    void MonitorConnPool();
    void KeepConnection(std::shared_ptr<MySQLConnection> conn);
};

std::shared_ptr<MySQLConnPool> MySQLConnPool::GetInstance() {
    return instance_;
}

const unsigned MySQLConnPool::GetCurrentPoolSize() const {
    return curr_pool_size_;
}

const unsigned MySQLConnPool::GetAvailablePoolSize() const {
    return pool_size_-curr_pool_size_+(unsigned)conn_pool_.size();
}

class MySQLConnAssistant {
private:
    std::shared_ptr<MySQLConnection> conn_{nullptr};

public:
    explicit MySQLConnAssistant(bool auto_commit=true,
                                bool block=true,
                                int timeout=30)
        : conn_{MySQLConnPool::GetInstance()->GetConnection(auto_commit,
                                                            block,
                                                            timeout)} {
            if (!conn_ || !conn_->raw_conn_) {
                throw ConnectionNull();
            }
    }

    ~MySQLConnAssistant() {
        ReleaseConnection();
    }

    MySQLConnAssistant(const MySQLConnAssistant &) = delete;
    MySQLConnAssistant &operator=(const MySQLConnAssistant &) = delete;
    MySQLConnAssistant(MySQLConnAssistant &&) = delete;
    MySQLConnAssistant &operator=(MySQLConnAssistant &&) = delete;

public:
    std::shared_ptr<sql::Connection> operator->() {
        if (!conn_ || !conn_->raw_conn_) {
            throw ConnectionNull();
        }
        return conn_->raw_conn_;
    }

    void ReleaseConnection() {
        if (conn_) {
            MySQLConnPool::GetInstance()->ReleaseConnection(conn_);
            conn_.reset();
        }
    }

    std::shared_ptr<sql::Connection> GetRawConn() {
        return conn_?conn_->raw_conn_:nullptr;
    }
};

}   // mysql
}   // sql_utils

