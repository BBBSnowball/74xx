
foreach (_tbb_component "tbb tbbmalloc tbbmalloc_proxy")
    set(_tbb_release_lib "/nix/store/m41mc9jycigmv86r0g2vs228pq3xgj7d-tbb-2020.3/lib/lib${_tbb_component}.so")
    #set(_tbb_debug_lib "/nix/store/m41mc9jycigmv86r0g2vs228pq3xgj7d-tbb-2020.3/lib/lib${_tbb_component}_debug.so")

    if (EXISTS "${_tbb_release_lib}" AND EXISTS "${_tbb_debug_lib}")
        add_library(TBB::${_tbb_component} SHARED IMPORTED)
        set_target_properties(TBB::${_tbb_component} PROPERTIES
                              IMPORTED_CONFIGURATIONS "RELEASE;DEBUG"
                              IMPORTED_LOCATION_RELEASE     "${_tbb_release_lib}"
                              #IMPORTED_LOCATION_DEBUG       "${_tbb_debug_lib}"
                              INTERFACE_INCLUDE_DIRECTORIES "/nix/store/l7vm3gw7y70ssfw3373whjhs1mj3bxyq-tbb-2020.3-dev/include")

        # Add internal dependencies for imported targets: TBB::tbbmalloc_proxy -> TBB::tbbmalloc
        if (_tbb_component STREQUAL tbbmalloc_proxy)
            set_target_properties(TBB::tbbmalloc_proxy PROPERTIES INTERFACE_LINK_LIBRARIES TBB::tbbmalloc)
        endif()

        list(APPEND TBB_IMPORTED_TARGETS TBB::${_tbb_component})
        set(TBB_${_tbb_component}_FOUND 1)
    elseif (TBB_FIND_REQUIRED AND TBB_FIND_REQUIRED_${_tbb_component})
        message(FATAL_ERROR "Missed required Intel TBB component: ${_tbb_component}")
    endif()
endforeach()
