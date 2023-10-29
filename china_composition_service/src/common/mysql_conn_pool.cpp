#include "mysql_conn_pool.h"

#include <iostream>
#include <chrono>
#include <thread>

namespace sql_utils {
namespace mysql {

std::once_flag MySQLConnPool::new_flag_;
std::once_flag MySQLConnPool::del_flag_;
std::shared_ptr<MySQLConnPool> MySQLConnPool::instance_{nullptr};
unsigned int MySQLConnPool::version_{1};
std::thread *MySQLConnPool::monitor_{nullptr};
bool MySQLConnPool::monitor_flag_{false};

void MySQLConnPool::InitInstance(const std::string &host, 
                                 const std::string &user_name, 
                                 const std::string &password, 
                                 const std::string &db_name, 
                                 const unsigned pool_size, 
                                 const int port) {
    std::call_once(new_flag_, [&]() {
                   instance_.reset(new MySQLConnPool(host, 
                                                 user_name, 
                                                 password, 
                                                 db_name, 
                                                 pool_size, 
                                                 port));
                   });
}

void MySQLConnPool::ReleaseInstance() {
    std::call_once(del_flag_, [&]() {
                   instance_.reset();
                   });
}

MySQLConnPool::MySQLConnPool(const std::string &host_name, 
                             const std::string &user_name, 
                             const std::string &password, 
                             const std::string &db_name, 
                             const unsigned pool_size, 
                             const int port) 
    : pool_size_{pool_size} {
    conn_properties_["hostName"] = host_name;
    conn_properties_["userName"] = user_name;
    conn_properties_["password"] = password;
    conn_properties_["schema"] = db_name;
    conn_properties_["port"] = port;
    conn_properties_["OPT_RECONNECT"] = true;
    conn_properties_["CLIENT_FOUND_ROWS"] = true;
    driver_ = sql::mysql::get_mysql_driver_instance();
    auto size = pool_size / 2;
    if (pool_size & 0x01) {
        ++size;
    }
    InitConnectionPool(size);

    monitor_ = new std::thread(&MySQLConnPool::MonitorConnPool, 
                               std::ref(*this));
    monitor_flag_ = true;
}

MySQLConnPool::~MySQLConnPool() {
    monitor_flag_ = false;
    monitor_->join();
    delete monitor_;
    ReleaseConnectionPool();
}

void MySQLConnPool::InitConnectionPool(const unsigned pool_size) {
    std::unique_lock<std::mutex> guard{lock_};
    for (unsigned i=0; i!=pool_size; ++i) {
        std::shared_ptr<sql::Connection> conn = OpenConnection();
        if (conn) {
            ++curr_pool_size_;
            conn_pool_.push(std::make_shared<MySQLConnection>(conn, version_));
        }
    }
}

std::shared_ptr<sql::Connection> MySQLConnPool::OpenConnection() {
    try {
        sql::Connection *conn = driver_->connect(conn_properties_);
        if (conn) {
            std::cout << "success to open a new mysql connection" << std::endl;
            return std::shared_ptr<sql::Connection>{conn};
        } else {
            std::cerr << "connect mysql error" << std::endl;
        }
    } catch (sql::SQLException &e) {
        std::cerr << "conncet mysql error: " << e.what() << std::endl;
    }
    return nullptr;
}

std::shared_ptr<MySQLConnection> 
MySQLConnPool::_GetConnection(bool auto_commit) {
    std::shared_ptr<MySQLConnection> conn{conn_pool_.front()};
    conn_pool_.pop();
    // 注意：每次检测连接是否断开消耗性能
    if (!(*conn)->isValid() && !Reconnect(conn->raw_conn_)) {
        std::cerr << "reconnect to mysql error" << std::endl;
        --curr_pool_size_;
        return nullptr;
    }
    if (!auto_commit) {
        conn->auto_commit_ = false;
        try {
            (*conn)->setAutoCommit(false);
        } catch (sql::SQLException &e) {
            std::cerr << "set auto commit: " << e.what() << std::endl;
        }
    }
    return conn;
}

std::shared_ptr<MySQLConnection> 
MySQLConnPool::_GetConnection(std::unique_lock<std::mutex> &guard, 
                              bool auto_commit, 
                              int timeout) {
    using namespace std::chrono;
    auto wait_time = milliseconds{(int64_t)timeout * 1000};
    int64_t time_span = 0;
    while (conn_pool_.empty()) {
        wait_time = milliseconds(int64_t(wait_time.count())- time_span);
        auto start = system_clock::now();
        auto res = cond_.wait_for(guard, wait_time);
        if (res == std::cv_status::timeout) {
            std::cerr << "get connection timeout " << std::endl;
            return nullptr;
        }
        auto end = system_clock::now();
        auto duration = duration_cast<microseconds>(end - start);
        time_span = int64_t(duration.count()/1000);
    }
    return _GetConnection(auto_commit);
}

std::shared_ptr<MySQLConnection> 
MySQLConnPool::GetConnection(bool auto_commit, 
                             bool block, 
                             int timeout) {
    if (pool_size_ == 0) {
        std::cerr << "connection pool size is zero" << std::endl;
        return nullptr;
    }
    std::unique_lock<std::mutex> guard{lock_};
    if (!conn_pool_.empty()) {
        return _GetConnection(auto_commit);
    }

    if (curr_pool_size_ >= pool_size_) {
        if (!block) {
            std::cerr << "have reached max pool size" << std::endl;
            return nullptr;
        } else {
            if (timeout <= 0) {
                timeout = 0x7FFFFFFF;
            }
            return _GetConnection(guard, auto_commit, timeout);
        }
    } else {
        std::shared_ptr<sql::Connection> conn{OpenConnection()};
        if (!conn) {
            return nullptr;
        }
        ++curr_pool_size_;
        if (!auto_commit) {
            try {
                conn->setAutoCommit(false);
            } catch (sql::SQLException &e) {
                std::cout << "set auto commit: " << e.what() << std::endl;
            }
        }
        return std::make_shared<MySQLConnection>(conn, version_, auto_commit);
    }
    return nullptr;
}

bool MySQLConnPool::Reconnect(std::shared_ptr<sql::Connection> conn) {
    try {
        bool res = conn->reconnect();
        return res;
    } catch (sql::SQLException &e) {
        std::cerr << "reconnect mysql error: " << e.what() << std::endl;
    }
    return false;
}

void MySQLConnPool::ReleaseConnection(std::shared_ptr<MySQLConnection> conn) {
    if (conn && conn->raw_conn_) {
        if (conn->version_ < version_ ) {
            (*conn)->close();
            conn->raw_conn_ = OpenConnection();
            std::cout << "version: " << version_ 
                << " " << conn->version_ << std::endl;
            conn->version_ = version_;
        }
        std::unique_lock<std::mutex> guard{lock_};
        if (!conn->raw_conn_) {
            --curr_pool_size_;
            return;
        }
        if (!conn->auto_commit_) {
            try {
                (*conn)->setAutoCommit(true);
                conn->auto_commit_ = true;
            } catch (sql::SQLException &e) {
                std::cout << "set auto commit: " << e.what() << std::endl;
            }
        }
        conn_pool_.push(conn);
        cond_.notify_all();
    } else {
        std::cerr << "release a null connection" << std::endl;
    }
}

void MySQLConnPool::CloseConnection(std::shared_ptr<sql::Connection> conn) {
    if (!conn) {
        return;
    }
    try {
        conn->close();
    } catch (sql::SQLException &e) {
        std::cerr << "close connection error: " << e.what() << std::endl;
    }
}

void MySQLConnPool::ReleaseConnectionPool() {
    std::unique_lock<std::mutex> guard{lock_};
    while (!conn_pool_.empty()) {
        auto conn = conn_pool_.front();
        CloseConnection(conn->raw_conn_);  // ignore error
        conn_pool_.pop();
    }
    curr_pool_size_ = 0;
}

void MySQLConnPool::UpdateConfig(const std::string &host_name,
                             const std::string &user_name,
                             const std::string &password,
                             const std::string &db_name) {
    if (instance_ == nullptr) {
        return;
    }
    // 加读写锁，更新连接配置，释放锁
    // 关闭老连接，减少curr_pool_size_，增加config_version
    // 正在使用的连接在ReleaseConnection的时候检查版本号，如果不是最新的，
    // 需要重新连接
    std::lock_guard<std::mutex> guard{lock_};
    conn_properties_["hostName"] = host_name;
    conn_properties_["userName"] = user_name;
    conn_properties_["password"] = password;
    conn_properties_["schema"] = db_name;
    unsigned available_size = conn_pool_.size();
    while (!conn_pool_.empty()) {
        auto conn = conn_pool_.front();
        (*conn)->close();
        conn_pool_.pop();
        --curr_pool_size_;
    }
    for (unsigned i=0; i!=available_size; ++i) {
        std::shared_ptr<sql::Connection> conn = OpenConnection();
        if (conn) {
            ++curr_pool_size_;
            conn_pool_.push(std::make_shared<MySQLConnection>(conn, version_));
        }
    }
    ++version_;
}

void MySQLConnPool::KeepConnection(std::shared_ptr<MySQLConnection> conn) {
    try {
        std::shared_ptr<sql::Statement> state{(*conn)->createStatement()};
        std::string sql{"SELECT count(*) FROM CONN_PING"};
        std::shared_ptr<sql::ResultSet> res{state->executeQuery(sql)};
    } catch (sql::SQLException &e) {
        std::cerr << "keepConnection: " << e.what() << std::endl;
    }
}

void MySQLConnPool::MonitorConnPool() {
    while (monitor_flag_) {
        for (unsigned i=0; i<curr_pool_size_; ++i) {
            auto conn = GetConnection();
            if (conn) {
                KeepConnection(conn);
                ReleaseConnection(conn);
            } else {
                std::cerr << "connection null" << std::endl;
            }
        }

        std::cout << "one round of detection has been completed" 
            << std::endl;

        int wait_count = 1200;
        while (wait_count>0 && monitor_flag_) {
            std::this_thread::sleep_for(std::chrono::seconds(3));
            --wait_count;
        }
    }
}

}   // mysql
}   // sql_utils
