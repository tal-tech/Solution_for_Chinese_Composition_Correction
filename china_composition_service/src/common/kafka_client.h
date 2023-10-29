#pragma once

#include <iostream>
#include <mutex>
#include "cppkafka/cppkafka.h"


using namespace cppkafka;

class KafkaClient {
public:
    virtual ~KafkaClient();

public:
    void Init(const std::string &hosts, const std::string &topic);
    static KafkaClient *GetInstance();

    void SendMsg(const std::string &msg);
    std::string &Topic() { return m_topic_; }

private:
    KafkaClient() = default;
    KafkaClient(const KafkaClient&) = delete;
    KafkaClient& operator=(const KafkaClient&) = delete;

private:
    static KafkaClient *p_instance_;
    static std::mutex m_mutex_;
    static cppkafka::Producer *p_producer_;
    std::string m_topic_{"datawork-image"};
};

