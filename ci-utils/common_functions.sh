#!/bin/bash

function s_info() {
    echo -e "INFO: $1"
}

function s_err() {
    echo -e "ERROR: $1"
}

function iterate_over_lines() {
    while read -r line; do
        s_info "\t $line"
    done <<< "$1"
}