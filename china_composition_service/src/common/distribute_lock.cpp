#include "distribute_lock.h"
#include "redis_conn_pool.h"

#include <iostream>


std::once_flag DistributeLock::new_flag_;
std::once_flag DistributeLock::del_flag_;
std::shared_ptr<DistributeLock> DistributeLock::instance_{nullptr};

bool DistributeLock::InitInstance(const int retry_count, 
                                  const int delay) {
    std::call_once(new_flag_, [&]() {
                   instance_.reset(new DistributeLock{retry_count, 
                                   delay});
                   });
    return true;
}

void DistributeLock::ReleaseInstance() {
    std::call_once(del_flag_, [&] {
                   instance_.reset();
                   });
}

RedisLock DistributeLock::Lock(const std::string &resource, 
                           const int ttl) {
    RedisLock lock;
    redis_utils::RedisClient client{-1};
    if (!(*client)) {
        lock.error_ = true;
        return lock;
    }
    bool res = red_lock_->Lock(*client, 
                               resource.c_str(), 
                               ttl, 
                               lock.lock_);
    if (res) {
        lock.error_ = false;
        lock.locked_ = true;
    }
    return lock;
}

void DistributeLock::Unlock(RedisLock &lock) {
    if (lock.locked_) {
        redis_utils::RedisClient client{-1};
        if (!(*client)) {
            lock.error_ = true;
            return;
        }
        red_lock_->Unlock(*(client), lock.lock_);
        lock.locked_ = false;
    }
}

