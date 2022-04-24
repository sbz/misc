#!/usr/bin/env bash

set -o errexit
set -o nounset

#
# Renice sub processes of the given <pid> with the given <value>
#
# Usage: reniceall.sh <pid> <value>
#

get_all_childs() {
    local pid="$1"
    declare -a childs

    childs=($(pgrep -P "${pid}"))
    for child in ${childs[*]}; do
        if [[ -z "${child}" ]]; then
            exit $?
        else
            echo -n "${child} "
            get_all_childs "${child}"
        fi
    done
}

if (( $# != 2 )); then
    echo "Usage: ${0} <pid> <value>" >&2
    exit 2
fi

if (( ${2/#-} > 20 )); then
    PRIO_MIN=-20
    PRIO_MAX=20
    echo "Cannot nice using $2 (${PRIO_MIN} > value > ${PRIO_MAX})" >&2
    exit 1
fi

declare -a all_pids

all_pids=($(get_all_childs "${1}"))
for pid in ${all_pids[*]}; do
    renice "${2}" -p "${pid}"
done

exit 0
