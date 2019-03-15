#!/bin/sh

function contains_element {
  local e match="$1"
  shift
  for e; do [[ "$e" == "$match" ]] && echo "true"; done
  echo "false"
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
    `contains_element "${solver}" "${applied_solvers[@]}"`
    rc=$?
    if [ ${rc} -eq 0 ]; then
        for heuristic in "${heuristics[@]}"
        do
            echo ${heuristic}
            output_path=`format_output ${solver} ${heuristic}`
            rm -rf ${output_path}
            mkdir ${output_path}
            _execution_start_time=$SECONDS
            python sat_solver.py --solver ${solver-name} \
            cdcl --log-level ${log_level} --input ${input_path} \
            --branching-heuristic ${heuristic} --output ${output_path}
            _elapsed=$(($SECONDS - ${_execution_start_time}))
            echo "${output_path} ${_elapsed}" >> ${result_path}
            outputs+=('${output_path}')
        done
    fi
    output_path=`format_output ${solver} ""`
    rm -rf ${output_path}
    mkdir ${output_path}
    _execution_start_time=$SECONDS
    python sat_solver.py --solver ${solver-name} \
    cdcl --log-level ${log_level} --input ${input_path} \
    --output ${output_path}
    _elapsed=$(($SECONDS - ${_execution_start_time}))
    echo "${output_path} ${_elapsed}" >> ${result_path}
done