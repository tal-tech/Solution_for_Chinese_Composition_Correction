#pragma once

#include "mysql_conn_pool.h"

#include <string>
#include <vector>
#include <memory>
#include <atomic>

namespace sql_utils {
namespace mysql {
/**
 * 暂时只提供部分函数接口，后期根据实际需求进行增加
 */
class MySQLOperation {
public:
    using SQLCollection = std::vector<std::string>;
    using ResultSetPtr = std::shared_ptr<sql::ResultSet>;

private:
    static std::atomic_uint savepoint_seq_;

public:
    static ResultSetPtr ExecuteQuery(const std::string &query_sql, 
                                     std::string &err_msg);
    /**
     * @return: < 0  - 执行insert sql失败
     *          >= 0 - 执行成功，返回插入的记录条数
     */
    static inline int ExecuteInsert(const std::string &insert_sql, 
                                    std::string &err_msg);
    static inline int ExecuteInserts(const SQLCollection &insert_sqls, 
                                     std::string &err_msg, 
                                     bool trans_ctrl=false, 
                                     int affect_rows=-1);
    /**
     * @return: < 0 - 执行delete sql失败
     *          = 0 - 执行delete sql成功，但无满足删除条件记录
     *          > 0 - 执行delete sql成功，已被删除的记录条数
     */
    static inline int ExecuteDelete(const std::string &delete_sql, 
                                    std::string &err_msg);
    /**
     * @return: 不报错即认为成功，即使要删除的记录不存在
     *          >= 0 - 执行所有的delete sql成功，已被删除的记录条数
     *          < 0  - 执行delete sql失败，依据trans_ctrl决定是否回滚
     */
    static inline int ExecuteDeletes(const SQLCollection &delete_sqls, 
                                     std::string &err_msg, 
                                     bool trans_ctrl=false, 
                                     int affect_rows=-1);
    // 返回值含义同ExecuteDelete
    static int ExecuteUpdate(const std::string &update_sql, 
                             std::string &err_msg);
    static int ExecuteUpdates(const SQLCollection &update_sqls, 
                              std::string &err_msg, 
                              bool trans_ctrl=false, 
                              int affect_rows=-1);

    static std::string ManageException(sql::SQLException &e);

    static bool EscapeString(sql::SQLString &dest, 
                             const std::string &src, 
                             std::string &err_msg);
};

int MySQLOperation::ExecuteInsert(const std::string &insert_sql, 
                                  std::string &err_msg) {
    return ExecuteUpdate(insert_sql, err_msg);
}
 
int MySQLOperation::ExecuteInserts(const SQLCollection &insert_sqls, 
                                   std::string &err_msg, 
                                   bool trans_ctrl, 
                                   int affect_rows) {
    return ExecuteUpdates(insert_sqls, err_msg, trans_ctrl, affect_rows);
}

int MySQLOperation::ExecuteDelete(const std::string &delete_sql, 
                                  std::string &err_msg) {
    return ExecuteUpdate(delete_sql, err_msg);
}

int MySQLOperation::ExecuteDeletes(const SQLCollection &delete_sqls, 
                                   std::string &err_msg, 
                                   bool trans_ctrl, 
                                   int affect_rows) {
    return ExecuteUpdates(delete_sqls, err_msg, trans_ctrl, affect_rows);
}

}  // namespace mysql
}  // namespace sql_utils
