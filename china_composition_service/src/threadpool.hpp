/*
 * threadpool.hpp
 *
 *  Created on: 2020年12月2日
 *      Author: ym
 */
#pragma once
#ifndef THREAD_POOL_H
#define THREAD_POOL_H

#include <vector>
#include <iostream>
#include <queue>
#include <thread>
#include <atomic>
#include <condition_variable>
#include <future>
#include <functional>
#include <stdexcept>

namespace std
{
#define  MAX_THREAD_NUM 100

class ThreadPool
{
private:
    using Task = std::function<void()>;
    std::vector<std::thread> pool;
    std::queue<Task> tasks;
    std::mutex m_lock;
    std::condition_variable cv_task;
    int max_tasks_len;
    bool stoped;

public:
    inline ThreadPool(unsigned short size = 4, unsigned int max_task_len = 10000) :stoped{ false }
    {
    	max_tasks_len = max_task_len;
    	size = size == 0?MAX_THREAD_NUM:size;
    	size = size >= MAX_THREAD_NUM?MAX_THREAD_NUM:size;
    	for (; size > 0; --size)
        {   //初始化线程数量
            pool.emplace_back(
                [this]
                {
                    while(!this->stoped)
                    {
                        std::function<void()> task;
                        {
                            std::unique_lock<std::mutex> lock{ this->m_lock };
                            this->cv_task.wait(lock,
                                [this] {
                                    return this->stoped || !this->tasks.empty();
                                }
                            );
                            if (this->stoped && this->tasks.empty())
                                return;
                            task = std::move(this->tasks.front()); // 取一个 task
                            this->tasks.pop();
                        }
                        task();
                    }
                }
            );
        }
    }
    inline ~ThreadPool()
    {
        this->stoped = true;
        cv_task.notify_all(); // 唤醒所有线程执行
        for (std::thread& thread : pool) {
            thread.detach(); // 让线程“自生自灭”
//            if(thread.joinable())
//                thread.join(); // 等待任务结束， 前提：线程一定会执行完
        }
    }

public:
    template<typename F, typename... Args>
    auto commit(F&& f, Args&&... args) ->std::future<decltype(f(args...))>
    {
        if (this->stoped)
            throw std::runtime_error("commit on ThreadPool is stopped.");
        using RetType = decltype(f(args...));
        auto task = std::make_shared<std::packaged_task<RetType()> >(
            std::bind(std::forward<F>(f), std::forward<Args>(args)...)
        );
        std::future<RetType> future = task->get_future();
        {
            std::lock_guard<std::mutex> lock{ m_lock };
//            if (tasks.size() > max_tasks_len) {
//            	throw std::runtime_error("tasks queues full.");
//            }

            tasks.emplace(
                [task]()
                {
                    (*task)();
                }
            );
        }

        cv_task.notify_one(); // 唤醒一个线程执行

        return future;
    }
};
}
#endif
