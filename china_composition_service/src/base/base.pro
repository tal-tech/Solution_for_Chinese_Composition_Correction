#-------------------------------------------------
#
# Project created by QtCreator 2016-01-28T13:42:07
#
#-------------------------------------------------

QT       -= core gui

TARGET = base
TEMPLATE = lib

INCLUDEPATH += ../ \
    /usr/include/glib-2.0 /usr/lib64/glib-2.0/include

DEFINES += COMPONENT_BUILD BASE_IMPLEMENTATION USE_X11=1 \
    USE_SYMBOLIZE USE_OPENSSL=1 USE_GLIB=1 USE_NSS_CERTS=1 \
    __STDC_CONSTANT_MACROS __STDC_FORMAT_MACROS

QMAKE_CXXFLAGS += -fstack-protector --param=ssp-buffer-size=4 -Werror -pthread \
    -fno-strict-aliasing -Wall -Wextra -Wno-unused-parameter \
    -Wno-missing-field-initializers -fvisibility=hidden -pipe -fPIC \
    -fno-exceptions -fno-rtti -fno-threadsafe-statics \
    -fvisibility-inlines-hidden -std=gnu++11 \
    -m64 -march=x86-64

QMAKE_LFLAGS += -Wl,-z,now -Wl,-z,relro -Wl,--fatal-warnings -Wl,-z,defs -pthread \
    -Wl,-z,noexecstack -fPIC -fuse-ld=gold -m64 -Wl,--disable-new-dtags \
    -Wl,--detect-odr-violations -Wl,--icf=all \

LIBS += -lrt -ldl -lgmodule-2.0 -lgobject-2.0 -lgthread-2.0 -lglib-2.0

CONFIG(debug, debug|release) {
DEFINES += DYNAMIC_ANNOTATIONS_ENABLED=1 _DEBUG _GLIBCXX_DEBUG=1

QMAKE_CXXFLAGS += -O0 -g

LIBS += $$OUT_PWD/../lib/debug/libbase_static.a \
    $$OUT_PWD/../lib/debug/libdynamic_annotations.a \
    $$OUT_PWD/../lib/debug/libevent.a $$OUT_PWD/../lib/debug/libmodp_b64.a \
    $$OUT_PWD/../lib/debug/libsymbolize.a $$OUT_PWD/../lib/debug/libxdg_mime.a

DESTDIR = $$PWD/../lib/debug/
}

CONFIG(release, debug|release) {
DEFINES += NDEBUG NVALGRIND DYNAMIC_ANNOTATIONS_ENABLED=0

QMAKE_CXXFLAGS += -O2

QMAKE_LFLAGS += -Wl,-O1 -Wl,--as-needed -Wl,--gc-sections

LIBS += $$OUT_PWD/../lib/release/libbase_static.a \
    $$OUT_PWD/../lib/release/libdynamic_annotations.a \
    $$OUT_PWD/../lib/release/libevent.a $$OUT_PWD/../lib/release/libmodp_b64.a \
    $$OUT_PWD/../lib/release/libsymbolize.a $$OUT_PWD/../lib/release/libxdg_mime.a

DESTDIR = $$PWD/../lib/release/
}


!defined(TCMALLOC, var) {
DEFINES += NO_TCMALLOC
}

defined(TCMALLOC, var) {
message("enable TCMALLOC")
QMAKE_LFLAGS += -Wl,-uIsHeapProfilerRunning,-uProfilerStart \
    -Wl,-u_Z21InitialMallocHook_NewPKvj,-u_Z22InitialMallocHook_MMapPKvS0_jiiix \
    -Wl,-u_Z22InitialMallocHook_SbrkPKvi,-u_Z21InitialMallocHook_NewPKvm \
    -Wl,-u_Z22InitialMallocHook_MMapPKvS0_miiil,-u_Z22InitialMallocHook_SbrkPKvl \
    -Wl,-u_ZN15HeapLeakChecker12IgnoreObjectEPKv \
    -Wl,-u_ZN15HeapLeakChecker14UnIgnoreObjectEPKv

CONFIG(debug, debug|release) {
LIBS += $$OUT_PWD/../lib/debug/liballocator.a
}
CONFIG(debug, debug|release) {
LIBS += $$OUT_PWD/../lib/release/liballocator.a
}
}

SOURCES += \
    linux_util.cc \
    message_loop/message_pump_glib.cc \
    message_loop/message_pump_libevent.cc \
    metrics/field_trial.cc \
    posix/file_descriptor_shuffle.cc \
    sync_socket_posix.cc \
    third_party/xdg_user_dirs/xdg_user_dir_lookup.cc \
    allocator/allocator_check.cc \
    allocator/allocator_extension.cc \
    at_exit.cc \
    barrier_closure.cc \
    base64.cc \
    base64url.cc \
    base_paths.cc \
    base_paths_posix.cc \
    big_endian.cc \
    bind_helpers.cc \
    build_time.cc \
    callback_helpers.cc \
    callback_internal.cc \
    command_line.cc \
    cpu.cc \
    debug/alias.cc \
    debug/asan_invalid_access.cc \
    debug/crash_logging.cc \
    debug/debugger.cc \
    debug/debugger_posix.cc \
    debug/dump_without_crashing.cc \
    debug/proc_maps_linux.cc \
    debug/profiler.cc \
    debug/stack_trace.cc \
    debug/stack_trace_posix.cc \
    debug/task_annotator.cc \
    deferred_sequenced_task_runner.cc \
    environment.cc \
    feature_list.cc \
    files/file.cc \
    files/file_enumerator.cc \
    files/file_enumerator_posix.cc \
    files/file_path.cc \
    files/file_path_constants.cc \
    files/file_path_watcher.cc \
    files/file_path_watcher_linux.cc \
    files/file_posix.cc \
    files/file_proxy.cc \
    files/file_tracing.cc \
    files/file_util.cc \
    files/file_util_linux.cc \
    files/file_util_posix.cc \
    files/file_util_proxy.cc \
    files/important_file_writer.cc \
    files/memory_mapped_file.cc \
    files/memory_mapped_file_posix.cc \
    files/scoped_file.cc \
    files/scoped_temp_dir.cc \
    guid.cc \
    guid_posix.cc \
    hash.cc \
    json/json_file_value_serializer.cc \
    json/json_parser.cc \
    json/json_reader.cc \
    json/json_string_value_serializer.cc \
    json/json_value_converter.cc \
    json/json_writer.cc \
    json/string_escape.cc \
    lazy_instance.cc \
    location.cc \
    logging.cc \
    md5.cc \
    memory/aligned_memory.cc \
    memory/discardable_memory.cc \
    memory/discardable_memory_allocator.cc \
    memory/discardable_shared_memory.cc \
    memory/memory_pressure_listener.cc \
    memory/memory_pressure_monitor.cc \
    memory/ref_counted.cc \
    memory/ref_counted_memory.cc \
    memory/shared_memory_posix.cc \
    memory/singleton.cc \
    memory/weak_ptr.cc \
    message_loop/incoming_task_queue.cc \
    message_loop/message_loop.cc \
    message_loop/message_loop_task_runner.cc \
    message_loop/message_pump.cc \
    message_loop/message_pump_default.cc \
    metrics/bucket_ranges.cc \
    metrics/histogram.cc \
    metrics/histogram_base.cc \
    metrics/histogram_delta_serialization.cc \
    metrics/histogram_samples.cc \
    metrics/histogram_snapshot_manager.cc \
    metrics/metrics_hashes.cc \
    metrics/persistent_memory_allocator.cc \
    metrics/sample_map.cc \
    metrics/sample_vector.cc \
    metrics/sparse_histogram.cc \
    metrics/statistics_recorder.cc \
    metrics/user_metrics.cc \
    native_library_posix.cc \
    nix/mime_util_xdg.cc \
    nix/xdg_util.cc \
    path_service.cc \
    pending_task.cc \
    pickle.cc \
    posix/global_descriptors.cc \
    posix/safe_strerror.cc \
    posix/unix_domain_socket_linux.cc \
    power_monitor/power_monitor.cc \
    power_monitor/power_monitor_device_source.cc \
    power_monitor/power_monitor_device_source_posix.cc \
    power_monitor/power_monitor_source.cc \
    process/internal_linux.cc \
    process/kill.cc \
    process/kill_posix.cc \
    process/launch.cc \
    process/launch_posix.cc \
    process/memory.cc \
    process/memory_linux.cc \
    process/process_handle.cc \
    process/process_handle_linux.cc \
    process/process_handle_posix.cc \
    process/process_iterator.cc \
    process/process_iterator_linux.cc \
    process/process_linux.cc \
    process/process_metrics.cc \
    process/process_metrics_linux.cc \
    process/process_metrics_posix.cc \
    process/process_posix.cc \
    profiler/alternate_timer.cc \
    profiler/native_stack_sampler.cc \
    profiler/native_stack_sampler_posix.cc \
    profiler/scoped_profile.cc \
    profiler/scoped_tracker.cc \
    profiler/stack_sampling_profiler.cc \
    profiler/tracked_time.cc \
    rand_util.cc \
    rand_util_posix.cc \
    run_loop.cc \
    scoped_native_library.cc \
    sequence_checker_impl.cc \
    sequenced_task_runner.cc \
    strings/latin1_string_conversions.cc \
    strings/nullable_string16.cc \
    strings/pattern.cc \
    strings/safe_sprintf.cc \
    strings/string16.cc \
    strings/string_number_conversions.cc \
    strings/string_piece.cc \
    strings/stringprintf.cc \
    strings/string_split.cc \
    strings/string_util.cc \
    strings/string_util_constants.cc \
    strings/sys_string_conversions_posix.cc \
    strings/utf_offset_string_conversions.cc \
    strings/utf_string_conversions.cc \
    strings/utf_string_conversion_utils.cc \
    supports_user_data.cc \
    synchronization/cancellation_flag.cc \
    synchronization/condition_variable_posix.cc \
    synchronization/lock.cc \
    synchronization/lock_impl_posix.cc \
    synchronization/waitable_event_posix.cc \
    synchronization/waitable_event_watcher_posix.cc \
    sys_info.cc \
    sys_info_linux.cc \
    sys_info_posix.cc \
    system_monitor/system_monitor.cc \
    task/cancelable_task_tracker.cc \
    task_runner.cc \
    third_party/dmg_fp/dtoa_wrapper.cc \
    third_party/dmg_fp/g_fmt.cc \
    third_party/icu/icu_utf.cc \
    third_party/nspr/prtime.cc \
    third_party/superfasthash/superfasthash.c \
    thread_task_runner_handle.cc \
    threading/non_thread_safe_impl.cc \
    threading/platform_thread_internal_posix.cc \
    threading/platform_thread_linux.cc \
    threading/platform_thread_posix.cc \
    threading/post_task_and_reply_impl.cc \
    threading/sequenced_task_runner_handle.cc \
    threading/sequenced_worker_pool.cc \
    threading/simple_thread.cc \
    threading/thread.cc \
    threading/thread_checker_impl.cc \
    threading/thread_collision_warner.cc \
    threading/thread_id_name_manager.cc \
    threading/thread_local_posix.cc \
    threading/thread_local_storage.cc \
    threading/thread_local_storage_posix.cc \
    threading/thread_restrictions.cc \
    threading/watchdog.cc \
    threading/worker_pool.cc \
    threading/worker_pool_posix.cc \
    time/clock.cc \
    time/default_clock.cc \
    time/default_tick_clock.cc \
    time/tick_clock.cc \
    time/time.cc \
    time/time_posix.cc \
    timer/elapsed_timer.cc \
    timer/hi_res_timer_manager_posix.cc \
    timer/mock_timer.cc \
    timer/timer.cc \
    tracked_objects.cc \
    tracking_info.cc \
    value_conversions.cc \
    values.cc \
    version.cc \
    vlog.cc \
    trace_event/heap_profiler_allocation_context.cc \
    trace_event/heap_profiler_allocation_context_tracker.cc \
    trace_event/heap_profiler_allocation_register.cc \
    trace_event/heap_profiler_allocation_register_posix.cc \
    trace_event/heap_profiler_heap_dump_writer.cc \
    trace_event/heap_profiler_stack_frame_deduplicator.cc \
    trace_event/heap_profiler_type_name_deduplicator.cc \
    trace_event/memory_allocator_dump.cc \
    trace_event/memory_allocator_dump_guid.cc \
    trace_event/memory_dump_manager.cc \
    trace_event/memory_dump_request_args.cc \
    trace_event/memory_dump_session_state.cc \
    trace_event/process_memory_dump.cc \
    trace_event/process_memory_maps.cc \
    trace_event/process_memory_maps_dump_provider.cc \
    trace_event/process_memory_totals.cc \
    trace_event/process_memory_totals_dump_provider.cc \
    trace_event/trace_buffer.cc \
    trace_event/trace_config.cc \
    trace_event/trace_event_argument.cc \
    trace_event/trace_event_impl.cc \
    trace_event/trace_event_memory_overhead.cc \
    trace_event/trace_event_synthetic_delay.cc \
    trace_event/trace_event_system_stats_monitor.cc \
    trace_event/trace_log.cc \
    trace_event/trace_log_constants.cc \
    trace_event/trace_sampling_thread.cc \
    trace_event/tracing_agent.cc \
    trace_event/malloc_dump_provider.cc \
    sha1_portable.cc \
    net/escape.cc

HEADERS += \
    linux_util.h \
    message_loop/message_pump_glib.h \
    message_loop/message_pump_libevent.h \
    metrics/field_trial.h \
    posix/file_descriptor_shuffle.h \
    sync_socket.h \
    third_party/xdg_user_dirs/xdg_user_dir_lookup.h \
    allocator/allocator_check.h \
    allocator/allocator_extension.h \
    at_exit.h \
    barrier_closure.h \
    base64.h \
    base64url.h \
    base_export.h \
    base_paths.h \
    base_paths_posix.h \
    big_endian.h \
    bind.h \
    bind_helpers.h \
    bind_internal.h \
    build_time.h \
    callback.h \
    callback_forward.h \
    callback_helpers.h \
    callback_internal.h \
    callback_list.h \
    cancelable_callback.h \
    command_line.h \
    compiler_specific.h \
    cpu.h \
    containers/adapters.h \
    containers/hash_tables.h \
    containers/linked_list.h \
    containers/mru_cache.h \
    containers/scoped_ptr_hash_map.h \
    containers/small_map.h \
    containers/stack_container.h \
    debug/alias.h \
    debug/asan_invalid_access.h \
    debug/crash_logging.h \
    debug/debugger.h \
    debug/debugging_flags.h \
    debug/dump_without_crashing.h \
    debug/proc_maps_linux.h \
    debug/profiler.h \
    debug/stack_trace.h \
    debug/task_annotator.h \
    deferred_sequenced_task_runner.h \
    environment.h \
    feature_list.h \
    files/file.h \
    files/file_enumerator.h \
    files/file_path.h \
    files/file_path_watcher.h \
    files/file_proxy.h \
    files/file_tracing.h \
    files/file_util.h \
    files/file_util_proxy.h \
    files/important_file_writer.h \
    files/memory_mapped_file.h \
    files/scoped_file.h \
    files/scoped_temp_dir.h \
    guid.h \
    hash.h \
    json/json_file_value_serializer.h \
    json/json_parser.h \
    json/json_reader.h \
    json/json_string_value_serializer.h \
    json/json_value_converter.h \
    json/json_writer.h \
    json/string_escape.h \
    lazy_instance.h \
    location.h \
    logging.h \
    macros.h \
    md5.h \
    memory/aligned_memory.h \
    memory/discardable_memory.h \
    memory/discardable_memory_allocator.h \
    memory/discardable_shared_memory.h \
    memory/memory_pressure_listener.h \
    memory/memory_pressure_monitor.h \
    memory/ref_counted.h \
    memory/ref_counted_memory.h \
    memory/singleton.h \
    memory/scoped_policy.h \
    memory/scoped_ptr.h \
    memory/scoped_vector.h \
    memory/shared_memory.h \
    memory/weak_ptr.h \
    message_loop/incoming_task_queue.h \
    message_loop/message_loop.h \
    message_loop/message_loop_task_runner.h \
    message_loop/message_pump.h \
    message_loop/message_pump_default.h \
    metrics/bucket_ranges.h \
    metrics/histogram.h \
    metrics/histogram_base.h \
    metrics/histogram_delta_serialization.h \
    metrics/histogram_samples.h \
    metrics/histogram_snapshot_manager.h \
    metrics/metrics_hashes.h \
    metrics/persistent_memory_allocator.h \
    metrics/sample_map.h \
    metrics/sample_vector.h \
    metrics/sparse_histogram.h \
    metrics/statistics_recorder.h \
    metrics/user_metrics.h \
    native_library.h \
    nix/mime_util_xdg.h \
    nix/xdg_util.h \
    path_service.h \
    pending_task.h \
    pickle.h \
    posix/global_descriptors.h \
    posix/safe_strerror.h \
    posix/unix_domain_socket_linux.h \
    power_monitor/power_monitor.h \
    power_monitor/power_monitor_device_source.h \
    power_monitor/power_monitor_source.h \
    process/internal_linux.h \
    process/kill.h \
    process/launch.h \
    process/memory.h \
    process/process.h \
    process/process_handle.h \
    process/process_iterator.h \
    process/process_metrics.h \
    profiler/alternate_timer.h \
    profiler/native_stack_sampler.h \
    profiler/scoped_profile.h \
    profiler/scoped_tracker.h \
    profiler/stack_sampling_profiler.h \
    profiler/tracked_time.h \
    rand_util.h \
    run_loop.h \
    scoped_native_library.h \
    sequence_checker.h \
    sequence_checker_impl.h \
    sequenced_task_runner.h \
    strings/latin1_string_conversions.h \
    strings/nullable_string16.h \
    strings/pattern.h \
    strings/safe_sprintf.h \
    strings/string16.h \
    strings/string_number_conversions.h \
    strings/string_piece.h \
    strings/stringprintf.h \
    strings/string_split.h \
    strings/string_tokenizer.h \
    strings/string_util.h \
    strings/string_util_posix.h \
    strings/utf_offset_string_conversions.h \
    strings/utf_string_conversions.h \
    strings/utf_string_conversion_utils.h \
    supports_user_data.h \
    synchronization/cancellation_flag.h \
    synchronization/condition_variable.h \
    synchronization/lock.h \
    synchronization/lock_impl.h \
    synchronization/waitable_event.h \
    synchronization/waitable_event_watcher.h \
    sys_info.h \
    system_monitor/system_monitor.h \
    task/cancelable_task_tracker.h \
    task_runner.h \
    third_party/icu/icu_utf.h \
    third_party/nspr/prtime.h \
    thread_task_runner_handle.h \
    threading/non_thread_safe.h \
    threading/non_thread_safe_impl.h \
    threading/platform_thread.h \
    threading/platform_thread_internal_posix.h \
    threading/post_task_and_reply_impl.h \
    threading/sequenced_task_runner_handle.h \
    threading/sequenced_worker_pool.h \
    threading/simple_thread.h \
    threading/thread.h \
    threading/thread_checker.h \
    threading/thread_checker_impl.h \
    threading/thread_collision_warner.h \
    threading/thread_id_name_manager.h \
    threading/thread_local.h \
    threading/thread_local_storage.h \
    threading/thread_restrictions.h \
    threading/watchdog.h \
    threading/worker_pool.h \
    threading/worker_pool_posix.h \
    time/clock.h \
    time/default_clock.h \
    time/default_tick_clock.h \
    time/tick_clock.h \
    time/time.h \
    timer/elapsed_timer.h \
    timer/hi_res_timer_manager.h \
    timer/mock_timer.h \
    timer/timer.h \
    tracked_objects.h \
    tracking_info.h \
    value_conversions.h \
    values.h \
    version.h \
    vlog.h \
    trace_event/heap_profiler_allocation_context.h \
    trace_event/heap_profiler_allocation_context_tracker.h \
    trace_event/heap_profiler_allocation_register.h \
    trace_event/heap_profiler_heap_dump_writer.h \
    trace_event/heap_profiler_stack_frame_deduplicator.h \
    trace_event/heap_profiler_type_name_deduplicator.h \
    trace_event/memory_allocator_dump.h \
    trace_event/memory_allocator_dump_guid.h \
    trace_event/memory_dump_manager.h \
    trace_event/memory_dump_request_args.h \
    trace_event/memory_dump_session_state.h \
    trace_event/process_memory_dump.h \
    trace_event/process_memory_maps.h \
    trace_event/process_memory_maps_dump_provider.h \
    trace_event/process_memory_totals.h \
    trace_event/process_memory_totals_dump_provider.h \
    trace_event/trace_buffer.h \
    trace_event/trace_config.h \
    trace_event/trace_event_argument.h \
    trace_event/trace_event_impl.h \
    trace_event/trace_event_memory_overhead.h \
    trace_event/trace_event_synthetic_delay.h \
    trace_event/trace_event_system_stats_monitor.h \
    trace_event/trace_log.h \
    trace_event/trace_sampling_thread.h \
    trace_event/tracing_agent.h \
    trace_event/malloc_dump_provider.h \
    net/escape.h \
    bind_to_current_loop.h

unix {
    target.path = /usr/lib
    INSTALLS += target
}
