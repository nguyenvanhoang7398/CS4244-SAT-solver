#!/bin/sh

contains_element() {
    local e
    for e in "${@:2}"; do [[ "$e" == "$1" ]] && return 0; done
    return 1
}

function format_output () {
    echo "${output_dir}/output-$1-$2"
}

config_file="sat_solver.conf"
. ${config_file}

rm ${result_path}
touch ${result_path}
rm -rf ${output_dir}
mkdir ${output_dir}

outputs=()

for solver in "${solvers[@]}"
do
    echo "${solver}"
    `contains_element "${solver}" "${applied_solvers[@]}"`
    rc=$?
    if [ ${rc} -eq 0 ]; then
        for heuristic in "${heuristics[@]}"
        do
            echo ${heuristic}
            output_path=`format_output ${solver} ${heuristic}`
            rm -rf ${output_path}
            mkdir ${output_path}
            python sat_solver.py --solver ${solver-name} \
            cdcl --log-level ${log_level} --input ${input_path} \
            --branching-heuristic ${heuristic} --output ${output_path} \
            --result ${result_path}
            outputs+=('${output_path}')
        done
    fi
    output_path=`format_output ${solver} ""`
    rm -rf ${output_path}
    mkdir ${output_path}
    python sat_solver.py --solver ${solver-name} \
    cdcl --log-level ${log_level} --input ${input_path} \
    --output ${output_path} --result ${result_path}
done