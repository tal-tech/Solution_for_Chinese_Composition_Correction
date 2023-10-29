#include "mysql_operation.h"
#include "base/logging.h"

namespace sql_utils {
namespace mysql {

std::atomic_uint MySQLOperation::savepoint_seq_{0};

MySQLOperation::ResultSetPtr 
MySQLOperation::ExecuteQuery(const std::string &query_sql, 
                             std::string &err_msg) {
    try {
        MySQLConnAssistant assist;
        std::shared_ptr<sql::Statement> state{assist->createStatement()};
        ResultSetPtr res{state->executeQuery(query_sql)};
        return res;
    } catch (ConnectionNull &e) {
        err_msg = e.what();
    } catch (sql::SQLException &e) {
        err_msg = e.what();
    }
    return nullptr;
}

int MySQLOperation::ExecuteUpdate(const std::string &update_sql, 
                                  std::string &err_msg) {
    int res = -1;
    try {
        MySQLConnAssistant assist;
        std::shared_ptr<sql::Statement> state{assist->createStatement()};
        res = state->executeUpdate(update_sql);
    } catch (ConnectionNull &e) {
        err_msg = e.what();
        res = -1;
    } catch (sql::SQLException &e) {
        err_msg = e.what();
        res = -2;
    }
    return res;
}

int MySQLOperation::ExecuteUpdates(const SQLCollection &update_sqls, 
                                   std::string &err_msg, 
                                   bool trans_ctrl, 
                                   int affect_rows) {
    int res = 0;
    sql::Savepoint *savepoint{nullptr};
    try {
        MySQLConnAssistant assist{!trans_ctrl};
        try {
            if (trans_ctrl) {
                std::string savepoint_name{"update_pos"};
                savepoint_name += "_" + std::to_string(savepoint_seq_++);
                savepoint = assist->setSavepoint(savepoint_name);
            }
            std::shared_ptr<sql::Statement> state{assist->createStatement()};
            for (const auto &sql : update_sqls) {
                res += state->executeUpdate(sql);
                // LOG(INFO) << "res:" << res <<",sql: " << sql;
            }
        } catch (ConnectionNull &e) {
            err_msg = e.what();
            res = -1;
        } catch (sql::SQLException &e) {
            err_msg = e.what();
            res = -2;
        }
        if (trans_ctrl) {
            if ((affect_rows>=0 && affect_rows!=res) || 
                (affect_rows<0 && res<0)) {
                assist->rollback(savepoint);
                err_msg = "partial statement execution failed";
                res = -3;  // 部分成功
            } else {
                assist->commit();
            }
        }
    } catch (ConnectionNull &e) {
        err_msg = e.what();
        res = -1;
    } catch (sql::SQLException &e) {
        err_msg = e.what();
        res = -2;
    }
    if (savepoint) {
        delete savepoint;
    }
    return res;
}

std::string MySQLOperation::ManageException(sql::SQLException &e) {
    std::string msg;
    if (e.getErrorCode() != 0) {
        msg += "error_msg: ";
        msg += e.what();
        msg += ", SQLState: ";
        msg += e.getSQLState();
        msg += ", error_code: ";
        msg += e.getErrorCode();
    }
    return msg;
}

bool MySQLOperation::EscapeString(sql::SQLString &dest, 
                                  const std::string &src, 
                                  std::string &err_msg) {
    bool res = false;
    try {
        MySQLConnAssistant assist;
        auto raw_conn = assist.GetRawConn();
        if (!raw_conn) {
            err_msg = "failed to get connection";
            return res;
        }
        using MySQLConnection = sql::mysql::MySQL_Connection;
        auto conn = std::dynamic_pointer_cast<MySQLConnection>(raw_conn);
        if (!conn) {
            err_msg = "failed to convert connection";
            return res;
        }
        dest = conn->escapeString(src);
        res = true;
    } catch (ConnectionNull &e) {
        err_msg = e.what();
    } catch (sql::SQLException &e) {
        err_msg = e.what();
    }
    return res;
}

}  // namespace mysql
}  // namespace sql_utils
