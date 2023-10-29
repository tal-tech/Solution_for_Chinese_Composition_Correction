#pragma once

#include "redlock.h"

#include <memory>
#include <mutex>


class DistributeLock;

class RedisLock {
public:
    CLock lock_;
    bool error_{true};
    bool locked_{false};

public:
    RedisLock() = default;
    ~RedisLock() {
        Unlock();
    }

    inline void Unlock();
    inline bool IsOK() const { return !error_; }
};

class DistributeLock {
private:
    static std::once_flag new_flag_;
    static std::once_flag del_flag_;
    static std::shared_ptr<DistributeLock> instance_;

    CRedLock *red_lock_{nullptr};

private:
    DistributeLock(const int retry_count, const int delay) 
        : red_lock_{new CRedLock()} {
            red_lock_->SetRetry(retry_count, delay);
    }

public:
    ~DistributeLock() {
        delete red_lock_;
    }

public:
    static bool InitInstance(const int retry_count=3, 
                             const int delay=300);
    static void ReleaseInstance();
    static inline std::shared_ptr<DistributeLock> GetInstance();

    inline void SetRetry(const int retry_count, const int dealy);

    RedisLock Lock(const std::string &resource, const int ttl=1000);
    void Unlock(RedisLock &lock);
};

std::shared_ptr<DistributeLock> DistributeLock::GetInstance() {
    return instance_;
}

void DistributeLock::SetRetry(const int retry_count, 
                              const int delay) {
    if (red_lock_) {
        red_lock_->SetRetry(retry_count, delay);
    }
}

void RedisLock::Unlock() {
    DistributeLock::GetInstance()->Unlock(*this);
}

