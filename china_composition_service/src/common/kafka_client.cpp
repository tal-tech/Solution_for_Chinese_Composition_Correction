#include "kafka_client.h"

#include <exception>


KafkaClient* KafkaClient::p_instance_ = nullptr;
std::mutex KafkaClient::m_mutex_;
cppkafka::Producer *KafkaClient::p_producer_ = nullptr;

void KafkaClient::Init(const std::string &hosts, 
                       const std::string &topic) {
    Configuration config = {
        {"metadata.broker.list", hosts},
        {"message.max.bytes", 10*1024*1024}
    };
    m_topic_ = topic;
    if (!p_producer_) {
        p_producer_ = new Producer(config);
    }
}

KafkaClient *KafkaClient::GetInstance() {
    if (!p_instance_) {
        std::lock_guard<std::mutex> lock(m_mutex_);
        if (!p_instance_) {
            p_instance_ = new KafkaClient();
        }
    }
    return p_instance_;
}

KafkaClient::~KafkaClient() {
    if (p_producer_) {
        delete p_producer_;
        p_producer_ = nullptr;
    }

    if (p_instance_) {
        delete p_instance_;
        p_instance_ = nullptr;
    }
}

void KafkaClient::SendMsg(const std::string &msg) {
    try {
        p_producer_->produce(MessageBuilder(m_topic_).payload(msg));
        // p_producer_->flush();
    } catch (const std::exception &e) {
        std::cout<<"mq send msg exception: "<< e.what() << std::endl;
    } catch (...) {
        std::cout<<"mq send msg error" << std::endl;
    }
}
